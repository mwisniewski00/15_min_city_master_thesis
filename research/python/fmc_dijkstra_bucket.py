from __future__ import annotations

from collections import deque
from typing import Deque, List, Optional, Tuple

from fmc_core import INF, IndexedGraph

_DEFAULT_DELTA = 1.0


def _initial_bucket_count(bound: float, delta: float) -> int:
    return int(bound / delta) + 2


class _BucketQueue:
    def __init__(self, delta: float, initial_buckets: int = 1) -> None:
        self.delta = delta
        self.min_idx = 0
        self.max_idx = -1
        self.buckets: List[Deque[Tuple[float, int]]] = [
            deque() for _ in range(initial_buckets)
        ]

    def insert(self, v: int, dist: float) -> None:
        idx = int(dist / self.delta)
        if idx >= len(self.buckets):
            self.buckets.extend(deque() for _ in range(idx - len(self.buckets) + 1))
        self.buckets[idx].append((dist, v))
        if idx > self.max_idx:
            self.max_idx = idx

    def extract_min(self) -> Tuple[float, Optional[int], bool]:
        i = self.min_idx
        max_i = self.max_idx
        buckets = self.buckets
        while i <= max_i:
            if buckets[i]:
                self.min_idx = i
                d, v = buckets[i].popleft()
                return d, v, True
            i += 1
        self.min_idx = i
        return 0.0, None, False


class _BucketDijkstraSolver:
    def __init__(
        self,
        adj: List[List[Tuple[int, float]]],
        delta: float = _DEFAULT_DELTA,
    ) -> None:
        self.adj = adj
        self.n = len(adj)
        self.distances: List[float] = [INF] * self.n
        self.delta = delta

    def solve(self, source: int, bound: float) -> List[float]:
        self.distances[source] = 0.0
        self._solve(source, bound)
        return self.distances

    def _solve(self, source: int, bound: float) -> None:
        n_buckets = _initial_bucket_count(bound, self.delta)
        pq = _BucketQueue(self.delta, initial_buckets=n_buckets)

        distances = self.distances
        adj = self.adj
        d0 = distances[source]
        if d0 <= bound:
            pq.insert(source, d0)

        while True:
            d_at_push, u, ok = pq.extract_min()
            if not ok:
                break
            if d_at_push != distances[u]:
                continue

            du = distances[u]
            if du >= bound:
                continue

            for vi, w in adj[u]:
                nd = du + w
                if nd < distances[vi] and nd <= bound:
                    distances[vi] = nd
                    pq.insert(vi, nd)


def solve_bucket(indexed: IndexedGraph, threshold: float) -> set:
    solver = _BucketDijkstraSolver(indexed.adj)
    src = indexed.super_idx

    dist_arr = solver.solve(src, bound=threshold)
    nodes = indexed.nodes
    return {
        nodes[i]
        for i, d in enumerate(dist_arr)
        if i != src and d <= threshold
    }
