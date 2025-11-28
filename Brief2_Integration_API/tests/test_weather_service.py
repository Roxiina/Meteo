"""
Tests for WeatherService.

This module tests weather API integration and data parsing.
"""

import pytest
from unittest.mock import Mock, patch

from src.services.weather_service import WeatherService
from src.utils.error_handler import ValidationError, DataNotFoundError


class TestWeatherServiceInit:
    """Test WeatherService initialization."""
    
    def test_init_default_client(self):
        """Test initialization with default API client."""
        service = WeatherService()
        assert service.api_client is not None
        assert service.base_url == "https://api.open-meteo.com/v1/forecast"
    
    def test_init_custom_client(self, mock_api_client):
        """Test initialization with custom API client."""
        service = WeatherService(api_client=mock_api_client)
        assert service.api_client == mock_api_client


class TestWeatherServiceGetForecast:
    """Test get_forecast method."""
    
    def test_get_forecast_success(self, mock_api_client, mock_weather_response, valid_coordinates):
        """Test successful forecast retrieval."""
        mock_api_client.get.return_value = mock_weather_response
        service = WeatherService(api_client=mock_api_client)
        
        result = service.get_forecast(
            latitude=valid_coordinates["latitude"],
            longitude=valid_coordinates["longitude"],
            forecast_days=3
        )
        
        assert result["location"]["latitude"] == valid_coordinates["latitude"]
        assert result["location"]["longitude"] == valid_coordinates["longitude"]
        assert len(result["forecast"]) == 3
        assert "date" in result["forecast"][0]
        assert "temperature_2m_max" in result["forecast"][0]
    
    @pytest.mark.parametrize("forecast_days", [1, 7, 16])
    def test_get_forecast_various_days(self, mock_api_client, mock_weather_response, valid_coordinates, forecast_days):
        """Test forecast with various day counts."""
        mock_api_client.get.return_value = mock_weather_response
        service = WeatherService(api_client=mock_api_client)
        
        result = service.get_forecast(
            latitude=valid_coordinates["latitude"],
            longitude=valid_coordinates["longitude"],
            forecast_days=forecast_days
        )
        
        assert result is not None
    
    def test_get_forecast_invalid_latitude(self, mock_api_client):
        """Test forecast with invalid latitude."""
        service = WeatherService(api_client=mock_api_client)
        
        with pytest.raises(ValidationError, match="Latitude must be between -90 and 90"):
            service.get_forecast(latitude=-95.0, longitude=55.5364)
    
    def test_get_forecast_invalid_longitude(self, mock_api_client):
        """Test forecast with invalid longitude."""
        service = WeatherService(api_client=mock_api_client)
        
        with pytest.raises(ValidationError, match="Longitude must be between -180 and 180"):
            service.get_forecast(latitude=-21.1151, longitude=185.0)
    
    def test_get_forecast_invalid_forecast_days(self, mock_api_client, valid_coordinates):
        """Test forecast with invalid forecast_days."""
        service = WeatherService(api_client=mock_api_client)
        
        with pytest.raises(ValidationError, match="forecast_days must be between 1 and 16"):
            service.get_forecast(
                latitude=valid_coordinates["latitude"],
                longitude=valid_coordinates["longitude"],
                forecast_days=20
            )
    
    def test_get_forecast_missing_data(self, mock_api_client, valid_coordinates):
        """Test forecast with missing response data."""
        mock_api_client.get.return_value = {"daily": {}}
        service = WeatherService(api_client=mock_api_client)
        
        with pytest.raises(DataNotFoundError):
            service.get_forecast(
                latitude=valid_coordinates["latitude"],
                longitude=valid_coordinates["longitude"]
            )


class TestWeatherServiceGetCurrent:
    """Test get_current_weather method."""
    
    def test_get_current_success(self, mock_api_client, mock_current_weather_response, valid_coordinates):
        """Test successful current weather retrieval."""
        mock_api_client.get.return_value = mock_current_weather_response
        service = WeatherService(api_client=mock_api_client)
        
        result = service.get_current_weather(
            latitude=valid_coordinates["latitude"],
            longitude=valid_coordinates["longitude"]
        )
        
        assert result["location"]["latitude"] == valid_coordinates["latitude"]
        assert result["current"]["temperature_2m"] == 28.5
        assert result["current"]["surface_pressure"] == 975.2
    
    def test_get_current_invalid_coordinates(self, mock_api_client):
        """Test current weather with invalid coordinates."""
        service = WeatherService(api_client=mock_api_client)
        
        with pytest.raises(ValidationError):
            service.get_current_weather(latitude=-95.0, longitude=55.5364)
    
    def test_get_current_missing_data(self, mock_api_client, valid_coordinates):
        """Test current weather with missing response data."""
        mock_api_client.get.return_value = {"current": {}}
        service = WeatherService(api_client=mock_api_client)
        
        with pytest.raises(DataNotFoundError):
            service.get_current_weather(
                latitude=valid_coordinates["latitude"],
                longitude=valid_coordinates["longitude"]
            )


class TestWeatherServiceValidation:
    """Test validation methods."""
    
    def test_validate_coordinates_valid(self, mock_api_client):
        """Test coordinate validation with valid inputs."""
        service = WeatherService(api_client=mock_api_client)
        
        # Should not raise exception
        service._validate_coordinates(-21.1151, 55.5364)
    
    @pytest.mark.parametrize("lat,lon", [
        (-95.0, 55.5364),
        (95.0, 55.5364),
        (-21.1151, -185.0),
        (-21.1151, 185.0),
        ("invalid", 55.5364),
        (-21.1151, "invalid")
    ])
    def test_validate_coordinates_invalid(self, mock_api_client, lat, lon):
        """Test coordinate validation with invalid inputs."""
        service = WeatherService(api_client=mock_api_client)
        
        with pytest.raises(ValidationError):
            service._validate_coordinates(lat, lon)
