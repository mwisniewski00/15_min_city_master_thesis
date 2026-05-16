from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import osmnx
from matplotlib.lines import Line2D

from fmc_core import GRAPHS, GRAPHS_DIR, load_graph


_ALGORITHMS = ("modified", "regular")

# Colour scheme: green = in C(t), red = not in C(t).
_COLOR_IN = "#2ca02c"
_COLOR_OUT = "#d62728"


def visualize(graph_key: str, algorithm: str) -> Path:
    graphml_path = GRAPHS_DIR / GRAPHS[graph_key]
    json_path = GRAPHS_DIR / f"{graph_key}_15mc_{algorithm}.json"
    if not graphml_path.is_file():
        raise SystemExit(f"Graph file not found: {graphml_path}")
    if not json_path.is_file():
        raise SystemExit(
            f"Result JSON not found: {json_path}\n"
            f"Run: python fifteen_min_city.py {graph_key} -a {algorithm}"
        )

    print(f"[load] {graphml_path}")
    graph = load_graph(graphml_path)
    print(f"[load] {json_path}")
    payload = json.loads(json_path.read_text())

    in_set = set(payload["intersection"])
    threshold = payload["threshold_minutes"]
    n_nodes = graph.number_of_nodes()
    n_edges = graph.number_of_edges()
    n_in = len(in_set)
    pct_in_nodes = n_in / n_nodes * 100.0 if n_nodes else 0.0

    edge_colors = [
        _COLOR_IN if (u in in_set and v in in_set) else _COLOR_OUT
        for u, v, _ in graph.edges(keys=True)
    ]
    n_in_edges = sum(1 for c in edge_colors if c == _COLOR_IN)
    n_out_edges = n_edges - n_in_edges
    pct_in_edges = n_in_edges / n_edges * 100.0 if n_edges else 0.0

    print(f"[plot] {n_nodes} nodes, {n_edges} edges...")
    fig, ax = osmnx.plot.plot_graph(
        graph,
        bgcolor="#ffffff",
        node_size=0,
        edge_color=edge_colors,
        edge_linewidth=0.5,
        edge_alpha=0.9,
        show=False,
        close=False,
        figsize=(12, 12),
    )

    ax.set_title(
        f"{graph_key} — 15-minute city  "
        f"(algorithm: {algorithm}, t = {threshold:g} min)\n"
        f"|C(t)| = {n_in:,} / {n_nodes:,} nodes  ({pct_in_nodes:.1f}%)",
        fontsize=13,
    )

    legend_handles = [
        Line2D(
            [0], [0],
            color=_COLOR_IN, linewidth=3,
            label=f"served  ({n_in_edges:,} edges, {pct_in_edges:.1f}%)",
        ),
        Line2D(
            [0], [0],
            color=_COLOR_OUT, linewidth=3,
            label=f"underserved  ({n_out_edges:,} edges, {100 - pct_in_edges:.1f}%)",
        ),
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower right",
        frameon=True,
        framealpha=0.9,
        fontsize=10,
    )

    out_path = GRAPHS_DIR / f"{graph_key}_15mc_{algorithm}.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[done] wrote {out_path}")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a node-level map of 15-minute-city results.",
    )
    parser.add_argument(
        "graph",
        choices=list(GRAPHS),
        help="Which graph to visualize.",
    )
    parser.add_argument(
        "-a", "--algorithm",
        choices=_ALGORITHMS,
        default="modified",
        help="Which algorithm's results to use (default: modified).",
    )
    args = parser.parse_args(argv)
    visualize(args.graph, args.algorithm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
