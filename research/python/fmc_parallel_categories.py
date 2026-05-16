from __future__ import annotations

import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, Tuple

from fmc_core import CategorySolver, IndexedGraph

_WORKER_INDEXED: dict = {}
_WORKER_SOLVER: Optional[CategorySolver] = None


def _init_worker(
    indexed_by_cat: "dict[str, IndexedGraph]",
    solver: CategorySolver,
) -> None:
    global _WORKER_INDEXED, _WORKER_SOLVER
    _WORKER_INDEXED = indexed_by_cat
    _WORKER_SOLVER = solver


def _run_one(task: Tuple[str, float]) -> Tuple[str, set, float]:
    cat, threshold = task
    indexed = _WORKER_INDEXED[cat]
    solver = _WORKER_SOLVER
    t0 = time.perf_counter()
    reached = solver(indexed, threshold)
    return cat, reached, time.perf_counter() - t0

def _preferred_start_method() -> str:
    if "fork" in multiprocessing.get_all_start_methods():
        return "fork"
    return multiprocessing.get_start_method()

class ParallelCategoryRunner:
    def __init__(
        self,
        indexed_by_cat: "dict[str, IndexedGraph]",
        solver: CategorySolver,
        *,
        workers: Optional[int] = None,
    ) -> None:
        self.indexed_by_cat = indexed_by_cat
        self.solver = solver
        ncpu = os.cpu_count() or 1
        ncat = max(len(indexed_by_cat), 1)
        requested = ncpu if workers is None else workers
        self.workers = max(1, min(requested, ncpu, ncat))

        self._executor: Optional[ProcessPoolExecutor] = None

    def __enter__(self) -> "ParallelCategoryRunner":
        ctx = multiprocessing.get_context(_preferred_start_method())
        self._executor = ProcessPoolExecutor(
            max_workers=self.workers,
            mp_context=ctx,
            initializer=_init_worker,
            initargs=(self.indexed_by_cat, self.solver),
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None
        return False

    def run(
        self,
        threshold: float,
        *,
        verbose: bool = True,
    ) -> "tuple[dict[str, set], set, dict[str, float]]":
        if self._executor is None:
            raise RuntimeError(
                "ParallelCategoryRunner must be used as a context manager."
            )
        if not self.indexed_by_cat:
            raise ValueError(
                "No service categories provided."
            )

        cats = sorted(self.indexed_by_cat)
        tasks = [(cat, threshold) for cat in cats]

        per_category: "dict[str, set]" = {}
        timings: "dict[str, float]" = {}
        
        for cat, reached, elapsed in self._executor.map(_run_one, tasks):
            per_category[cat] = reached
            timings[cat] = elapsed
            if verbose:
                indexed = self.indexed_by_cat[cat]
                n_services = len(indexed.adj[indexed.super_idx])
                print(
                    f"  [{cat:<13}] services={n_services:>5}  "
                    f"|C_k(t)|={len(reached):>6}  "
                    f"({elapsed:.2f}s)"
                )

        intersection = (
            set.intersection(*per_category.values()) if per_category else set()
        )
        return per_category, intersection, timings
