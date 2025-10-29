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

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

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

summary = (
    df.groupby(["city", "county", "state"], dropna=False)
      .agg(records=("orig_client_id", "count"),
           unique_clients=("orig_client_id", pd.Series.nunique))
      .reset_index()
)

cache_file = "city_coords_cache.json"
if os.path.exists(cache_file):
    with open(cache_file, "r", encoding="utf-8") as f:
        city_coords = json.load(f)
else:
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
            print(f"Geocoded {i}/{len(unique_cities)}")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(city_coords, f, indent=4, ensure_ascii=False)

summary["latitude"] = summary["city"].map(lambda c: city_coords.get(c, {}).get("lat"))
summary["longitude"] = summary["city"].map(lambda c: city_coords.get(c, {}).get("lon"))
summary = summary.dropna(subset=["latitude", "longitude"])

nj_center = [40.0583, -74.4057]
m = folium.Map(location=nj_center, zoom_start=8, tiles="CartoDB positron")

for _, row in summary.iterrows():
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

m.save("nj_client_map.html")

