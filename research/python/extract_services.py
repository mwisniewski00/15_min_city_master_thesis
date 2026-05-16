import geopandas as gpd
import osmnx
import pandas as pd
from shapely.ops import unary_union

NEXI_TAGS = {
    "education": {
        "amenity": [
            "college", "driving_school", "kindergarten", "language_school",
            "music_school", "school", "university",
        ],
    },
    "entertainment": {
        "amenity": [
            "arts_centre", "brothel", "casino", "cinema", "community_centre",
            "conference_centre", "events_venue", "fountain", "gambling",
            "love_hotel", "nightclub", "planetarium", "public_bookcase",
            "social_centre", "stripclub", "studio", "swingerclub", "theatre",
        ],
    },
    "grocery": {
        "shop": [
            "alcohol", "bakery", "beverages", "brewing_supplies", "butcher",
            "cheese", "chocolate", "coffee", "confectionery", "convenience",
            "deli", "dairy", "farm", "frozen_food", "greengrocer",
            "health_food", "ice_cream", "pasta", "pastry", "seafood",
            "spices", "tea", "water", "supermarket", "department_store",
            "general", "kiosk", "mall",
        ],
    },
    "health": {
        "amenity": [
            "clinic", "dentist", "doctors", "hospital", "nursing_home",
            "pharmacy", "social_facility",
        ],
    },
    "posts_banks": {
        "amenity": ["atm", "bank", "bureau_de_change", "post_office"],
    },
    "parks": {
        "leisure": ["park", "dog_park"],
    },
    "sustenance": {
        "amenity": [
            "restaurant", "pub", "bar", "cafe", "fast_food", "food_court",
            "ice_cream", "biergarten",
        ],
    },
    "shops": {
        "shop": [
            # general retail
            "department_store", "general", "kiosk", "mall",
            # fashion & clothing
            "wholesale", "baby_goods", "bag", "boutique", "clothes", "fabric",
            "fashion_accessories", "jewelry", "leather", "watches", "wool",
            "charity", "second_hand", "variety_store",
            # health & beauty
            "beauty", "chemist", "cosmetics", "erotic", "hairdresser",
            "hairdresser_supply", "hearing_aids", "herbalist", "massage",
            "medical_supply", "nutrition_supplements", "optician", "perfumery",
            "tattoo",
            # home improvement & garden
            "agrarian", "appliance", "bathroom_furnishing", "doityourself",
            "electrical", "energy", "fireplace", "florist", "garden_centre",
            "garden_furniture", "gas", "glaziery", "groundskeeping", "hardware",
            "houseware", "locksmith", "paint", "security", "trade",
            # furniture & interior
            "antiques", "bed", "candles", "carpet", "curtain", "doors",
            "flooring", "furniture", "household_linen", "interior_decoration",
            "kitchen", "lighting", "tiles", "window_blind",
            # electronics
            "computer", "electronics", "hifi", "mobile_phone", "radio_technics",
            "vacuum_cleaner",
            # sport & vehicles
            "bicycle", "boat", "car", "car_repair", "car_parts", "caravan",
            "fuel", "fishing", "golf", "hunting", "jet_ski", "military_surplus",
            "motorcycle", "outdoor", "scuba_diving", "ski", "snowmobile",
            "swimming_pool", "trailer", "tyres",
            # art, leisure & collectibles
            "art", "collector", "craft", "frame", "games", "model", "music",
            "musical_instrument", "photo", "camera", "trophy", "video",
            "video_games", "anime",
            # books & media
            "books", "gift", "lottery", "newsagent", "stationery", "ticket",
            "bookmaker",
            # miscellaneous
            "cannabis", "copyshop", "drycleaning", "e-cigarette",
            "funeral_directors", "laundry", "moneylender", "party", "pawnbroker",
            "pet", "pet_grooming", "pest_control", "pyrotechnics", "religion",
            "storage_rental", "tobacco", "toys", "travel_agency", "vacant",
            "weapons", "outpost",
        ],
    },
}


def _features_shop_tags_chunked(polygon, shop_values, *, chunk_size=10):
    parts = []
    shop_list = list(shop_values)
    for start in range(0, len(shop_list), chunk_size):
        chunk = shop_list[start : start + chunk_size]
        part = osmnx.features.features_from_polygon(polygon, {"shop": chunk})
        if not part.empty:
            parts.append(part)
    if not parts:
        return gpd.GeoDataFrame(geometry=gpd.GeoSeries(dtype="geometry"), crs="EPSG:4326")
    merged = pd.concat(parts)
    if merged.index.duplicated().any():
        merged = merged[~merged.index.duplicated(keep="first")]
    return merged


def fetch_services_for_polygon(polygon, output_path, *, overpass_mitigations=False):
    for category, tags in NEXI_TAGS.items():
        try:
            if overpass_mitigations and category in ("shops", "grocery"):
                gdf = _features_shop_tags_chunked(polygon, tags["shop"])
            else:
                gdf = osmnx.features.features_from_polygon(polygon, tags)
        except Exception as e:
            print(f"  [{category}] error, skipping: {e!r}")
            continue
        if gdf.empty:
            print(f"  [{category}] empty result, skipping")
            continue
        gdf = gdf.copy()
        gdf["category"] = category
        gdf["geometry"] = gdf.geometry.to_crs(epsg=3035).centroid
        gdf = gdf[["geometry", "category"]]
        gdf.to_file(output_path, layer=category, driver="GPKG")
        print(f"  [{category}] {len(gdf)} features written")


def fetch_services_for_place(place_query, output_path, *, overpass_mitigations=False):
    gdf_boundary = osmnx.geocoder.geocode_to_gdf(place_query)
    polygon = gdf_boundary.geometry.iloc[0]
    print(f"Fetching services for '{place_query}' → {output_path}")
    fetch_services_for_polygon(polygon, output_path, overpass_mitigations=overpass_mitigations)


# GDANSK POLUDNIE
#######################################
# sub_districts = [
#     "Chełm, Gdańsk, Poland",
#     "Jasień, Gdańsk, Poland",
#     "Orunia Górna-Gdańsk Południe, Gdańsk, Poland",
#     "Ujeścisko-Łostowice, Gdańsk, Poland",
# ]

# gdfs = [osmnx.geocoder.geocode_to_gdf(q) for q in sub_districts]
# polygon_poludnie = unary_union([gdf.geometry.iloc[0] for gdf in gdfs])

# print(f"Fetching services for Gdańsk Południe → services_gdansk_poludnie.gpkg")
# fetch_services_for_polygon(polygon_poludnie, "services_gdansk_poludnie.gpkg")
#######################################

# Gdańsk
#######################################
# fetch_services_for_place("Gdańsk, Poland", "services_gdansk.gpkg")
#######################################

# Greater London
#######################################
# fetch_services_for_place(
#     "Greater London, United Kingdom",
#     "services_london.gpkg",
#     overpass_mitigations=True,
# )
#######################################
