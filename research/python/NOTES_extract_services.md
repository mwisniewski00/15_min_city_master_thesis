# Notes on `extract_services.py` — design decisions

## What the script does

Fetches OpenStreetMap Points of Interest (PoIs) for three study areas — Gdańsk Południe, Gdańsk (whole city), and Greater London — and stores them in GeoPackage files with one layer per NEXI service category.

Output files produced by the script:
- `services_gdansk_poludnie.gpkg`
- `services_gdansk.gpkg`
- `services_london.gpkg`

## NEXI service categories and OSM tag mapping

The eight categories come from **NEXI Table 1**. Most map directly to `amenity=*` or `shop=*` values; one exception:

| Category | OSM key | Note |
|---|---|---|
| education | `amenity` | — |
| entertainment | `amenity` | — |
| grocery | `shop` | Food/drink retail only |
| health | `amenity` | — |
| posts_banks | `amenity` | — |
| parks | `leisure` | Paper uses "amenity" but correct OSM tag is `leisure` |
| sustenance | `amenity` | — |
| shops | `shop` | Non-food retail only |

## Why `grocery` and `shops` both use `shop=*`, and why they need explicit value lists

OSMnx's `features_from_polygon` (and `features_from_place`) accept `{"shop": True}` to return **all** features with any `shop` tag value.  Using `True` for both `grocery` and `shops` would produce overlapping layers — bakeries, supermarkets, etc. would appear in both.

The solution is to enumerate the specific `shop=*` values that belong to each category:

- **grocery** — food/drink-oriented shop types (bakery, supermarket, greengrocer, etc.)
- **shops** — non-food retail (clothes, electronics, furniture, etc.)

This ensures clean, non-overlapping layers that match the NEXI definition.

Alternative (more maintainable) approach: issue a single `{"shop": True}` query, then split the returned GeoDataFrame into `grocery` and `shops` rows in Python using two `frozenset`s of allowed values, and drop rows in neither set. Same end result, but the split logic is centralised in one place instead of duplicated in two tag lists.

## Why `parks` uses `leisure`, not `amenity`

NEXI Table 1 lists parks under "amenity" as a conceptual grouping, but in OSM `park` and `dog_park` are values of the `leisure` key, not `amenity`. Using `{"amenity": ["park"]}` returns almost nothing; the correct query is `{"leisure": ["park", "dog_park"]}`.

## Geometry normalisation

OSM features can be points, lines, or polygons (e.g. a hospital building outline). All geometries are reduced to their **centroid** before writing:

```python
gdf["geometry"] = gdf.geometry.to_crs(epsg=3035).centroid
```

Reprojecting to EPSG:3035 (a metric CRS covering Europe) before calling `.centroid` avoids the `UserWarning: Geometry is in a geographic CRS` inaccuracy — centroids computed in degrees are skewed near the poles. The resulting centroid coordinates are in the 3035 projected space, consistent with the walk-graph CRS used in `extract_graph.py`.

This ensures every layer contains only point features, which is the expected input format for accessibility / isochrone analysis.

## Area definitions

The three areas mirror `extract_graph.py`:

- **Gdańsk Południe** — four sub-districts geocoded individually and merged with `shapely.ops.unary_union` (same boundary used for the walk graph).
- **Gdańsk** — single `geocode_to_gdf("Gdańsk, Poland")` call; OSM holds the full municipal boundary polygon.
- **Greater London** — single `geocode_to_gdf("Greater London, United Kingdom")` call.
