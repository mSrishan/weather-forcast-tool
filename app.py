import requests
import json 
from groq import Groq
import os 
from dotenv import load_dotenv

load_dotenv()

#initialize the Groq client with API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_weather_forcast(city: str, days: int = 3) -> str:
    """
    Get the weather forecast for a given city and number of days.

    Args:
        city (str): The name of the city.
        days (int): The number of days for the forecast (default is 3).

    Returns:
        str: The weather forecast as a string.
    """
    geo_url = 