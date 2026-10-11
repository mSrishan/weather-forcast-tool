import requests
import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

#initialize the Groq client with API key
client= Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_weather_frocast(city: str, days: int = 3 ) -> str:
    
    """
    Get the weather forecast for a given city and number of days.

    Args:
        city (str): The name of the city to get the weather forecast for.
        days (int): The number of days to get the forecast for. Default is 3.

    Returns:
        str: A string containing the weather forecast.
    """
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_res = requests.get(geo_url).json()
    
    if not geo_res.get("results"):
        return f"City '{city}' not found."
    
    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]
    
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&hourly=temperature_2m&timezone=auto&forecast_days={days}"
    weather_res = requests.get(weather_url).json()
    
    daily = weather_res.get("daily", {})
    dates = daily.get("time", [])
    temps = daily.get("temperature_2m_max", [])

    if not dates or not temps:
        return f"No weather data available for '{city}'."

    forecast_details = "; ".join(
        f"{date}: {temp}°C max" for date, temp in zip(dates, temps)
    )
    return f"Weather forecast for '{city}': {forecast_details}."
   
    