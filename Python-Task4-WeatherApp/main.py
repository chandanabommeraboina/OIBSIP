"""
=============================================================================
Oasis Infobyte - Python Programming Internship
Task 4: Basic Weather App (Beginner Tier)
Author: Internship Project
Technologies: Python 3, requests, json, python-dotenv, OpenWeatherMap API
=============================================================================

This program fetches and displays real-time weather information for any
city or ZIP code entered by the user using the OpenWeatherMap API.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import requests
from dotenv import load_dotenv


def load_api_key() -> str:
    """
    Loads and validates the OpenWeatherMap API key from the .env file.
    
    Returns:
        str: The API key if found and not a placeholder, otherwise an empty string.
    """
    # Load environment variables from .env file in the current directory or parent
    load_dotenv()
    
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    return api_key


def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Converts temperature from Celsius to Fahrenheit.
    Formula: (C * 9/5) + 32
    
    Args:
        celsius (float): Temperature in degrees Celsius.
        
    Returns:
        float: Temperature in degrees Fahrenheit rounded to 2 decimal places.
    """
    return round((celsius * 9.0 / 5.0) + 32.0, 2)


def get_weather_icon(condition: str) -> str:
    """
    Returns an appropriate weather icon/symbol based on the condition description.
    
    Args:
        condition (str): Main weather condition string (e.g. 'Clear', 'Clouds').
        
    Returns:
        str: Visual icon representing the weather.
    """
    condition_lower = condition.lower()
    if "clear" in condition_lower:
        return "[Sunny/Clear] ☀️"
    elif "cloud" in condition_lower:
        return "[Cloudy] ⛅"
    elif "rain" in condition_lower or "drizzle" in condition_lower:
        return "[Rainy] 🌧️"
    elif "thunder" in condition_lower:
        return "[Thunderstorm] ⛈️"
    elif "snow" in condition_lower:
        return "[Snow] ❄️"
    elif "mist" in condition_lower or "fog" in condition_lower or "haze" in condition_lower:
        return "[Mist/Fog] 🌫️"
    else:
        return "[Weather] 🌤️"


def format_timestamp(epoch_seconds: int, timezone_offset_seconds: int) -> str:
    """
    Converts a Unix epoch timestamp to a local readable time string based
    on the city's timezone offset from UTC.
    
    Args:
        epoch_seconds (int): Epoch timestamp in seconds.
        timezone_offset_seconds (int): Timezone offset in seconds from UTC.
        
    Returns:
        str: Formatted time string (e.g. "06:45 AM").
    """
    try:
        tz = timezone(timedelta(seconds=timezone_offset_seconds))
        dt = datetime.fromtimestamp(epoch_seconds, tz=tz)
        return dt.strftime("%I:%M %p")
    except Exception:
        return "N/A"


def build_api_params(location_query: str, api_key: str) -> dict:
    """
    Builds the query parameters for OpenWeatherMap API.
    Determines whether the input is a ZIP code or a City name.
    
    Args:
        location_query (str): The raw user input (e.g. "London", "90210,us", "Mumbai,in").
        api_key (str): OpenWeatherMap API key.
        
    Returns:
        dict: Query parameters for requests.get().
    """
    cleaned = location_query.strip()
    
    # Check if the query begins with digits (e.g. 90210 or 90210,US or 110001)
    parts = [p.strip() for p in cleaned.split(",")]
    if parts[0].isdigit():
        # OpenWeatherMap supports zip parameter (format: {zip code},{country code})
        # If no country code was provided, we pass the raw zip which OpenWeatherMap treats as US by default
        return {
            "zip": cleaned,
            "appid": api_key,
            "units": "metric"  # Metric returns temperature in Celsius, wind in m/s
        }
    else:
        # Standard city query (e.g. "London" or "London,GB" or "New York,US")
        return {
            "q": cleaned,
            "appid": api_key,
            "units": "metric"
        }


def fetch_weather(location_query: str, api_key: str, timeout: int = 10):
    """
    Sends an HTTP GET request to OpenWeatherMap API to retrieve weather data.
    Handles network errors, timeouts, invalid status codes, and parsing errors.
    
    Args:
        location_query (str): City name or ZIP code.
        api_key (str): OpenWeatherMap API key.
        timeout (int): Maximum time in seconds to wait for a response.
        
    Returns:
        tuple: (data_dict or None, error_message or None)
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = build_api_params(location_query, api_key)
    
    try:
        response = requests.get(base_url, params=params, timeout=timeout)
        
        # Check HTTP status codes
        if response.status_code == 200:
            try:
                data = response.json()
                return data, None
            except ValueError:
                return None, "Error: Failed to parse API response as JSON (Malformed response)."
                
        elif response.status_code == 401:
            return None, (
                "Authentication Error (HTTP 401): Invalid API Key!\n"
                "  -> Please check your OPENWEATHER_API_KEY in the .env file.\n"
                "  -> If you just generated a new key, it can take 10 to 15 minutes to activate."
            )
            
        elif response.status_code == 404:
            # If ZIP query failed, try falling back to 'q' parameter if no country was specified
            if "zip" in params and "," not in location_query:
                fallback_params = {
                    "q": location_query.strip(),
                    "appid": api_key,
                    "units": "metric"
                }
                try:
                    fallback_res = requests.get(base_url, params=fallback_params, timeout=timeout)
                    if fallback_res.status_code == 200:
                        return fallback_res.json(), None
                except Exception:
                    pass
                    
            return None, (
                f"Location Not Found (HTTP 404): Could not find weather for '{location_query}'.\n"
                "  -> Check the spelling of the city name.\n"
                "  -> For non-US ZIP codes, specify the country code (e.g., '110001,IN' or 'EC1A,GB').\n"
                "  -> You can also search as: 'City, Country' (e.g., 'Tokyo, JP' or 'Paris, FR')."
            )
            
        elif response.status_code == 429:
            return None, (
                "Rate Limit Exceeded (HTTP 429): You have exceeded the free API request limit.\n"
                "  -> Please wait a few moments before trying again."
            )
            
        else:
            # Other HTTP errors (e.g. 500, 502, 503)
            error_msg = f"HTTP Error {response.status_code}: {response.reason}"
            try:
                api_error = response.json().get("message", "")
                if api_error:
                    error_msg += f" - {api_error}"
            except Exception:
                pass
            return None, error_msg
            
    except requests.exceptions.ConnectionError:
        return None, (
            "Network Connection Error:\n"
            "  -> Unable to connect to OpenWeatherMap servers.\n"
            "  -> Please check your internet connection, Wi-Fi, or firewall settings."
        )
        
    except requests.exceptions.Timeout:
        return None, (
            f"Request Timeout Error:\n"
            f"  -> The request timed out after {timeout} seconds.\n"
            "  -> The server may be slow or temporarily unreachable. Please retry."
        )
        
    except requests.exceptions.RequestException as e:
        return None, f"An unexpected request error occurred: {str(e)}"
        
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"


def parse_weather_data(data: dict) -> dict:
    """
    Extracts and organizes key weather details from the raw OpenWeatherMap JSON response.
    
    Args:
        data (dict): JSON response from OpenWeatherMap.
        
    Returns:
        dict: Clean dictionary with formatted weather attributes.
    """
    # 1. City & Country
    city = data.get("name", "Unknown City")
    country = data.get("sys", {}).get("country", "")
    location_display = f"{city}, {country}" if country else city
    
    # 2. Coordinates
    coord = data.get("coord", {})
    lat = coord.get("lat", "N/A")
    lon = coord.get("lon", "N/A")
    
    # 3. Temperatures
    main_section = data.get("main", {})
    temp_c = float(main_section.get("temp", 0.0))
    temp_f = celsius_to_fahrenheit(temp_c)
    
    feels_c = float(main_section.get("feels_like", temp_c))
    feels_f = celsius_to_fahrenheit(feels_c)
    
    temp_min_c = float(main_section.get("temp_min", temp_c))
    temp_min_f = celsius_to_fahrenheit(temp_min_c)
    temp_max_c = float(main_section.get("temp_max", temp_c))
    temp_max_f = celsius_to_fahrenheit(temp_max_c)
    
    # 4. Humidity & Pressure
    humidity = main_section.get("humidity", 0)
    pressure = main_section.get("pressure", 0)
    
    # 5. Weather Condition
    weather_list = data.get("weather", [{}])
    weather_first = weather_list[0] if weather_list else {}
    condition_main = weather_first.get("main", "Unknown")
    condition_desc = weather_first.get("description", "").title()
    icon = get_weather_icon(condition_main)
    
    # 6. Wind Information
    wind_section = data.get("wind", {})
    wind_speed_ms = float(wind_section.get("speed", 0.0))
    wind_speed_kmh = round(wind_speed_ms * 3.6, 2)
    wind_speed_mph = round(wind_speed_ms * 2.23694, 2)
    
    # 7. Visibility
    visibility_m = data.get("visibility", None)
    if visibility_m is not None:
        visibility_km = round(visibility_m / 1000.0, 1)
        visibility_str = f"{visibility_km} km"
    else:
        visibility_str = "N/A"
        
    # 8. Sunrise and Sunset (adjusted for local city timezone)
    tz_offset = data.get("timezone", 0)
    sys_section = data.get("sys", {})
    sunrise_epoch = sys_section.get("sunrise")
    sunset_epoch = sys_section.get("sunset")
    
    sunrise_str = format_timestamp(sunrise_epoch, tz_offset) if sunrise_epoch else "N/A"
    sunset_str = format_timestamp(sunset_epoch, tz_offset) if sunset_epoch else "N/A"
    
    return {
        "location": location_display,
        "coordinates": f"Lat: {lat}, Lon: {lon}",
        "temp_c": f"{temp_c:.1f}°C",
        "temp_f": f"{temp_f:.1f}°F",
        "feels_c": f"{feels_c:.1f}°C",
        "feels_f": f"{feels_f:.1f}°F",
        "min_temp": f"{temp_min_c:.1f}°C / {temp_min_f:.1f}°F",
        "max_temp": f"{temp_max_c:.1f}°C / {temp_max_f:.1f}°F",
        "humidity": f"{humidity}%",
        "pressure": f"{pressure} hPa",
        "condition": condition_main,
        "description": condition_desc,
        "icon": icon,
        "wind_speed_ms": f"{wind_speed_ms:.2f} m/s",
        "wind_speed_kmh": f"{wind_speed_kmh} km/h",
        "wind_speed_mph": f"{wind_speed_mph} mph",
        "visibility": visibility_str,
        "sunrise": sunrise_str,
        "sunset": sunset_str,
    }


def display_weather(info: dict):
    """
    Displays the weather information in a clean, aesthetically formatted command-line card.
    
    Args:
        info (dict): Parsed weather details from parse_weather_data().
    """
    card_width = 64
    border = "+" + "-" * (card_width - 2) + "+"
    sep = "|" + "-" * (card_width - 2) + "|"
    
    header_text = f"|  {info['icon']}  WEATHER REPORT: {info['location']}"
    # Header line with proper spacing
    if len(header_text) < card_width - 1:
        header_line = header_text + " " * (card_width - 1 - len(header_text)) + "|"
    else:
        header_line = header_text + " |"

    print()
    print(border)
    print(header_line)
    print(sep)
    
    items = [
        ("Weather Condition", f"{info['description']} ({info['condition']})"),
        ("Temperature", f"{info['temp_c']} / {info['temp_f']}"),
        ("Feels Like", f"{info['feels_c']} / {info['feels_f']}"),
        ("Min / Max Temp", info["min_temp"]),
        ("Humidity", info["humidity"]),
        ("Wind Speed", f"{info['wind_speed_kmh']} ({info['wind_speed_mph']})"),
        ("Atmospheric Press.", info["pressure"]),
        ("Visibility", info["visibility"]),
        ("Sunrise / Sunset", f"{info['sunrise']} / {info['sunset']}"),
    ]
    
    for label, val in items:
        content = f"|  {label:<19} : {val}"
        if len(content) < card_width - 1:
            line = content + " " * (card_width - 1 - len(content)) + "|"
        else:
            line = content + " |"
        print(line)
        
    print(border)
    print()


def display_banner():
    """Prints the application banner and introductory instructions."""
    banner = r"""
==========================================================
        OASIS INFOBYTE - PYTHON PROGRAMMING INTERNSHIP
                TASK 4: BASIC WEATHER APP
==========================================================
    Powered by OpenWeatherMap API | Beginner Tier
==========================================================
"""
    print(banner)


def display_help():
    """Prints helpful hints on supported search queries."""
    print("Tip: You can search by:")
    print("  * City Name           -> e.g., Tokyo, London, Mumbai, New York")
    print("  * City, Country Code  -> e.g., Paris, FR or Sydney, AU")
    print("  * US ZIP Code         -> e.g., 90210 or 10001")
    print("  * Int'l ZIP, Country  -> e.g., 110001,IN or SW1A,GB")
    print("  * Type 'exit' or 'q'  -> Exit the application anytime\n")


def display_api_key_guide():
    """Prints instructions on how to set up the OpenWeatherMap API key."""
    print("=" * 60)
    print("⚠️  MISSING OR DEFAULT API KEY DETECTED")
    print("=" * 60)
    print("To fetch real-time weather, you need a free OpenWeatherMap API key.")
    print("\nHow to set up your API Key in 3 easy steps:")
    print("  1. Visit: https://openweathermap.org/ and sign up for a FREE account.")
    print("  2. Go to your Profile -> 'My API Keys' and copy your 32-character key.")
    print("  3. Open the '.env' file in this folder and paste your key:")
    print("         OPENWEATHER_API_KEY=your_actual_api_key_here")
    print("\nNote: New OpenWeatherMap keys typically activate within 10-15 minutes.")
    print("=" * 60)
    print()


def ask_to_continue() -> bool:
    """
    Asks the user whether they want to search for another city.
    
    Returns:
        bool: True if the user wants to continue, False if they want to exit.
    """
    while True:
        choice = input("Would you like to check another city? (y/n): ").strip().lower()
        if choice in ("y", "yes"):
            return True
        elif choice in ("n", "no", "exit", "quit", "q"):
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def main():
    """
    Main driver function for the Weather Application.
    Runs the interactive CLI loop.
    """
    display_banner()
    
    # 1. Load API Key
    api_key = load_api_key()
    
    # Check if key is missing or still the default placeholder
    placeholder_values = ["", "your_api_key_here", "your_actual_api_key_here", "YOUR_OPENWEATHERMAP_API_KEY"]
    if not api_key or api_key in placeholder_values:
        display_api_key_guide()
        # Offer user the option to enter key interactively in the terminal
        prompt_key = input("Enter your OpenWeatherMap API Key now (or press Enter to exit): ").strip()
        if not prompt_key or prompt_key in placeholder_values:
            print("\nNo valid API key provided. Exiting application. Goodbye!")
            sys.exit(0)
        api_key = prompt_key
        # Update .env file for the user's convenience
        try:
            with open(".env", "w", encoding="utf-8") as env_file:
                env_file.write(f"# OpenWeatherMap API Configuration\nOPENWEATHER_API_KEY={api_key}\n")
            print("✓ Saved your API key to .env for future sessions!\n")
        except Exception:
            pass

    display_help()
    
    # 2. Main Interactive Loop
    while True:
        try:
            # Mandatory Feature 1: Ask user for city name or ZIP code
            user_input = input("Enter City Name or ZIP Code: ").strip()
            
            # Check for exit command
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nThank you for using the Weather App! Have a great day! 👋")
                break
                
            # Mandatory Feature 1: Reject empty input
            if not user_input:
                print("❌ Input cannot be empty! Please enter a valid city name or ZIP code.\n")
                continue
                
            print(f"\n🔍 Fetching real-time weather for '{user_input}'...")
            
            # Mandatory Feature 2: Fetch and parse data from OpenWeatherMap API
            raw_data, error_message = fetch_weather(user_input, api_key)
            
            # Mandatory Feature 4: Graceful Error Handling
            if error_message:
                print("\n" + "-" * 56)
                print(f"❌ {error_message}")
                print("-" * 56 + "\n")
            else:
                # Mandatory Feature 3: Parse and Display Weather Information
                parsed_weather = parse_weather_data(raw_data)
                display_weather(parsed_weather)
                
            # Mandatory Feature 5: Ask user whether they want to check another city
            if not ask_to_continue():
                print("\nThank you for using the Weather App! Have a great day! 👋")
                break
            print()
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully without a messy stack trace
            print("\n\nOperation cancelled by user. Exiting safely. Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ An unexpected error occurred in the application: {e}\n")


if __name__ == "__main__":
    main()
