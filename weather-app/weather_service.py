import requests
from typing import Dict, Tuple, Optional


class WeatherServiceError(Exception):
    """Base exception for weather service errors."""
    pass


class LocationNotFoundError(WeatherServiceError):
    """Raised when location cannot be found."""
    pass


class APIError(WeatherServiceError):
    """Raised when API returns an error."""
    pass


class NetworkError(WeatherServiceError):
    """Raised when network error occurs."""
    pass


class OfflineError(NetworkError):
    """
    Raised specifically when the internet is unavailable (no connection
    could be made to the weather API).

    It inherits from NetworkError, so existing code that catches
    NetworkError still works.
    """
    pass


class WeatherService:
    """
    Weather service using Open-Meteo API (free, no API key required).
    """
    
    GEOCODE_BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @staticmethod
    def _network_error(exc: Exception) -> NetworkError:
        """
        Convert a low-level requests exception into a friendly NetworkError.

        This is what lets the app show a clear, human-readable message when
        the internet is unavailable instead of a technical traceback.
        """
        if isinstance(exc, requests.exceptions.Timeout):
            return NetworkError(
                "The weather service took too long to respond. "
                "Please check your internet connection and try again."
            )
        if isinstance(exc, requests.exceptions.ConnectionError):
            return OfflineError(
                "No internet connection. Please connect to the internet and try again."
            )
        return NetworkError(
            "A network error occurred. Please check your internet connection and try again."
        )
    
    def get_coordinates(self, city_name: str) -> Tuple[float, float, str]:
        """
        Get latitude, longitude, and location name from city name.
        
        Args:
            city_name: Name of city or village
            
        Returns:
            Tuple of (latitude, longitude, full_location_name)
            
        Raises:
            LocationNotFoundError: If location not found
            APIError: If API returns error
            NetworkError: If network error occurs
        """
        if not city_name or not city_name.strip():
            raise LocationNotFoundError("Please enter a city or village name")
        
        params = {
            "name": city_name.strip(),
            "count": 10,
            "language": "en",
            "format": "json"
        }
        
        try:
            response = requests.get(self.GEOCODE_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                raise LocationNotFoundError(f"Location '{city_name}' not found in India. Please enter an Indian city or village.")
            
            # Only allow Indian locations
            results = [r for r in data["results"] if r.get("country_code") == "IN"]
            
            if not results:
                raise LocationNotFoundError(f"Location '{city_name}' not found in India. Please enter an Indian city or village.")
            
            result = results[0]
            lat = result["latitude"]
            lon = result["longitude"]
            name = result.get("name", city_name)
            admin1 = result.get("admin1", "")
            
            # Build full location name
            parts = [name]
            if admin1:
                parts.append(admin1)
            parts.append("India")
            full_location = ", ".join(parts)
            
            return lat, lon, full_location
            
        except requests.exceptions.HTTPError:
            raise APIError("Geocoding API error. Please try again later.")
        except requests.exceptions.RequestException as e:
            raise self._network_error(e)
        except (KeyError, IndexError, ValueError):
            raise APIError("Invalid response from geocoding API.")
    
    def get_weather(self, lat: float, lon: float) -> Dict:
        """
        Get current weather from coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary containing weather data
            
        Raises:
            APIError: If API returns error
            NetworkError: If network error occurs
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
                "precipitation",
                "rain"
            ],
            "forecast_days": 1,
            "timezone": "auto"
        }
        
        try:
            response = requests.get(self.WEATHER_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data
            
        except requests.exceptions.HTTPError:
            raise APIError("Weather API error. Please try again later.")
        except requests.exceptions.RequestException as e:
            raise self._network_error(e)
        except (KeyError, ValueError):
            raise APIError("Invalid response from weather API.")
    
    def get_current_weather(self, city_name: str) -> Dict:
        """
        Get complete current weather information for a city.
        
        Args:
            city_name: Name of city or village
            
        Returns:
            Dictionary with weather information
            
        Raises:
            LocationNotFoundError, APIError, NetworkError
        """
        # Get coordinates
        lat, lon, location = self.get_coordinates(city_name)
        
        # Get weather data
        weather_data = self.get_weather(lat, lon)
        
        # Parse current weather
        current = weather_data.get("current", {})
        units = weather_data.get("current_units", {})
        
        # Weather code mapping (WMO codes)
        weather_code_map = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        
        weather_code = current.get("weather_code", 0)
        weather_condition = weather_code_map.get(weather_code, "Unknown")
        
        # Get rain status
        rain = current.get("rain", 0) or current.get("precipitation", 0) or 0
        if rain > 0:
            rain_status = f"Raining ({rain} {units.get('rain', 'mm')})"
        else:
            rain_status = "No rain"
        
        # Check for rain timing - Open-Meteo doesn't provide specific timing for current/next hour in simple form
        # So we'll show the message as specified
        rain_timing = "Rain timing information is not available."
        
        result = {
            "location": location,
            "temperature": f"{current.get('temperature_2m', 'N/A')} {units.get('temperature_2m', '°C')}",
            "weather_condition": weather_condition,
            "humidity": f"{current.get('relative_humidity_2m', 'N/A')} {units.get('relative_humidity_2m', '%')}",
            "wind_speed": f"{current.get('wind_speed_10m', 'N/A')} {units.get('wind_speed_10m', 'km/h')}",
            "rain_status": rain_status,
            "rain_timing": rain_timing
        }
        
        return result
