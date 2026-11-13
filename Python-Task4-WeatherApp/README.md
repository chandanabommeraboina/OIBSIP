# Oasis Infobyte - Python Programming Internship
## Task 4: Basic Weather App (Beginner Tier)

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Completed-success.svg)
![API](https://img.shields.io/badge/API-OpenWeatherMap-orange.svg)

A clean, reliable, beginner-friendly Command-Line Weather Application built in Python. This project connects to the **OpenWeatherMap REST API**, fetches real-time meteorological data for any specified city or ZIP code, parses the JSON response, and presents the weather in an organized, beautiful terminal interface.

---

## 📋 Table of Contents
1. [Project Overview & Objective](#-project-overview--objective)
2. [Key Features](#-key-features)
3. [Technologies Used](#-technologies-used)
4. [Project Structure](#-project-structure)
5. [OpenWeatherMap API Setup](#-openweathermap-api-setup)
6. [Installation & Requirements](#-installation--requirements)
7. [How to Run the Application](#-how-to-run-the-application)
8. [Example CLI Output](#-example-cli-output)
9. [Error Handling & Edge Cases](#-error-handling--edge-cases)
10. [Automated Testing Suite](#-automated-testing-suite)
11. [Beginner's Technical Guide](#-beginners-technical-guide)
12. [Screenshots](#-screenshots)
13. [Future Enhancements](#-future-enhancements)
14. [Submission & Internship Checklist](#-submission--internship-checklist)

---

## 🎯 Project Overview & Objective

### Objective
To build a functional command-line weather application using Python that interacts with an external web API (OpenWeatherMap), processes JSON data, and handles user interactions and network anomalies gracefully without crashing.

### Target Tier: Beginner
- Utilizes Python's standard libraries alongside standard networking packages (`requests`, `python-dotenv`).
- Structured with modular functions, clear docstrings, and comprehensive comments.
- Adheres to security best practices by strictly isolating secrets (API keys) in environment variables.

---

## ✨ Key Features

- **Flexible Location Input:** Supports queries by City Name (e.g., `London`, `Tokyo`), City + Country Code (e.g., `Paris, FR`, `Mumbai, IN`), and postal/ZIP codes (e.g., `90210, US`, `110001, IN`).
- **Input Validation:** Automatically detects and rejects empty or whitespace-only inputs with immediate feedback.
- **Dual Temperature Units:** Automatically displays temperatures in both **Celsius (°C)** and **Fahrenheit (°F)**.
- **Rich Weather Metrics:**
  - City and Country Code
  - Weather condition category and descriptive summary (e.g., `Broken Clouds`, `Clear Sky`)
  - Real-time temperature & "Feels Like" temperature
  - Day's minimum and maximum recorded temperatures
  - Atmospheric humidity percentage (%)
  - Atmospheric pressure in hectopascals (hPa)
  - Wind speed in both **km/h** and **mph**
  - Atmospheric visibility distance (km)
  - Local sunrise and sunset times adjusted for the city's timezone offset
- **Continuous Session Loop:** Allows searching for multiple locations sequentially without needing to restart the script.
- **Graceful Error Handling:** Catches connection issues, API timeouts, invalid cities (404), unauthorized API keys (401), and rate limits (429).
- **Safe Exit & Signal Trapping:** Supports clean exit via `exit`, `quit`, `q`, or `Ctrl+C` (`KeyboardInterrupt`).

---

## 🛠️ Technologies Used

| Technology | Purpose |
| :--- | :--- |
| **Python 3.8+** | Core programming language |
| **requests** | Performing HTTP GET requests to the external REST API |
| **json** | Parsing and formatting data payloads |
| **python-dotenv** | Loading environment variables securely from `.env` |
| **datetime & timezone** | Converting Unix epoch timestamps into human-readable local times |
| **unittest & unittest.mock**| Comprehensive test suite verifying all required scenarios |

---

## 📁 Project Structure

```text
OIBSIP/Python-Task4-WeatherApp/
│
├── WeatherApp/
│   ├── main.py              # Main application entry point & interactive loop
│   ├── test_weather.py      # Automated unit and integration test suite
│   ├── requirements.txt     # Python package dependencies
│   ├── .env.example         # Template for environment variables (safe for Git)
│   ├── .env                 # Local API key file (ignored by Git)
│   ├── .gitignore           # Excludes .env, pycache, and virtual environments
│   └── README.md            # Comprehensive project documentation
```

---

## 🔑 OpenWeatherMap API Setup

This application uses the **Current Weather Data API** provided by OpenWeatherMap on the Free tier.

### Step 1: Create a Free Account
1. Visit [https://openweathermap.org/](https://openweathermap.org/).
2. Click on **Sign In** in the top navigation bar, then select **Create an Account**.
3. Fill in your email and password, agree to the terms, and confirm your email address.

### Step 2: Obtain your API Key
1. Once logged in, click your username in the top right corner and choose **My API Keys**.
2. You will find a default API key or you can generate a new one under a custom name (e.g., `WeatherAppKey`).
3. Copy the 32-character hexadecimal key (e.g., `a1b2c3d4e5f678901234567890abcdef`).

> [!NOTE]
> Newly generated OpenWeatherMap API keys typically require **10 to 15 minutes** to activate on OpenWeatherMap's global servers. If you encounter an HTTP 401 error right after signup, please wait a few minutes and try again.

### Step 3: Secure Your Key in `.env`
1. Duplicate `.env.example` and name the copy `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in your text editor and paste your key:
   ```env
   OPENWEATHER_API_KEY=a1b2c3d4e5f678901234567890abcdef
   ```
3. Verify that `.gitignore` contains `.env` so your secret key is **never** committed to a public Git repository.

---

## ⚙️ Installation & Requirements

### 1. Clone or Open the Repository
```bash
git clone https://github.com/<your-username>/OIBSIP.git
cd OIBSIP/Python-Task4-WeatherApp/WeatherApp
```

### 2. (Optional but Recommended) Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Application

Execute `main.py` using Python:

```bash
# Windows
python main.py

# macOS / Linux
python3 main.py
```

### Usage Guide
When prompted:
- **Search by City Name:** Type `London`, `Tokyo`, or `Chicago`.
- **Search by City and Country:** Type `Paris, FR` or `Sydney, AU` for specific regional accuracy.
- **Search by US ZIP Code:** Type `90210` or `10001`.
- **Search by International Postal Code:** Type `110001,IN` or `SW1A,GB`.
- **Exit anytime:** Type `q`, `quit`, or `exit`.

---

## 🖥️ Example CLI Output

### 1. Valid City Query (Tokyo, JP)
```text
==========================================================
        OASIS INFOBYTE - PYTHON PROGRAMMING INTERNSHIP
                TASK 4: BASIC WEATHER APP
==========================================================
    Powered by OpenWeatherMap API | Beginner Tier
==========================================================

Tip: You can search by:
  * City Name           -> e.g., Tokyo, London, Mumbai, New York
  * City, Country Code  -> e.g., Paris, FR or Sydney, AU
  * US ZIP Code         -> e.g., 90210 or 10001
  * Int'l ZIP, Country  -> e.g., 110001,IN or SW1A,GB
  * Type 'exit' or 'q'  -> Exit the application anytime

Enter City Name or ZIP Code: Tokyo

🔍 Fetching real-time weather for 'Tokyo'...

+--------------------------------------------------------------+
|  [Sunny/Clear] ☀️  WEATHER REPORT: Tokyo, JP                  |
|--------------------------------------------------------------|
|  Weather Condition   : Clear Sky (Clear)                     |
|  Temperature         : 18.5°C / 65.3°F                       |
|  Feels Like          : 18.0°C / 64.4°F                       |
|  Min / Max Temp      : 17.0°C / 62.6°F to 20.0°C / 68.0°F    |
|  Humidity            : 65%                                   |
|  Wind Speed          : 11.52 km/h (7.16 mph)                 |
|  Atmospheric Press.  : 1015 hPa                              |
|  Visibility          : 10.0 km                               |
|  Sunrise / Sunset    : 06:14 AM / 05:22 PM                   |
+--------------------------------------------------------------+

Would you like to check another city? (y/n): 
```

### 2. Empty Input Handling
```text
Enter City Name or ZIP Code:    
❌ Input cannot be empty! Please enter a valid city name or ZIP code.
```

### 3. City Not Found (HTTP 404)
```text
Enter City Name or ZIP Code: AtlantisCityXYZ

🔍 Fetching real-time weather for 'AtlantisCityXYZ'...

--------------------------------------------------------
❌ Location Not Found (HTTP 404): Could not find weather for 'AtlantisCityXYZ'.
  -> Check the spelling of the city name.
  -> For non-US ZIP codes, specify the country code (e.g., '110001,IN').
  -> You can also search as: 'City, Country' (e.g., 'Tokyo, JP').
--------------------------------------------------------
```

---

## 🛡️ Error Handling & Edge Cases

The application handles every potential failure mode without crashing:

| Error Case | Root Cause | Application Handling |
| :--- | :--- | :--- |
| **Empty Input** | User presses Enter without entering characters | Rejects input immediately and re-prompts user |
| **City Not Found (404)** | Typo or invalid location query | Displays actionable suggestions (spelling, country codes) |
| **Invalid API Key (401)** | Missing, mistyped, or unactivated key | Alerts user to check `.env` and reminds of activation delay |
| **Rate Limit Exceeded (429)** | Exceeded 60 calls/minute limit | Informs user to pause briefly before retrying |
| **No Internet Connection** | Wi-Fi disconnected or DNS failure | Catches `requests.exceptions.ConnectionError` gracefully |
| **API Request Timeout** | Server unresponsive (>10 seconds) | Catches `requests.exceptions.Timeout` with retry suggestion |
| **Malformed JSON** | Non-JSON response from server | Catches `ValueError` / `JSONDecodeError` cleanly |
| **Missing .env File** | First-time setup | Shows interactive setup guide and allows inline key entry |
| **Keyboard Interrupt** | User presses `Ctrl+C` | Traps `KeyboardInterrupt` and exits with polite goodbye message |

---

## 🧪 Automated Testing Suite

A comprehensive test suite is included in `test_weather.py`. It uses Python's standard `unittest` framework and `unittest.mock` to simulate all network conditions deterministically.

### Running the Tests
```bash
python test_weather.py
```

### Verified Test Cases
```text
test_empty_input_validation (__main__.TestWeatherApp.test_empty_input_validation)
Test rejection of empty strings and whitespace-only inputs. ... ok
test_invalid_api_key (__main__.TestWeatherApp.test_invalid_api_key)
Test behavior when API key is unauthorized or invalid. ... ok
test_invalid_city_name (__main__.TestWeatherApp.test_invalid_city_name)
Test behavior when an invalid city name is entered. ... ok
test_multiple_city_searches (__main__.TestWeatherApp.test_multiple_city_searches)
Simulate searching multiple cities sequentially without restarting. ... ok
test_network_connection_error (__main__.TestWeatherApp.test_network_connection_error)
Test handling of offline or unreachable network. ... ok
test_rate_limit_exceeded (__main__.TestWeatherApp.test_rate_limit_exceeded)
Test handling of rate limit exceedance. ... ok
test_request_timeout_error (__main__.TestWeatherApp.test_request_timeout_error)
Test handling when OpenWeatherMap request times out. ... ok
test_temperature_conversion (__main__.TestWeatherApp.test_temperature_conversion)
Verify accurate conversion from Celsius to Fahrenheit. ... ok
test_valid_city_name (__main__.TestWeatherApp.test_valid_city_name)
Test fetching and parsing weather for a valid city name. ... ok
test_valid_zip_code (__main__.TestWeatherApp.test_valid_zip_code)
Test fetching weather using a ZIP code. ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.011s

OK
```

---

## 📖 Beginner's Technical Guide

If you are new to Python or web APIs, here is how the core concepts work:

### 1. What is an API?
An **API (Application Programming Interface)** acts as a messenger between your Python code and a remote server. Instead of scraping a web page visually, your program sends a structured request to OpenWeatherMap's servers, which reply with live weather data.

### 2. How `requests.get()` Works
The `requests` library simplifies HTTP communication in Python.
```python
import requests

# 1. We specify the server's endpoint URL
url = "https://api.openweathermap.org/data/2.5/weather"

# 2. We pass parameters in a dictionary
params = {
    "q": "London",
    "appid": "your_api_key",
    "units": "metric"
}

# 3. requests sends an HTTP GET request
response = requests.get(url, params=params, timeout=10)

# 4. Check the response status code (200 means Success)
if response.status_code == 200:
    data = response.json()  # Convert JSON string to Python dictionary
```

### 3. What is JSON?
**JSON (JavaScript Object Notation)** is a lightweight data interchange format. When OpenWeatherMap responds, it sends data as text formatted like a Python dictionary:
```json
{
  "name": "London",
  "main": {
    "temp": 15.0,
    "humidity": 72
  }
}
```
In Python, `response.json()` converts this text directly into native Python dictionaries and lists, allowing access like `data["main"]["temp"]`.

### 4. Why Use Environment Variables (`.env`)?
Never hardcode passwords, API keys, or private tokens inside your `.py` source files. If you push hardcoded keys to GitHub:
- Anyone can steal your API quota.
- Automated security bots will flag and revoke your key.
- It violates industry security best practices.

By placing keys in `.env` and adding `.env` to `.gitignore`, the key remains only on your local machine.

---

## 📸 Screenshots

> Place your application execution screenshots in this section before submitting to Oasis Infobyte.

| Scenario | Screenshot Preview |
| :--- | :--- |
| **Application Launch & City Search** | *(Insert screenshot of valid city weather output)* |
| **Error Handling (Invalid City / Key)** | *(Insert screenshot of 404 or missing key handling)* |
| **Unit Test Suite Execution** | *(Insert screenshot showing 10/10 tests passing)* |

---

## 🚀 Future Enhancements

- [ ] **5-Day / 3-Hour Forecast:** Extend API calls to OpenWeatherMap's `/forecast` endpoint to display upcoming weather trends.
- [ ] **Graphical User Interface (GUI):** Build a desktop interface using Tkinter or CustomTkinter.
- [ ] **Automatic Geolocation:** Detect user location using IP geolocation when no city is typed.
- [ ] **Audio Weather Announcements:** Integrate text-to-speech (`pyttsx3`) for audible weather briefings.
- [ ] **Historical Weather Comparison:** Compare today's weather with historical averages.

---

## 📋 Submission & Internship Checklist

- [x] Python 3 code is beginner-friendly and clean.
- [x] `requests` and `json` utilized effectively.
- [x] OpenWeatherMap Free API integrated.
- [x] City and ZIP code inputs supported.
- [x] Empty input rejected.
- [x] Continuous city search loop supported.
- [x] Temperatures displayed in both Celsius (°C) and Fahrenheit (°F).
- [x] Humidity, condition, wind speed, pressure, and visibility displayed.
- [x] Graceful error handling for 404, 401, 429, timeouts, and network failures.
- [x] API key protected using `.env` and `.gitignore`.
- [x] `.env.example` template provided.
- [x] Complete automated test suite (`test_weather.py`) passed 10/10.
- [x] Detailed README with documentation and beginner guide.

---

### Author & Internship Details
- **Internship:** Oasis Infobyte Python Programming Internship
- **Task:** Task 4 – Basic Weather App (Beginner Tier)
- **Repository Directory:** `OIBSIP/Python-Task4-WeatherApp/`
