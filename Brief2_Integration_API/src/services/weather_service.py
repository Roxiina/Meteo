"""
Weather Service for Open-Meteo Weather Forecast API.

This service handles all interactions with the Weather Forecast API,
including current weather and forecasts.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..utils.api_client import APIClient
from ..utils.error_handler import ValidationError, DataNotFoundError
from ..config.settings import settings

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service for retrieving weather data from Open-Meteo Weather Forecast API.
    
    Features:
    - Get current weather conditions
    - Get weather forecasts (up to 16 days)
    - Temperature, pressure, wind speed data
    - Automatic validation and parsing
    """
    
    def __init__(self, api_client: Optional[APIClient] = None):
        """
        Initialize Weather Service.
        
        Args:
            api_client: Optional custom API client (default: new APIClient)
        """
        self.api_client = api_client or APIClient()
        self.base_url = settings.WEATHER_API_URL
        logger.info(f"WeatherService initialized with URL: {self.base_url}")
    
    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            latitude: Latitude (-90 to 90)
            longitude: Longitude (-180 to 180)
            forecast_days: Number of forecast days (1-16, default: 7)
        
        Returns:
            Dictionary with forecast data:
            {
                "location": {"latitude": float, "longitude": float},
                "forecast": [
                    {
                        "date": str,
                        "temperature_2m_max": float,
                        "temperature_2m_min": float,
                        "surface_pressure": float,
                        "wind_speed_10m_max": float
                    },
                    ...
                ]
            }
        
        Raises:
            ValidationError: If parameters are invalid
            DataNotFoundError: If required data is missing from response
        """
        # Validate parameters
        self._validate_coordinates(latitude, longitude)
        self._validate_forecast_days(forecast_days)
        
        # Build request parameters
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": forecast_days,
            "daily": "temperature_2m_max,temperature_2m_min,surface_pressure,wind_speed_10m_max",
            "timezone": "auto"
        }
        
        logger.info(
            f"Fetching weather forecast for ({latitude}, {longitude}), "
            f"{forecast_days} days"
        )
        
        # Make API call
        response = self.api_client.get(self.base_url, params=params)
        
        # Parse and validate response
        forecast_data = self._parse_forecast_response(response, latitude, longitude)
        
        logger.info(f"Successfully fetched {len(forecast_data['forecast'])} days of forecast")
        
        return forecast_data
    
    def get_current_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get current weather conditions for a location.
        
        Args:
            latitude: Latitude (-90 to 90)
            longitude: Longitude (-180 to 180)
        
        Returns:
            Dictionary with current weather:
            {
                "location": {"latitude": float, "longitude": float},
                "current": {
                    "time": str,
                    "temperature_2m": float,
                    "surface_pressure": float,
                    "wind_speed_10m": float
                }
            }
        
        Raises:
            ValidationError: If coordinates are invalid
            DataNotFoundError: If required data is missing
        """
        # Validate coordinates
        self._validate_coordinates(latitude, longitude)
        
        # Build request parameters
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,surface_pressure,wind_speed_10m",
            "timezone": "auto"
        }
        
        logger.info(f"Fetching current weather for ({latitude}, {longitude})")
        
        # Make API call
        response = self.api_client.get(self.base_url, params=params)
        
        # Parse and validate response
        current_data = self._parse_current_response(response, latitude, longitude)
        
        logger.info("Successfully fetched current weather")
        
        return current_data
    
    def _validate_coordinates(self, latitude: float, longitude: float):
        """
        Validate geographic coordinates.
        
        Args:
            latitude: Latitude to validate
            longitude: Longitude to validate
        
        Raises:
            ValidationError: If coordinates are out of bounds
        """
        if not isinstance(latitude, (int, float)):
            raise ValidationError(
                f"Latitude must be a number, got: {type(latitude).__name__}"
            )
        
        if not isinstance(longitude, (int, float)):
            raise ValidationError(
                f"Longitude must be a number, got: {type(longitude).__name__}"
            )
        
        if not -90 <= latitude <= 90:
            raise ValidationError(
                f"Latitude must be between -90 and 90, got: {latitude}"
            )
        
        if not -180 <= longitude <= 180:
            raise ValidationError(
                f"Longitude must be between -180 and 180, got: {longitude}"
            )
    
    def _validate_forecast_days(self, forecast_days: int):
        """
        Validate forecast_days parameter.
        
        Args:
            forecast_days: Number of forecast days
        
        Raises:
            ValidationError: If forecast_days is out of range
        """
        if not isinstance(forecast_days, int):
            raise ValidationError(
                f"forecast_days must be an integer, got: {type(forecast_days).__name__}"
            )
        
        if not 1 <= forecast_days <= 16:
            raise ValidationError(
                f"forecast_days must be between 1 and 16, got: {forecast_days}"
            )
    
    def _parse_forecast_response(
        self,
        response: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse and validate forecast API response.
        
        Args:
            response: Raw API response
            latitude: Request latitude
            longitude: Request longitude
        
        Returns:
            Parsed forecast data
        
        Raises:
            DataNotFoundError: If required fields are missing
        """
        try:
            daily = response["daily"]
            
            # Verify all required fields are present
            required_fields = [
                "time",
                "temperature_2m_max",
                "temperature_2m_min",
                "surface_pressure",
                "wind_speed_10m_max"
            ]
            
            for field in required_fields:
                if field not in daily:
                    raise DataNotFoundError(f"Missing field in response: {field}")
            
            # Build forecast list
            forecast_list = []
            for i in range(len(daily["time"])):
                forecast_list.append({
                    "date": daily["time"][i],
                    "temperature_2m_max": daily["temperature_2m_max"][i],
                    "temperature_2m_min": daily["temperature_2m_min"][i],
                    "surface_pressure": daily["surface_pressure"][i],
                    "wind_speed_10m_max": daily["wind_speed_10m_max"][i]
                })
            
            return {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "forecast": forecast_list
            }
        
        except KeyError as e:
            raise DataNotFoundError(f"Missing required field in response: {e}")
        except (IndexError, TypeError) as e:
            raise DataNotFoundError(f"Invalid response structure: {e}")
    
    def _parse_current_response(
        self,
        response: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse and validate current weather API response.
        
        Args:
            response: Raw API response
            latitude: Request latitude
            longitude: Request longitude
        
        Returns:
            Parsed current weather data
        
        Raises:
            DataNotFoundError: If required fields are missing
        """
        try:
            current = response["current"]
            
            # Verify required fields
            required_fields = [
                "time",
                "temperature_2m",
                "surface_pressure",
                "wind_speed_10m"
            ]
            
            for field in required_fields:
                if field not in current:
                    raise DataNotFoundError(f"Missing field in response: {field}")
            
            return {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "current": {
                    "time": current["time"],
                    "temperature_2m": current["temperature_2m"],
                    "surface_pressure": current["surface_pressure"],
                    "wind_speed_10m": current["wind_speed_10m"]
                }
            }
        
        except KeyError as e:
            raise DataNotFoundError(f"Missing required field in response: {e}")
        except TypeError as e:
            raise DataNotFoundError(f"Invalid response structure: {e}")
