from collections import defaultdict
from pathlib import Path

import numpy as np
import osmnx
import geopandas as gpd
import pyogrio
from shapely.geometry import Point, LineString
from shapely.ops import substring

from extract_graph import (
    WALKING_SPEED_IN_METERS_PER_MINUTE,
    build_gdansk_graph,
    build_gdansk_poludnie_graph,
    build_london_graph,
)

_SCRIPT_DIR = Path(__file__).resolve().parent
_DEFAULT_GRAPHS_DIR = _SCRIPT_DIR / "graphs"

# Plot: street vs service nodes (light grey vs accent)
_STREET_NODE_COLOR = "#9e9e9e"
_SERVICE_NODE_COLOR = "#d62728"


def _coords_to_linestring(coords):
    seq = list(coords)
    if not seq:
        raise ValueError("LineString requires at least one coordinate")
    if len(seq) == 1:
        seq = [seq[0], seq[0]]
    return LineString(seq)


def _edge_geometry(graph, u, v, edge_data):
    if 'geometry' in edge_data:
        return edge_data['geometry']
    return LineString([
        (graph.nodes[u]['x'], graph.nodes[u]['y']),
        (graph.nodes[v]['x'], graph.nodes[v]['y']),
    ])


def _safe_substring(edge_geom, start_dist, end_dist, fallback_xy):
    if abs(end_dist - start_dist) < 1e-12:
        return _coords_to_linestring([fallback_xy])
    seg = substring(edge_geom, start_dist, end_dist)
    if seg.is_empty or seg.geom_type == 'Point':
        return _coords_to_linestring([fallback_xy])
    return seg


def insert_services_from_gpkg(graph, gpkg_path):
    layers = [row[0] for row in pyogrio.list_layers(gpkg_path)]

    all_services = []
    for category in layers:
        gdf = gpd.read_file(gpkg_path, layer=category)
        for row in gdf.itertuples(index=False):
            all_services.append((category, row.geometry.x, row.geometry.y))

    if not all_services:
        return graph, {}

    xs = np.array([s[1] for s in all_services])
    ys = np.array([s[2] for s in all_services])

    ne = osmnx.distance.nearest_edges(graph, xs, ys)

    edge_groups = defaultdict(list)
    for i, (cat, x, y) in enumerate(all_services):
        edge_key = tuple(int(c) for c in ne[i])
        edge_groups[edge_key].append((cat, x, y))

    next_id = max(graph.nodes()) + 1
    inserted = defaultdict(list)

    for (u, v, k), services in edge_groups.items():
        edge_data = graph.edges[u, v, k]
        edge_geom = _edge_geometry(graph, u, v, edge_data)
        total_length = edge_geom.length

        projections = []
        for cat, sx, sy in services:
            dist = edge_geom.project(Point(sx, sy))
            pp = edge_geom.interpolate(dist)
            projections.append((dist, cat, pp.x, pp.y))
        projections.sort(key=lambda t: t[0])

        base_attrs = {
            k_: v_
            for k_, v_ in edge_data.items()
            if k_ not in ('geometry', 'length', 'weight')
        }
        graph.remove_edge(u, v, k)

        prev_node = u
        prev_dist = 0.0
        for dist, cat, px, py in projections:
            nid = next_id
            next_id += 1
            graph.add_node(nid, x=px, y=py, service_category=cat)
            inserted[cat].append(nid)

            seg = _safe_substring(edge_geom, prev_dist, dist, (px, py))
            seg_len = seg.length
            graph.add_edge(
                prev_node, nid,
                **base_attrs,
                geometry=seg,
                length=seg_len,
                weight=seg_len / WALKING_SPEED_IN_METERS_PER_MINUTE,
            )
            prev_node = nid
            prev_dist = dist

        vx, vy = graph.nodes[v]['x'], graph.nodes[v]['y']
        seg = _safe_substring(edge_geom, prev_dist, total_length, (vx, vy))
        seg_len = seg.length
        graph.add_edge(
            prev_node, v,
            **base_attrs,
            geometry=seg,
            length=seg_len,
            weight=seg_len / WALKING_SPEED_IN_METERS_PER_MINUTE,
        )

    for u, v, k, edge_data in graph.edges(keys=True, data=True):
        edge_data['weight'] = (
            float(edge_data['length']) / WALKING_SPEED_IN_METERS_PER_MINUTE
        )

    result = {}
    for category in layers:
        ids = inserted.get(category, [])
        result[category] = ids
        print(f"  [{category}] inserted {len(ids)} service nodes")

    return graph, result


def save_routed_graph(graph, graphml_path):
    path = Path(graphml_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    osmnx.io.save_graphml(graph, path)


def plot_street_vs_service_nodes(
    graph,
    png_path,
    *,
    figsize=(12, 12),
    dpi=300,
    bgcolor="#ffffff",
    edge_color="#cccccc",
    street_node_color=_STREET_NODE_COLOR,
    service_node_color=_SERVICE_NODE_COLOR,
    node_size_street=8,
    node_size_service=28,
):
    gdf_nodes = osmnx.convert.graph_to_gdfs(
        graph, edges=False, node_geometry=False
    )
    sizes = [
        node_size_service if "service_category" in graph.nodes[n] else node_size_street
        for n in gdf_nodes.index
    ]
    colors = [
        service_node_color if "service_category" in graph.nodes[n] else street_node_color
        for n in gdf_nodes.index
    ]
    path = Path(png_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    osmnx.plot.plot_graph(
        graph,
        bgcolor=bgcolor,
        node_color=colors,
        node_size=sizes,
        node_edgecolor="#333333",
        node_alpha=0.9,
        edge_color=edge_color,
        edge_linewidth=0.4,
        show=False,
        save=True,
        filepath=path,
        dpi=dpi,
        figsize=figsize,
        close=True,
    )


def _build_insert_save(
    label,
    build_graph_fn,
    gpkg_path,
    graphml_name,
    png_name,
    *,
    graphs_dir=_DEFAULT_GRAPHS_DIR,
):
    gpkg_path = Path(gpkg_path)
    graphs_dir = Path(graphs_dir)
    if not gpkg_path.is_file():
        raise FileNotFoundError(f"GeoPackage not found: {gpkg_path}")

    print(f"[{label}] Building walk graph…")
    graph = build_graph_fn()

    nodes_before = graph.number_of_nodes()
    edges_before = graph.number_of_edges()
    print(f"[{label}] Before insertion — nodes: {nodes_before}, edges: {edges_before}")

    print(f"[{label}] Inserting services from {gpkg_path}…")
    graph, inserted = insert_services_from_gpkg(graph, str(gpkg_path))

    nodes_after = graph.number_of_nodes()
    edges_after = graph.number_of_edges()
    total_inserted = sum(len(v) for v in inserted.values())
    print(f"[{label}] After insertion  — nodes: {nodes_after}, edges: {edges_after}")
    print(f"[{label}] Service nodes added: {total_inserted} "
          f"(+{nodes_after - nodes_before} net nodes, "
          f"+{edges_after - edges_before} net edges)")

    graphml_path = graphs_dir / graphml_name
    png_path = graphs_dir / png_name
    print(f"[{label}] Saving graph → {graphml_path}")
    save_routed_graph(graph, graphml_path)
    print(f"[{label}] Saving map → {png_path}")
    plot_street_vs_service_nodes(graph, png_path)

    return graph, inserted


def build_insert_save_gdansk_poludnie(
    *,
    graphs_dir=_DEFAULT_GRAPHS_DIR,
    gpkg_path=_SCRIPT_DIR / "services_gdansk_poludnie.gpkg",
):
    return _build_insert_save(
        "Gdańsk Południe",
        build_gdansk_poludnie_graph,
        gpkg_path,
        "gdansk_poludnie_walk_services.graphml",
        "gdansk_poludnie_walk_services.png",
        graphs_dir=graphs_dir,
    )


def build_insert_save_gdansk(
    *,
    graphs_dir=_DEFAULT_GRAPHS_DIR,
    gpkg_path=_SCRIPT_DIR / "services_gdansk.gpkg",
):
    return _build_insert_save(
        "Gdańsk",
        build_gdansk_graph,
        gpkg_path,
        "gdansk_walk_services.graphml",
        "gdansk_walk_services.png",
        graphs_dir=graphs_dir,
    )


def build_insert_save_london(
    *,
    graphs_dir=_DEFAULT_GRAPHS_DIR,
    gpkg_path=_SCRIPT_DIR / "services_london.gpkg",
):
    return _build_insert_save(
        "London",
        build_london_graph,
        gpkg_path,
        "london_walk_services.graphml",
        "london_walk_services.png",
        graphs_dir=graphs_dir,
    )


if __name__ == '__main__':
    import sys

    runners = {
        "gdansk_poludnie": build_insert_save_gdansk_poludnie,
        "gdansk": build_insert_save_gdansk,
        "london": build_insert_save_london,
    }
    argv = [a.lower() for a in sys.argv[1:]]
    if not argv or argv == ["all"]:
        keys = list(runners) if argv == ["all"] else ["gdansk_poludnie"]
    else:
        keys = argv
    for k in keys:
        if k not in runners:
            print(
                f"Unknown target {k!r}. Use: gdansk_poludnie | gdansk | london | all",
                file=sys.stderr,
            )
            sys.exit(1)
        runners[k]()
