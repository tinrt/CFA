import os
import time
import json
import pandas as pd
import folium
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from sqlalchemy import create_engine

load_dotenv()

print("Loading database credentials...")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("Connecting to database...")
db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

print("Querying database...")
query = """
SELECT
    city,
    county,
    state,
    orig_client_id
FROM client_visit
WHERE state ILIKE 'NJ'
AND city IS NOT NULL;
"""
df = pd.read_sql(query, engine)
print(f"Loaded {len(df)} rows")

print("Aggregating data...")
summary = (
    df.groupby(["city", "county", "state"], dropna=False)
      .agg(records=("orig_client_id", "count"),
           unique_clients=("orig_client_id", pd.Series.nunique))
      .reset_index()
)
print(f"Aggregated {len(summary)} unique cities")

cache_file = "city_coords_cache.json"
if os.path.exists(cache_file):
    print("Loading cached coordinates...")
    with open(cache_file, "r", encoding="utf-8") as f:
        city_coords = json.load(f)
else:
    print("Geocoding cities...")
    geolocator = Nominatim(user_agent="nj_map", timeout=10)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    city_coords = {}
    unique_cities = summary["city"].unique()
    for i, city in enumerate(unique_cities, 1):
        loc = geocode(f"{city}, NJ")
        if loc:
            city_coords[city] = {"lat": loc.latitude, "lon": loc.longitude}
        else:
            city_coords[city] = {"lat": None, "lon": None}
        if i % 10 == 0:
            print(f"Geocoded {i}/{len(unique_cities)} cities")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(city_coords, f, indent=4, ensure_ascii=False)
    print("Geocoding complete and cached")

print("Merging coordinates...")
summary["latitude"] = summary["city"].map(lambda c: city_coords.get(c, {}).get("lat"))
summary["longitude"] = summary["city"].map(lambda c: city_coords.get(c, {}).get("lon"))
summary = summary.dropna(subset=["latitude", "longitude"])
print(f"Valid coordinates found for {len(summary)} cities")

print("Building map...")
nj_center = [40.0583, -74.4057]
m = folium.Map(location=nj_center, zoom_start=8, tiles="CartoDB positron")

layer_high = folium.FeatureGroup(name="High Activity (Records > 500)", show=True)
layer_mid = folium.FeatureGroup(name="Medium Activity (100–500)", show=True)
layer_low = folium.FeatureGroup(name="Low Activity (<100)", show=True)

for i, row in enumerate(summary.itertuples(), 1):
    popup = (
        f"<b>{row.city}, NJ</b><br>"
        f"Records: {row.records}<br>"
        f"Unique Clients: {row.unique_clients}"
    )
    if row.records > 500:
        color = "red"
        group = layer_high
    elif row.records >= 100:
        color = "orange"
        group = layer_mid
    else:
        color = "blue"
        group = layer_low

    folium.CircleMarker(
        location=[row.latitude, row.longitude],
        radius=max(4, min(row.records / 50, 15)),
        color=color,
        fill=True,
        fill_opacity=0.6,
        popup=popup
    ).add_to(group)

    if i % 20 == 0:
        print(f"Added {i}/{len(summary)} markers")

m.add_child(layer_high)
m.add_child(layer_mid)
m.add_child(layer_low)
folium.LayerControl(collapsed=False).add_to(m)

m.save("nj_client_map.html")
print("Map saved to nj_client_map.html")
