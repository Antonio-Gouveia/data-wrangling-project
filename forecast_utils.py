import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# === Weather code dictionaries ===
weather_map_en = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

weather_visibility_scores = {
    0: 100, 1: 90, 2: 80, 3: 60,
    45: 30, 48: 30,
    51: 50, 53: 40, 55: 30,
    56: 25, 57: 25,
    61: 60, 63: 45, 65: 30,
    66: 25, 67: 25,
    71: 60, 73: 45, 75: 30, 77: 25,
    80: 60, 81: 40, 82: 25,
    85: 45, 86: 30,
    95: 20, 96: 15, 99: 10
}

def get_forecast(lat, lon, start_date, end_date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "weather_code"
        ],
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def enrich_forecast_df(df):
    df["weather_description"] = df["weather_code"].map(weather_map_en).fillna("Unknown")
    df["weather_visibility_score"] = df["weather_code"].map(weather_visibility_scores).fillna(50)
    df["precipitation_penalty"] = df["precipitation_sum"].clip(0, 10) * 10
    df["precipitation_penalty"] = df["precipitation_penalty"].clip(0, 100)
    df["is_clear_night"] = df["weather_code"].apply(lambda x: 1 if x in [0, 1, 2] else 0)
    df["UFO_weather_optimal"] = (
        df["weather_visibility_score"] * 0.60 +
        (100 - df["precipitation_penalty"]) * 0.20 +
        df["is_clear_night"] * 100 * 0.20
    ).round(2)
    return df

def pivot_forecast(df):
    df["location_key"] = df["latitude"].round(5).astype(str) + "_" + df["longitude"].round(5).astype(str)
    df = df.sort_values(by=["location_key", "date"])
    df["day_index"] = df.groupby("location_key").cumcount() + 1
    pivot = df.pivot(index="location_key", columns="day_index", values="UFO_weather_optimal")
    pivot.columns = [f"optimal_day_{i}" for i in pivot.columns]
    pivot = pivot.reset_index()
    pivot[["latitude", "longitude"]] = pivot["location_key"].str.split("_", expand=True).astype(float)
    cols = ["latitude", "longitude"] + [f"optimal_day_{i}" for i in range(1, 8)]
    pivot = pivot[cols]
    pivot["mean_optimal_score"] = pivot[[f"optimal_day_{i}" for i in range(1, 8)]].mean(axis=1)
    return pivot.sort_values(by="mean_optimal_score", ascending=False)

def get_location_info(lat, lon):
    geolocator = Nominatim(user_agent="geo_lookup")
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)
    try:
        location = reverse((lat, lon), language="en")
        if location and location.raw.get("address"):
            address = location.raw["address"]
            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("hamlet")
            )
            country = address.get("country")
            return pd.Series([city, country])
    except Exception as e:
        print(f"Error for coordinates ({lat}, {lon}): {e}")
    return pd.Series([None, None])