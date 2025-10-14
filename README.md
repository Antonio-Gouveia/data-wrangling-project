# 🛸 UFO Sightings & Forecast Analysis

This project analyzes UFO sightings in relation to historical and forecasted weather conditions using the Open-Meteo API. It is structured into two modular notebooks with reusable Python utilities.

---

## 📁 Project Structure

ufo_project/

- Cleans UFO data and enriches with historical weather
ufo_weather_full.ipynb
- Scores sightings and forecasts optimal conditions
UFOscope.ipynb 
- Functions for scoring, forecasting, and geocoding
weather_utils.py                     
forecast_utils.py
- Project overview and instructions
README.md                            



---

## 🧪 Requirements

Before running the notebooks, install the required packages:

```bash
pip install pandas numpy requests geopy tqdm folium

📓 Notebook 1: notebook_1_data_enrichment.ipynb
Purpose:
- Load and clean UFO sightings dataset
- Fetch historical weather data for each sighting
- Merge weather data and export enriched dataset
Output:
- ufo_weather_full.csv — enriched dataset with weather features

📓 Notebook 2: notebook_2_forecast_analysis.ipynb
Purpose:
- Score sightings based on visibility and duration
- Select top 500 sightings from fall months
- Fetch 7-day weather forecasts for those locations
- Calculate predictive visibility scores
- Enrich with city/country and visualize with heat map
Output:
- Interactive heat map of top forecasted locations
- Optional CSV: forecast_with_cities.csv

🧩 Modular Utilities
- weather_utils.py:
- save_cache, load_cache
- get_weather_for_location_date
- build_weather_cache_from_df, attach_weather_to_df
- forecast_utils.py:
- get_forecast, enrich_forecast_df, pivot_forecast
- get_location_info
- weather_map_en, weather_visibility_scores

👥 Collaboration
This project is designed for collaborative analysis and reproducibility. All code is modular, documented, and ready for team sharing.

## 📽️ Project Presentation

You can view the full project presentation here:  
[UFO Sightings & Forecast Analysis — Canva Presentation](https://www.canva.com/design/DAG1fV_s9to/1CI9lOwQ2Z0MuaFpfgnZuA/edit?utm_content=DAG1fV_s9to&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

👥 Authors
- António Gouveia
- Martín Paez
- Miguel Florindo


📬 Questions or Feedback?
Feel free to reach out or fork the repository to build on this work!


