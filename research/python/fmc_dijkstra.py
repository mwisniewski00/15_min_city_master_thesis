from __future__ import annotations

import heapq
import math
from typing import List, Tuple

from fmc_core import INF, IndexedGraph


def _dijkstra_indexed(
    adj: List[List[Tuple[int, float]]],
    source: int,
    *,
    threshold: float = math.inf,
) -> List[float]:
    n = len(adj)
    distances: List[float] = [INF] * n
    distances[source] = 0.0
    heap: list = [(0.0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > threshold:
            break
        if d > distances[u]:
            continue

        for vi, w in adj[u]:
            nd = d + w
            if nd > threshold:
                continue
            if nd < distances[vi]:
                distances[vi] = nd
                heapq.heappush(heap, (nd, vi))

    return distances


def _dijkstra_reachable(
    indexed: IndexedGraph,
    threshold: float,
    *,
    bounded: bool,
) -> set:
    src = indexed.super_idx
    distances = _dijkstra_indexed(
        indexed.adj,
        src,
        threshold=threshold if bounded else math.inf,
    )
    nodes = indexed.nodes
    return {
        nodes[i]
        for i, d in enumerate(distances)
        if i != src and d <= threshold
    }


def solve_regular(indexed: IndexedGraph, threshold: float) -> set:
    return _dijkstra_reachable(indexed, threshold, bounded=False)


def solve_modified(indexed: IndexedGraph, threshold: float) -> set:
    return _dijkstra_reachable(indexed, threshold, bounded=True)
