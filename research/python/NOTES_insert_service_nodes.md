# Notes on `insert_service_nodes.py` — design decisions

## What the script does

Inserts service-location nodes (Points of Interest from a GeoPackage) into a
projected walk graph by splitting the nearest edge at the foot of the
perpendicular from each POI.  The result is a graph that can be used directly
for shortest-path / isochrone analysis where every service is reachable from
any street node.

## Relation to other scripts

| Script | Role |
|---|---|
| `extract_graph.py` | Builds and projects the walk graph (EPSG:3035) |
| `extract_services.py` | Fetches OSM POIs and writes them as centroid points into `.gpkg` layers |
| `insert_service_nodes.py` | Splits graph edges at POI projections; imports helpers from `extract_graph.py` |

## Algorithm — `insert_service_node`

1. **Nearest edge** — `osmnx.distance.nearest_edges` returns the single closest
   `(u, v, key)` triple in the undirected graph.
2. **Edge geometry** — an explicit `if 'geometry' in edge_data` check is used to
   retrieve the stored `LineString` (curved edges) or reconstruct a two-point
   straight line from node coordinates (straight edges).
3. **Projection** — `shapely.ops.nearest_points(edge_geom, service_point)`
   returns the foot of the perpendicular on the edge.
4. **Split** — the edge's coordinate sequence is walked to find which sub-segment
   contains the projected point; prefix and suffix coordinate lists are built
   into two new `LineString` geometries.  A guard prevents degenerate
   single-point lines when the projection falls exactly on an existing vertex.
5. **Graph update** — the original edge is removed; two replacement edges
   (u → new\_node, new\_node → v) are added with the split geometries, their
   `length` set to `geometry.length`, and `weight` set to
   `length / WALKING_SPEED_IN_METERS_PER_MINUTE`.  All other edge attributes
   (e.g. `osmid`, `highway`) are copied unchanged.
6. **Node ID** — `max(graph.nodes()) + 1` guarantees a unique integer that does
   not collide with OSM node IDs (which are large positive integers).

## Bugs fixed relative to the thesis implementation

### Bug 1 — `try/except` always fires

The thesis wrapped the geometry block in a `try/except AttributeError`.
`edge_geom.coords[0]` returns a plain Python tuple, which has no `.distance()`
method, so the `except` branch fired unconditionally — even when the edge had a
real curved `LineString` stored in `edge_data['geometry']`.  The curved
geometry was silently discarded and replaced by a straight two-point line every
time.

**Fix:** replace the `try/except` with an explicit `if 'geometry' in edge_data`
check.

### Bug 2 — spurious `* 111320` multiplier

In the thesis's `except` branch, the straight-line distance was multiplied by
111 320 (metres per degree of latitude) before being used as edge weight.
Because the graph is already in **EPSG:3035** (a metric CRS),
`Point.distance()` already returns metres, so the multiplier inflated
`edge_weight_linear` by a factor of ~111 320.  This corrupted the
`ratio_segment_1` calculation and the `length` values stored on the new split
edges.

The thesis did not surface this bug because Cell 13 recomputes all edge weights
from `geometry.length` before running Dijkstra, so the wrong `length` values
are never actually used for routing.

**Fix:** remove the `* 111320` multiplier entirely.  In this implementation the
multiplier is additionally unnecessary because edge lengths are derived directly
from `geom_seg1.length` / `geom_seg2.length` rather than from a ratio of linear
distances.

## Driver — `insert_services_from_gpkg`

Iterates every layer in a GeoPackage file with `pyogrio.list_layers` (used in
place of `fiona.listlayers` because `fiona` is not installed in the project
virtualenv; `geopandas` 1.x uses `pyogrio` as its default I/O backend).  Each
layer is read into a `GeoDataFrame` and `insert_service_node` is called for
every row.

After all insertions a weight-recomputation pass updates `weight` for every
edge in the graph from its `geometry.length` (or `length` for edges that have
no geometry attribute).  This mirrors the thesis's Cell 13 and ensures that
edges added by earlier insertion calls also get correct weights before Dijkstra
is run.

Returns `(graph, inserted)` where `inserted` is a `dict` mapping each category
name to the list of new node IDs created for it.

## Shared constants and helpers in `extract_graph.py`

To eliminate duplication, the following were added to `extract_graph.py` and
imported from there:

- `GDANSK_POLUDNIE_SUB_DISTRICTS` — the four sub-district name strings used
  both here and in `extract_services.py`.
- `build_gdansk_poludnie_graph()` — encapsulates the geocode → `unary_union` →
  `graph_from_polygon` → `process_graph` sequence that previously appeared as
  commented-out boilerplate in `extract_graph.py` and as live code in the
  `__main__` block here.

## Running the smoke test

```bash
cd research/python
.venv/bin/python insert_service_nodes.py
```

The `__main__` block:
1. Builds the Gdańsk Południe walk graph from OSM (requires internet access;
   results are cached by `osmnx` on subsequent runs).
2. Prints node and edge counts before insertion.
3. Calls `insert_services_from_gpkg` with `services_gdansk_poludnie.gpkg`.
4. Prints node and edge counts after insertion, plus the net change.

Expected output shape:

```
Building Gdańsk Południe walk graph…
Before insertion — nodes: 5159, edges: 11745
Inserting services from services_gdansk_poludnie.gpkg…
  [education] inserted N service nodes
  ...
After insertion  — nodes: XXXX, edges: YYYY
Service nodes added: N (+N net nodes, +N net edges)
```
