from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from collections import defaultdict
from contextlib import nullcontext
from pathlib import Path
from typing import Callable, Dict, Hashable, Iterable, List, Tuple

import networkx as nx
import osmnx


INF = math.inf


GRAPHS: dict[str, str] = {
    "gdansk_poludnie": "gdansk_poludnie_walk_services.graphml",
    "gdansk":          "gdansk_walk_services.graphml",
    "london":          "london_walk_services.graphml",
}

GRAPHS_DIR = Path(__file__).resolve().parent / "graphs"

BENCHMARK_RUNS = 100

BENCHMARK_WARMUP_RUNS = 3

CategorySolver = Callable[["IndexedGraph", float], set]


def load_graph(graphml_path: Path) -> nx.MultiGraph:
    return osmnx.io.load_graphml(
        graphml_path,
        edge_dtypes={"weight": float, "length": float},
    )


def services_by_category(graph: nx.Graph) -> dict[str, list]:
    by_cat: dict[str, list] = defaultdict(list)
    for node, data in graph.nodes(data=True):
        cat = data.get("service_category")
        if cat:
            by_cat[cat].append(node)
    return dict(by_cat)

class IndexedGraph:
    __slots__ = (
        "adj", "index", "nodes", "super_idx", "min_edge_weight", "__weakref__",
    )

    def __init__(self, graph: nx.MultiGraph, service_nodes: Iterable) -> None:
        nodes: List[Hashable] = list(graph.nodes)
        index: Dict[Hashable, int] = {u: i for i, u in enumerate(nodes)}
        n = len(nodes)
        adj: List[List[Tuple[int, float]]] = [[] for _ in range(n + 1)]
        min_w = INF
        for u in nodes:
            ui = index[u]
            bucket = adj[ui]
            for v, parallel in graph[u].items():
                w = min(
                    (e.get("weight", INF) for e in parallel.values()),
                    default=INF,
                )
                bucket.append((index[v], w))
                if 0.0 < w < min_w:
                    min_w = w
        adj[n] = [(index[s], 0.0) for s in service_nodes if s in index]
        self.adj = adj
        self.index = index
        self.nodes = nodes
        self.super_idx = n
        self.min_edge_weight = float(min_w) if math.isfinite(min_w) else 1.0


def run_per_category(
    indexed_by_cat: dict[str, IndexedGraph],
    threshold: float,
    solver: CategorySolver,
    *,
    verbose: bool = True,
) -> tuple[dict[str, set], set, dict[str, float]]:
    if not indexed_by_cat:
        raise ValueError(
            "No service categories provided (graph has no "
            "`service_category` attributes?)."
        )

    per_category: dict[str, set] = {}
    timings: dict[str, float] = {}
    for cat in sorted(indexed_by_cat):
        indexed = indexed_by_cat[cat]
        t0 = time.perf_counter()
        reached = solver(indexed, threshold)
        timings[cat] = time.perf_counter() - t0
        per_category[cat] = reached
        if verbose:
            n_services = len(indexed.adj[indexed.super_idx])
            print(
                f"  [{cat:<13}] services={n_services:>5}  "
                f"|C_k(t)|={len(reached):>6}  "
                f"({timings[cat]:.2f}s)"
            )

    intersection = (
        set.intersection(*per_category.values()) if per_category else set()
    )
    return per_category, intersection, timings


def _to_jsonable(node):
    if isinstance(node, (int, str, float, bool)) or node is None:
        return node
    return str(node)


def _summarize(values: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.mean(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def write_results(
    out_path: Path,
    *,
    graph_key: str,
    algorithm: str,
    threshold: float,
    n_nodes: int,
    n_edges: int,
    per_category: dict[str, set],
    intersection: set,
    timings: dict[str, float],
    runs_seconds: list[float],
) -> None:
    stats = _summarize(runs_seconds)
    payload = {
        "graph": graph_key,
        "algorithm": algorithm,
        "threshold_minutes": threshold,
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "per_category_counts": {k: len(v) for k, v in per_category.items()},
        "per_category_timings_seconds_last_run": timings,
        "intersection_count": len(intersection),
        "runs_seconds": runs_seconds,
        "mean_seconds": stats["mean"],
        "stdev_seconds": stats["stdev"],
        "min_seconds": stats["min"],
        "max_seconds": stats["max"],
        "per_category": {
            k: [_to_jsonable(n) for n in sorted(v)]
            for k, v in per_category.items()
        },
        "intersection": [_to_jsonable(n) for n in sorted(intersection)],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))


def build_arg_parser(
    *,
    prog: str | None = None,
    description: str | None = None,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute the 15-minute-city node set in a walk+services graph.",
    )
    parser.add_argument(
        "graph",
        choices=list(GRAPHS),
        help="Which graph to analyse.",
    )
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=15.0,
        help="Time threshold in minutes (default: 15).",
    )
    parser.add_argument(
        "-p", "--parallel",
        action="store_true",
        help=(
            "Run the per-category SSSPs in parallel across worker"
        ),
    )
    return parser


def run(
    args: argparse.Namespace,
    *,
    algorithm: str,
    solver: CategorySolver,
) -> int:
    graphml_path = GRAPHS_DIR / GRAPHS[args.graph]
    if not graphml_path.is_file():
        raise SystemExit(f"Graph file not found: {graphml_path}")

    print(f"[load] {graphml_path}")
    t0 = time.perf_counter()
    graph = load_graph(graphml_path)
    print(
        f"[load] nodes={graph.number_of_nodes()} "
        f"edges={graph.number_of_edges()} "
        f"({time.perf_counter() - t0:.2f}s)"
    )

    by_cat = services_by_category(graph)
    if not by_cat:
        raise SystemExit(
            "Graph has no service nodes (no `service_category` attributes)."
        )
    t0 = time.perf_counter()
    indexed_by_cat: dict[str, IndexedGraph] = {
        cat: IndexedGraph(graph, services) for cat, services in by_cat.items()
    }
    print(
        f"[prep] built IndexedGraph for {len(indexed_by_cat)} categories "
        f"({time.perf_counter() - t0:.2f}s; excluded from per-iteration timing)"
    )

    parallel = bool(getattr(args, "parallel", False))
    if parallel:
        from fmc_parallel_categories import ParallelCategoryRunner
        runner_cm = ParallelCategoryRunner(
            indexed_by_cat, solver, workers=len(indexed_by_cat),
        )
        algorithm_tag = f"{algorithm}_parallel"
    else:
        runner_cm = nullcontext(None)
        algorithm_tag = algorithm

    warmup_runs = BENCHMARK_WARMUP_RUNS if parallel else 0
    print(
        f"[run]  algorithm = {algorithm_tag}, threshold = {args.threshold} min, "
        f"runs = {BENCHMARK_RUNS}"
        + (f" (+ {warmup_runs} warmup)" if warmup_runs else "")
    )

    runs_seconds: list[float] = []
    per_cat: dict[str, set] = {}
    intersection: set = set()
    timings: dict[str, float] = {}

    with runner_cm as parallel_runner:
        if parallel_runner is not None:
            for w in range(warmup_runs):
                tw = time.perf_counter()
                parallel_runner.run(args.threshold, verbose=False)
                print(
                    f"  [warmup {w + 1:>2}/{warmup_runs}] "
                    f"{time.perf_counter() - tw:.3f}s (discarded)"
                )

        for i in range(BENCHMARK_RUNS):
            t1 = time.perf_counter()
            if parallel_runner is None:
                per_cat, intersection, timings = run_per_category(
                    indexed_by_cat, args.threshold, solver, verbose=(i == 0),
                )
            else:
                per_cat, intersection, timings = parallel_runner.run(
                    args.threshold, verbose=(i == 0),
                )
            runs_seconds.append(time.perf_counter() - t1)
            print(f"  [iter {i + 1:>2}/{BENCHMARK_RUNS}] {runs_seconds[-1]:.3f}s")

    n_nodes = graph.number_of_nodes()
    pct = (len(intersection) / n_nodes * 100.0) if n_nodes else 0.0
    s = _summarize(runs_seconds)
    print(
        f"[done] solver time over {BENCHMARK_RUNS} runs: "
        f"mean={s['mean']:.3f}s ± {s['stdev']:.3f}s  "
        f"min={s['min']:.3f}s  max={s['max']:.3f}s"
    )
    print(f"[done] |C(t)| = {len(intersection)} / {n_nodes} nodes ({pct:.1f}%)")

    out = GRAPHS_DIR / f"{args.graph}_15mc_{algorithm_tag}.json"
    write_results(
        out,
        graph_key=args.graph,
        algorithm=algorithm_tag,
        threshold=args.threshold,
        n_nodes=n_nodes,
        n_edges=graph.number_of_edges(),
        per_category=per_cat,
        intersection=intersection,
        timings=timings,
        runs_seconds=runs_seconds,
    )
    print(f"[done] wrote {out}")
    return 0
