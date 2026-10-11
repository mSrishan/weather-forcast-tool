import json
import os
import requests
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()


def get_weather_forecast(city: str, days: int = 3) -> str:
    """Fetch coordinates and daily weather forecast using Open-Meteo."""
    # Step 1: Geocode city name to lat/lon
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_res = requests.get(geo_url, timeout=10).json()

    if not geo_res.get("results"):
        return f"City '{city}' not found."

    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]

    # Step 2: Fetch forecast data
    weather_url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max&hourly=temperature_2m"
        f"&timezone=auto&forecast_days={days}"
    )
    weather_res = requests.get(weather_url, timeout=10).json()

    daily = weather_res.get("daily", {})
    dates = daily.get("time", [])
    temps = daily.get("temperature_2m_max", [])

    if not dates or not temps:
        return f"No weather data available for '{city}'."

    forecast_details = "; ".join(
        f"{date}: {temp}°C max" for date, temp in zip(dates, temps)
    )
    return f"Weather forecast for '{city}': {forecast_details}."


def main() -> None:
    raw_key = os.getenv("GROQ_API_KEY", "")
    api_key = raw_key.strip().strip('"').strip("'")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Add it to your .env file.")

    client = Groq(api_key=api_key)

    # Use the exact model ID present in your endpoint
    model_name = "openai/gpt-oss-120b"

    messages = [
        {
            "role": "user",
            "content": "Give me the weather forecast for Paris for 5 days.",
        }
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather_forecast",
                "description": "Get the weather forecast for a given city and number of days.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city to get the weather forecast for.",
                        },
                        "days": {
                            "type": "integer",
                            "description": "The number of days to get the forecast for. Default is 3.",
                            "default": 3,
                        },
                    },
                    "required": ["city"],
                },
            },
        }
    ]

    # Send initial user request to the model
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        temperature=0.2,
    )

    response_message = response.choices[0].message
    tool_calls = getattr(response_message, "tool_calls", None) or []

    if not tool_calls:
        print(response_message.content or "No response from the model.")
        return

    # Add the assistant's tool-call request to messages
    messages.append(response_message)

    # Execute requested functions
    for tool_call in tool_calls:
        if tool_call.function.name == "get_weather_forecast":
            args = json.loads(tool_call.function.arguments)
            city = args.get("city", "Paris")
            days = args.get("days", 3)

            forecast = get_weather_forecast(city=city, days=days)

            # Return tool output back to the model
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": "get_weather_forecast",
                    "content": forecast,
                }
            )

    # Let the model synthesize the final answer
    final_response = client.chat.completions.create(
        model=model_name,
        messages=messages,
    )

    print("\n--- Final Answer ---\n")
    print(final_response.choices[0].message.content)


if __name__ == "__main__":
    main()