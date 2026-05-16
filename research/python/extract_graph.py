import osmnx
from shapely.ops import unary_union
import matplotlib.pyplot as plt
import geopandas as gpd

GDANSK_POLUDNIE_SUB_DISTRICTS = [
    "Chełm, Gdańsk, Poland",
    "Jasień, Gdańsk, Poland",
    "Orunia Górna-Gdańsk Południe, Gdańsk, Poland",
    "Ujeścisko-Łostowice, Gdańsk, Poland",
]

PLACE_GDANSK = "Gdańsk, Poland"
PLACE_LONDON = "Greater London, United Kingdom"

WALKING_SPEED_KMH = 5.0
WALKING_SPEED_IN_METERS_PER_MINUTE = WALKING_SPEED_KMH * 1000.0 / 60.0


def process_graph(graph):
    # 3035 is the CRS for Europe
    graph = osmnx.projection.project_graph(graph, to_crs=3035)

    graph = osmnx.simplification.consolidate_intersections(
        graph,
        tolerance=10,
        rebuild_graph=True,
        dead_ends=False,
        reconnect_edges=True
    )

    return osmnx.convert.to_undirected(graph)


def build_gdansk_poludnie_graph():
    gdfs = [osmnx.geocoder.geocode_to_gdf(q) for q in GDANSK_POLUDNIE_SUB_DISTRICTS]
    polygon = unary_union([gdf.geometry.iloc[0] for gdf in gdfs])
    graph = osmnx.graph.graph_from_polygon(polygon, network_type="walk")
    return process_graph(graph)


def build_gdansk_graph():
    graph = osmnx.graph.graph_from_place(PLACE_GDANSK, network_type="walk")
    return process_graph(graph)


def build_london_graph():
    graph = osmnx.graph.graph_from_place(PLACE_LONDON, network_type="walk")
    return process_graph(graph)


# GDANSK POLUDNIE
#######################################
# graph = build_gdansk_poludnie_graph()
# print(f"Nodes: {graph.number_of_nodes()}")
# print(f"Edges: {graph.number_of_edges()}")

# gdfs = [osmnx.geocoder.geocode_to_gdf(q) for q in GDANSK_POLUDNIE_SUB_DISTRICTS]
# polygon = unary_union([gdf.geometry.iloc[0] for gdf in gdfs])
# fig, ax = osmnx.plot.plot_graph(graph, show=False, close=False)
# boundary = gpd.GeoSeries([polygon], crs="EPSG:4326").to_crs(epsg=3035)
# boundary.boundary.plot(ax=ax, color="red", linewidth=2)
# plt.savefig("graph.png", dpi=300, bbox_inches="tight")
# plt.close()
#######################################
# Nodes: 5159
# Edges: 11745

# Gdańsk
#######################################
# graph = build_gdansk_graph()
#
# print(f"Nodes: {graph.number_of_nodes()}")
# print(f"Edges: {graph.number_of_edges()}")
#
# gdf_boundary = osmnx.geocoder.geocode_to_gdf(PLACE_GDANSK)  # module constant
# polygon = gdf_boundary.geometry.iloc[0]
#
# fig, ax = osmnx.plot.plot_graph(graph, show=False, close=False)
# boundary = gpd.GeoSeries([polygon], crs="EPSG:4326").to_crs(epsg=3035)
# boundary.boundary.plot(ax=ax, color="red", linewidth=2)
# plt.savefig("graph_gdansk.png", dpi=300, bbox_inches="tight")
# plt.close()
#######################################
# Nodes: 24610
# Edges: 53584

# Greater London
#######################################
# graph = build_london_graph()

# print(f"Nodes: {graph.number_of_nodes()}")
# print(f"Edges: {graph.number_of_edges()}")

# gdf_boundary = osmnx.geocoder.geocode_to_gdf(PLACE_LONDON)  # module constant
# polygon = gdf_boundary.geometry.iloc[0]

# fig, ax = osmnx.plot.plot_graph(graph, show=False, close=False)
# boundary = gpd.GeoSeries([polygon], crs="EPSG:4326").to_crs(epsg=3035)
# boundary.boundary.plot(ax=ax, color="red", linewidth=2)
# plt.savefig("graph_london.png", dpi=300, bbox_inches="tight")
# plt.close()
#######################################
# Nodes: 186437
# Edges: 300862
