import os
import time
import json
import pandas as pd
import folium
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
from sqlalchemy import create_engine

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print("Connecting to database...")
db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

print("Running query...")
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
print(f"Query complete: {len(df)} rows")

print("Aggregating data...")
summary = (
    df.groupby(["city", "county", "state"], dropna=False)
      .agg(records=("orig_client_id", "count"),
           unique_clients=("orig_client_id", pd.Series.nunique))
      .reset_index()
)
print("Aggregation done")

print("Preparing geocoder...")
geolocator = Nominatim(user_agent="nj_map", timeout=10)
city_coords = {}
cache_file = "city_coords_cache.json"

if os.path.exists(cache_file):
    with open(cache_file, "r", encoding="utf-8") as f:
        city_coords = json.load(f)

unique_cities = summary["city"].unique()
print(f"Total cities to check: {len(unique_cities)}")

count = 0
for city in unique_cities:
    count += 1
    if city in city_coords:
        continue
    address = f"{city}, NJ"
    try:
        loc = geolocator.geocode(address)
        if loc:
            city_coords[city] = {"lat": loc.latitude, "lon": loc.longitude}
        else:
            city_coords[city] = {"lat": None, "lon": None}
    except (GeocoderTimedOut, GeocoderUnavailable):
        city_coords[city] = {"lat": None, "lon": None}
    if count % 10 == 0:
        print(f"Processed {count}/{len(unique_cities)} cities")
    time.sleep(1)

with open(cache_file, "w", encoding="utf-8") as f:
    json.dump(city_coords, f, indent=4, ensure_ascii=False)

print("Merging coordinates...")
summary["latitude"] = summary["city"].map(lambda c: city_coords.get(c, {}).get("lat"))
summary["longitude"] = summary["city"].map(lambda c: city_coords.get(c, {}).get("lon"))
summary = summary.dropna(subset=["latitude", "longitude"])
print(f"Valid coordinates: {len(summary)}")

print("Building map...")
nj_center = [40.0583, -74.4057]
m = folium.Map(location=nj_center, zoom_start=8, tiles="CartoDB positron")

for i, row in summary.iterrows():
    popup = (
        f"<b>{row['city']}, NJ</b><br>"
        f"Records: {row['records']}<br>"
        f"Unique Clients: {row['unique_clients']}"
    )
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=max(4, min(row["records"] / 50, 15)),
        color="blue",
        fill=True,
        fill_opacity=0.6,
        popup=popup
    ).add_to(m)
    if i % 10 == 0:
        print(f"Added {i}/{len(summary)} markers")

m.save("nj_client_map.html")
print("Map saved to nj_client_map.html")
