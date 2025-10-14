# ufo_weather_utils.py

import pandas as pd
import numpy as np
import requests
import time
import pickle
import os

def save_cache(cache, filename="weather_cache_test.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(cache, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_cache(filename="weather_cache_test.pkl"):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    return {}

def get_weather_for_location_date(lat, lon, date):
    try:
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": date,
            "end_date": date,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "weather_code",
            ],
            "timezone": "auto"
        }
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if "daily" in data and len(data["daily"].get("time", [])) > 0:
            df = pd.DataFrame(data["daily"])
            df["time"] = pd.to_datetime(df["time"]).dt.date
            return df
        return None
    except Exception as e:
        print(f"API error ({lat},{lon},{date}): {e}")
        return None

def build_weather_cache_from_df(df, delay=0.5, cache_file="weather_cache_test.pkl"):
    cache = load_cache(cache_file)
    total = len(df)
    print(f"\nStarting weather cache build for {total} rows...\n")

    for idx, row in df.iterrows():
        lat, lon, date = row["latitude"], row["longitude"], row["date"]
        if pd.isna(lat) or pd.isna(lon) or pd.isna(date):
            continue
        key = f"{lat:.2f}_{lon:.2f}_{date}"
        if key in cache:
            continue

        weather = get_weather_for_location_date(lat, lon, date)
        if weather is not None:
            cache[key] = weather

        print(f"[{idx+1}/{total}] -> {key}")
        time.sleep(delay)

    save_cache(cache, cache_file)
    print(f"\n✅ Cache completed: {len(cache)} entries saved.\n")
    return cache

def attach_weather_to_df(df, cache):
    df_out = df.copy()
    df_out["temp_max"] = np.nan
    df_out["temp_min"] = np.nan
    df_out["precipitation_sum"] = np.nan
    df_out["weather_code"] = np.nan

    for i, row in df_out.iterrows():
        key = f"{row['latitude']:.2f}_{row['longitude']:.2f}_{row['date']}"
        weather_df = cache.get(key)
        if weather_df is not None and not weather_df.empty:
            w = weather_df.iloc[0]
            df_out.at[i, "temp_max"] = w.get("temperature_2m_max", np.nan)
            df_out.at[i, "temp_min"] = w.get("temperature_2m_min", np.nan)
            df_out.at[i, "precipitation_sum"] = w.get("precipitation_sum", np.nan)
            df_out.at[i, "weather_code"] = w.get("weather_code", np.nan)

    return df_out