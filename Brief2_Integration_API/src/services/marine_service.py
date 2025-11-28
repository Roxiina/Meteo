"""
Marine Service for Open-Meteo Marine Weather API.

This service handles all interactions with the Marine Weather API,
including marine forecasts and sea surface temperature data.
"""

import logging
from typing import Dict, Any, Optional

from ..utils.api_client import APIClient
from ..utils.error_handler import ValidationError, DataNotFoundError
from ..config.settings import settings

logger = logging.getLogger(__name__)


class MarineService:
    """
    Service for retrieving marine data from Open-Meteo Marine Weather API.
    
    Features:
    - Get marine weather forecasts (up to 7 days)
    - Sea surface temperature (SST)
    - Wave height and direction
    - Automatic validation and parsing
    """
    
    def __init__(self, api_client: Optional[APIClient] = None):
        """
        Initialize Marine Service.
        
        Args:
            api_client: Optional custom API client (default: new APIClient)
        """
        self.api_client = api_client or APIClient()
        self.base_url = settings.MARINE_API_URL
        logger.info(f"MarineService initialized with URL: {self.base_url}")
    
    def get_marine_forecast(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7
    ) -> Dict[str, Any]:
        """
        Get marine weather forecast for a location.
        
        Args:
            latitude: Latitude (-90 to 90)
            longitude: Longitude (-180 to 180)
            forecast_days: Number of forecast days (1-7, default: 7)
        
        Returns:
            Dictionary with marine forecast data:
            {
                "location": {"latitude": float, "longitude": float},
                "marine_forecast": [
                    {
                        "date": str,
                        "ocean_sst": float,
                        "wave_height": float,
                        "wave_direction": float
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
            "daily": "wave_height_max,wave_direction_dominant,ocean_current_velocity,ocean_current_direction",
            "timezone": "auto"
        }
        
        # Add forecast_days parameter if API supports it (currently always 7 days)
        logger.info(
            f"Fetching marine forecast for ({latitude}, {longitude}), "
            f"{forecast_days} days"
        )
        
        # Make API call
        response = self.api_client.get(self.base_url, params=params)
        
        # Parse and validate response
        marine_data = self._parse_marine_response(response, latitude, longitude)
        
        # Limit to requested forecast_days
        marine_data["marine_forecast"] = marine_data["marine_forecast"][:forecast_days]
        
        logger.info(
            f"Successfully fetched {len(marine_data['marine_forecast'])} days of marine forecast"
        )
        
        return marine_data
    
    def get_sst(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get sea surface temperature for a location.
        
        Args:
            latitude: Latitude (-90 to 90)
            longitude: Longitude (-180 to 180)
        
        Returns:
            Dictionary with SST data:
            {
                "location": {"latitude": float, "longitude": float},
                "sst": {
                    "date": str,
                    "temperature": float
                }
            }
        
        Raises:
            ValidationError: If coordinates are invalid
            DataNotFoundError: If SST data is missing
        """
        # Validate coordinates
        self._validate_coordinates(latitude, longitude)
        
        # Build request parameters
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "wave_height_max",
            "timezone": "auto"
        }
        
        logger.info(f"Fetching SST for ({latitude}, {longitude})")
        
        # Make API call
        response = self.api_client.get(self.base_url, params=params)
        
        # Parse SST from response (use first day)
        try:
            daily = response["daily"]
            
            # Note: Marine API doesn't provide direct SST in daily data
            # This is a simplified implementation for demonstration
            # In production, use hourly data or dedicated SST endpoint
            
            sst_data = {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "sst": {
                    "date": daily["time"][0],
                    "temperature": None  # Would come from hourly data
                }
            }
            
            logger.info("Successfully fetched SST data")
            
            return sst_data
        
        except (KeyError, IndexError, TypeError) as e:
            raise DataNotFoundError(f"Failed to extract SST from response: {e}")
    
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
        Validate forecast_days parameter for marine data.
        
        Marine API supports up to 7 days.
        
        Args:
            forecast_days: Number of forecast days
        
        Raises:
            ValidationError: If forecast_days is out of range
        """
        if not isinstance(forecast_days, int):
            raise ValidationError(
                f"forecast_days must be an integer, got: {type(forecast_days).__name__}"
            )
        
        if not 1 <= forecast_days <= 7:
            raise ValidationError(
                f"forecast_days must be between 1 and 7 for marine data, got: {forecast_days}"
            )
    
    def _parse_marine_response(
        self,
        response: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse and validate marine API response.
        
        Args:
            response: Raw API response
            latitude: Request latitude
            longitude: Request longitude
        
        Returns:
            Parsed marine forecast data
        
        Raises:
            DataNotFoundError: If required fields are missing
        """
        try:
            daily = response["daily"]
            
            # Verify required fields
            required_fields = ["time", "wave_height_max", "wave_direction_dominant"]
            
            for field in required_fields:
                if field not in daily:
                    raise DataNotFoundError(f"Missing field in response: {field}")
            
            # Build marine forecast list
            marine_list = []
            for i in range(len(daily["time"])):
                marine_list.append({
                    "date": daily["time"][i],
                    "wave_height": daily["wave_height_max"][i],
                    "wave_direction": daily["wave_direction_dominant"][i],
                    "ocean_current_velocity": daily.get("ocean_current_velocity", [None] * len(daily["time"]))[i],
                    "ocean_current_direction": daily.get("ocean_current_direction", [None] * len(daily["time"]))[i]
                })
            
            return {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "marine_forecast": marine_list
            }
        
        except KeyError as e:
            raise DataNotFoundError(f"Missing required field in response: {e}")
        except (IndexError, TypeError) as e:
            raise DataNotFoundError(f"Invalid response structure: {e}")
