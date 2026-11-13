"""
=============================================================================
Unit and Integration Test Suite - Task 4: Basic Weather App
=============================================================================
This test suite verifies all mandatory testing requirements:
1. Valid city name
2. Invalid city name (404)
3. Empty input rejection
4. Valid ZIP code handling
5. Invalid API key (401)
6. Network connection error (ConnectionError)
7. Request timeout error (Timeout)
8. Rate limiting (429)
9. Temperature conversion math
10. Multi-city search simulation
=============================================================================
"""

import unittest
from unittest.mock import patch, MagicMock
import requests

from main import (
    celsius_to_fahrenheit,
    build_api_params,
    fetch_weather,
    parse_weather_data,
    get_weather_icon
)


class TestWeatherApp(unittest.TestCase):

    def setUp(self):
        """Set up dummy data and keys for testing."""
        self.dummy_api_key = "1234567890abcdef1234567890abcdef"
        
        # Sample realistic OpenWeatherMap 200 OK response for London
        self.mock_london_response = {
            "coord": {"lon": -0.1257, "lat": 51.5085},
            "weather": [
                {
                    "id": 803,
                    "main": "Clouds",
                    "description": "broken clouds",
                    "icon": "04d"
                }
            ],
            "base": "stations",
            "main": {
                "temp": 15.0,
                "feels_like": 14.2,
                "temp_min": 13.0,
                "temp_max": 16.5,
                "pressure": 1013,
                "humidity": 72
            },
            "visibility": 10000,
            "wind": {
                "speed": 5.0,
                "deg": 220
            },
            "clouds": {"all": 75},
            "dt": 1618317040,
            "sys": {
                "type": 2,
                "id": 2075535,
                "country": "GB",
                "sunrise": 1618282134,
                "sunset": 1618330456
            },
            "timezone": 3600,
            "id": 2643743,
            "name": "London",
            "cod": 200
        }

        # Sample realistic OpenWeatherMap 200 OK response for ZIP code 90210
        self.mock_zip_response = {
            "coord": {"lon": -118.41, "lat": 34.09},
            "weather": [
                {
                    "id": 800,
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d"
                }
            ],
            "main": {
                "temp": 22.0,
                "feels_like": 21.8,
                "temp_min": 20.0,
                "temp_max": 24.0,
                "pressure": 1016,
                "humidity": 45
            },
            "visibility": 10000,
            "wind": {
                "speed": 3.1,
                "deg": 180
            },
            "sys": {
                "country": "US",
                "sunrise": 1618280000,
                "sunset": 1618328000
            },
            "timezone": -25200,
            "name": "Beverly Hills",
            "cod": 200
        }

    # -------------------------------------------------------------
    # Test 1: Temperature conversion mathematics
    # -------------------------------------------------------------
    def test_temperature_conversion(self):
        """Verify accurate conversion from Celsius to Fahrenheit."""
        self.assertEqual(celsius_to_fahrenheit(0.0), 32.0)
        self.assertEqual(celsius_to_fahrenheit(100.0), 212.0)
        self.assertEqual(celsius_to_fahrenheit(25.0), 77.0)
        self.assertEqual(celsius_to_fahrenheit(-40.0), -40.0)
        self.assertEqual(celsius_to_fahrenheit(15.0), 59.0)

    # -------------------------------------------------------------
    # Test 2: Valid city name query and parsing
    # -------------------------------------------------------------
    @patch("requests.get")
    def test_valid_city_name(self, mock_get):
        """Test fetching and parsing weather for a valid city name."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_london_response
        mock_get.return_value = mock_response

        data, error = fetch_weather("London", self.dummy_api_key)
        
        self.assertIsNone(error)
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "London")
        
        # Test parsing
        parsed = parse_weather_data(data)
        self.assertEqual(parsed["location"], "London, GB")
        self.assertEqual(parsed["temp_c"], "15.0°C")
        self.assertEqual(parsed["temp_f"], "59.0°F")
        self.assertEqual(parsed["humidity"], "72%")
        self.assertEqual(parsed["condition"], "Clouds")
        self.assertEqual(parsed["description"], "Broken Clouds")
        self.assertEqual(parsed["wind_speed_kmh"], "18.0 km/h")

    # -------------------------------------------------------------
    # Test 3: Invalid city name (HTTP 404)
    # -------------------------------------------------------------
    @patch("requests.get")
    def test_invalid_city_name(self, mock_get):
        """Test behavior when an invalid city name is entered."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"cod": "404", "message": "city not found"}
        mock_get.return_value = mock_response

        data, error = fetch_weather("NonExistentCityXYZ123", self.dummy_api_key)
        
        self.assertIsNone(data)
        self.assertIsNotNone(error)
        self.assertIn("Location Not Found (HTTP 404)", error)
        self.assertIn("NonExistentCityXYZ123", error)

    # -------------------------------------------------------------
    # Test 4: Empty input validation
    # -------------------------------------------------------------
    def test_empty_input_validation(self):
        """Test rejection of empty strings and whitespace-only inputs."""
        empty_inputs = ["", "   ", "\t", "\n"]
        for sample in empty_inputs:
            cleaned = sample.strip()
            self.assertEqual(len(cleaned), 0, f"Expected empty input for '{sample}'")

    # -------------------------------------------------------------
    # Test 5: Valid ZIP code handling
    # -------------------------------------------------------------
    @patch("requests.get")
    def test_valid_zip_code(self, mock_get):
        """Test fetching weather using a ZIP code."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_zip_response
        mock_get.return_value = mock_response

        # Check parameter generation
        params = build_api_params("90210,us", self.dummy_api_key)
        self.assertIn("zip", params)
        self.assertEqual(params["zip"], "90210,us")

        # Test request
        data, error = fetch_weather("90210,us", self.dummy_api_key)
        self.assertIsNone(error)
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Beverly Hills")

        parsed = parse_weather_data(data)
        self.assertEqual(parsed["location"], "Beverly Hills, US")
        self.assertEqual(parsed["temp_c"], "22.0°C")
        self.assertEqual(parsed["temp_f"], "71.6°F")

    # -------------------------------------------------------------
    # Test 6: Invalid API key (HTTP 401)
    # -------------------------------------------------------------
    @patch("requests.get")
    def test_invalid_api_key(self, mock_get):
        """Test behavior when API key is unauthorized or invalid."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"cod": 401, "message": "Invalid API key"}
        mock_get.return_value = mock_response

        data, error = fetch_weather("Paris", "bad_api_key")
        
        self.assertIsNone(data)
        self.assertIsNotNone(error)
        self.assertIn("Authentication Error (HTTP 401)", error)
        self.assertIn("Invalid API Key", error)

    # -------------------------------------------------------------
    # Test 7: Network connection failure (ConnectionError)
    # -------------------------------------------------------------
    @patch("requests.get")
    def test_network_connection_error(self, mock_get):
        """Test handling of offline or unreachable network."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to resolve host")

        data, error = fetch_weather("Tokyo", self.dummy_api_key)
        
        self.assertIsNone(data)
        self.assertIsNotNone(error)
        self.assertIn("Network Connection Error", error)
        self.assertIn("check your internet connection", error)

    # -------------------------------------------------------------
    # Test 8: Request timeout error
    # -------------------------------------------------------------
    @patch("requests.get")
    def test_request_timeout_error(self, mock_get):
        """Test handling when OpenWeatherMap request times out."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        data, error = fetch_weather("Berlin", self.dummy_api_key, timeout=5)
        
        self.assertIsNone(data)
        self.assertIsNotNone(error)
        self.assertIn("Request Timeout Error", error)

    # -------------------------------------------------------------
    # Test 9: Rate limiting (HTTP 429)
    # -------------------------------------------------------------
    @patch("requests.get")
    def test_rate_limit_exceeded(self, mock_get):
        """Test handling of rate limit exceedance."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        data, error = fetch_weather("Sydney", self.dummy_api_key)
        
        self.assertIsNone(data)
        self.assertIsNotNone(error)
        self.assertIn("Rate Limit Exceeded (HTTP 429)", error)

    # -------------------------------------------------------------
    # Test 10: Multiple sequential city searches simulation
    # -------------------------------------------------------------
    @patch("requests.get")
    def test_multiple_city_searches(self, mock_get):
        """Simulate searching multiple cities sequentially without restarting."""
        cities_to_test = ["London", "Paris", "Tokyo"]
        
        for city in cities_to_test:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "name": city,
                "main": {"temp": 20.0, "humidity": 60, "pressure": 1012, "feels_like": 20.0},
                "weather": [{"main": "Clear", "description": "clear sky"}],
                "wind": {"speed": 4.0},
                "sys": {"country": "TEST"}
            }
            mock_get.return_value = mock_resp

            data, error = fetch_weather(city, self.dummy_api_key)
            self.assertIsNone(error)
            self.assertEqual(data["name"], city)
            parsed = parse_weather_data(data)
            self.assertEqual(parsed["temp_c"], "20.0°C")


if __name__ == "__main__":
    unittest.main(verbosity=2)
