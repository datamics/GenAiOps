import json
from typing import Tuple, Optional, List
from datetime import datetime, timedelta
from urllib import request, parse, error
import pytz
import dateparser
from langfuse import observe
from langchain_core.tools import tool

# ---------------------------------------------------------
# Retriever Import Logic
# ---------------------------------------------------------
try:
    from retriever import get_retriever
except ModuleNotFoundError:
    try:
        from backend.retriever import get_retriever
    except ModuleNotFoundError:
        # Fallback if retriever cannot be imported (for standalone testing)
        get_retriever = None


# ---------------------------------------------------------
# HTTP & Helper Functions (Internal)
# ---------------------------------------------------------

@observe(as_type="span")
def _http_get(url: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
    """
    Simple HTTP-GET-Wrapper (replaces requests).
    """
    if params:
        query = parse.urlencode(params, doseq=True)
        url = f"{url}?{query}"

    req = request.Request(url, method="GET")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    with request.urlopen(req, timeout=10) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        raw = resp.read().decode(charset)
        return json.loads(raw)


@observe()
def get_latitude_longitude(city: str, country: str) -> Optional[Tuple[float, float]]:
    """
    Internal helper: Gives back latitude and longitude for a city and a country.
    """
    try:
        data = _http_get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "city": city,
                "country": country,
                "format": "json"
            },
            headers={"User-Agent": "GenAiProject"}
        )

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        return None

    except (error.URLError, error.HTTPError, KeyError, IndexError, ValueError) as e:
        print(f"Error while loading of the Geo-Koordinates: {e}")
        return None


@observe()
def get_weather(latitude: float, longitude: float) -> Optional[dict]:
    """
    Internal helper: Retrieves the weather data for given coordinates.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "hourly": ["precipitation", "cloudcover", "wind_speed_10m"],
        "timezone": "auto"
    }

    try:
        data = _http_get(
            url,
            params=params,
            headers={"User-Agent": "GenAiProject"}
        )

        if "current_weather" in data:
            current = data["current_weather"]
            return {
                "temperature": current.get("temperature"),
                "windspeed": current.get("windspeed"),
                "winddirection": current.get("winddirection"),
                "weathercode": current.get("weathercode"),
                "time": current.get("time"),
                "rain": current.get("precipitation"),
                "cloudcover": current.get("cloudcover")
            }
        return None

    except (error.URLError, error.HTTPError, KeyError, ValueError, IndexError) as e:
        print(f"Error while retrieving the current weather: {e}")
        return None


@observe()
def get_weather_forecast(latitude: float, longitude: float, forecast_date: str) -> Optional[dict]:
    """
    Internal helper: Gets weather forecast for a specific date for the given latitude and longitude.
    """
    url = "https://api.open-meteo.com/v1/ecmwf"

    # Define start and end dates for 10-day forecast range
    start_date = datetime.utcnow().date()
    end_date = start_date + timedelta(days=10)

    try:
        requested_date = datetime.strptime(forecast_date, "%Y-%m-%d").date()
    except ValueError:
        print(f"Date format error: {forecast_date}")
        return None

    if requested_date < start_date or requested_date > end_date:
        print(f"Date '{forecast_date}' is out of range. Please request within {start_date} to {end_date}.")
        return None

    try:
        data = _http_get(
            url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,cloudcover_mean",
                "timezone": "auto",
            },
            headers={"User-Agent": "GenAiProject"}
        )

        if "daily" in data:
            daily_data = data["daily"]
            times = daily_data.get("time", [])
            if forecast_date in times:
                idx = times.index(forecast_date)
                return {
                    "date": forecast_date,
                    "temperature_max": daily_data["temperature_2m_max"][idx],
                    "temperature_min": daily_data["temperature_2m_min"][idx],
                    "precipitation_sum": daily_data["precipitation_sum"][idx],
                    "cloudcover_mean": daily_data.get("cloudcover_mean", [None])[idx],
                }
        return None
    except (error.URLError, error.HTTPError, KeyError, ValueError, IndexError) as e:
        print(f"Error fetching weather forecast: {e}")
        return None


# ---------------------------------------------------------
# LangChain Tools
# ---------------------------------------------------------

@tool
@observe()
def get_weather_from_city_name(city: str, country: str) -> Optional[dict]:
    """
    Gets the current weather for a specific city and country name.
    Useful for questions like "What is the weather in Berlin, Germany right now?"
    """
    coords = get_latitude_longitude(city, country)
    if coords:
        latitude, longitude = coords
        return get_weather(latitude, longitude)
    return None


@tool
@observe()
def get_weather_forecast_from_city_name(city: str, country: str, forecast_date: str) -> Optional[dict]:
    """
    Gets the weather forecast for a specific date (YYYY-MM-DD) for a given city and country.
    The date must be within the next 10 days.
    """
    coords = get_latitude_longitude(city, country)
    if coords:
        latitude, longitude = coords
        return get_weather_forecast(latitude, longitude, forecast_date)
    return None


@tool
@observe()
def get_weather_forecast_from_city_name_date_phrase(city: str, country: str, date_phrase: str) -> Optional[dict]:
    """
    Gets the weather forecast for a given city and country based on a natural language date phrase.
    Useful for questions like "Weather in London tomorrow" or "Forecast for Paris next Friday".
    """
    # Set timezone
    try:
        tz = pytz.timezone("Europe/Berlin")
        now = datetime.now(tz)

        dt = dateparser.parse(
            date_phrase,
            settings={
                "TIMEZONE": "Europe/Berlin",
                "RETURN_AS_TIMEZONE_AWARE": True,
                "RELATIVE_BASE": now
            }
        )

        if dt is None:
            # Fallback on today
            dt = now

        target_date_str = dt.strftime("%Y-%m-%d")
        return get_weather_forecast_from_city_name.func(city, country, target_date_str)

    except Exception as e:
        print(f"Error parsing date phrase '{date_phrase}': {e}")
        return None


# ---------------------------------------------------------
# Tool Aggregation
# ---------------------------------------------------------

def get_tools() -> List:
    """
    Initializes and returns the list of tools available to the agent.
    """
    tools = [
        get_weather_from_city_name,
        get_weather_forecast_from_city_name,
        get_weather_forecast_from_city_name_date_phrase,
    ]

    # Only add retriever if it was successfully imported
    if get_retriever:
        retriever = get_retriever()

        @tool
        def retriever_tool(query: str) -> str:
            """Retrieve relevant documents from the internal database. Use this to search for Information about cities and travel advice."""
            docs = retriever.query(query)
            return "\n\n".join([doc.page_content for doc in docs])

        tools.append(retriever_tool)
    else:
        print("Warning: Retriever could not be initialized.")

    return tools


if __name__ == "__main__":
    print(get_weather_forecast_from_city_name_date_phrase.invoke(
        {"city": "Berlin", "country": "Germany", "date_phrase": "tomorrow"}))
