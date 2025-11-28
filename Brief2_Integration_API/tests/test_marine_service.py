"""
Tests for MarineService.

This module tests marine API integration and data parsing.
"""

import pytest
from unittest.mock import Mock

from src.services.marine_service import MarineService
from src.utils.error_handler import ValidationError, DataNotFoundError


class TestMarineServiceInit:
    """Test MarineService initialization."""
    
    def test_init_default_client(self):
        """Test initialization with default API client."""
        service = MarineService()
        assert service.api_client is not None
        assert service.base_url == "https://marine-api.open-meteo.com/v1/marine"
    
    def test_init_custom_client(self, mock_api_client):
        """Test initialization with custom API client."""
        service = MarineService(api_client=mock_api_client)
        assert service.api_client == mock_api_client


class TestMarineServiceGetForecast:
    """Test get_marine_forecast method."""
    
    def test_get_marine_forecast_success(self, mock_api_client, mock_marine_response, valid_coordinates):
        """Test successful marine forecast retrieval."""
        mock_api_client.get.return_value = mock_marine_response
        service = MarineService(api_client=mock_api_client)
        
        result = service.get_marine_forecast(
            latitude=valid_coordinates["latitude"],
            longitude=valid_coordinates["longitude"],
            forecast_days=3
        )
        
        assert result["location"]["latitude"] == valid_coordinates["latitude"]
        assert len(result["marine_forecast"]) == 3
        assert "wave_height" in result["marine_forecast"][0]
        assert "wave_direction" in result["marine_forecast"][0]
    
    def test_get_marine_forecast_invalid_days(self, mock_api_client, valid_coordinates):
        """Test marine forecast with invalid forecast_days (>7)."""
        service = MarineService(api_client=mock_api_client)
        
        with pytest.raises(ValidationError, match="forecast_days must be between 1 and 7"):
            service.get_marine_forecast(
                latitude=valid_coordinates["latitude"],
                longitude=valid_coordinates["longitude"],
                forecast_days=10
            )
    
    def test_get_marine_forecast_invalid_coordinates(self, mock_api_client):
        """Test marine forecast with invalid coordinates."""
        service = MarineService(api_client=mock_api_client)
        
        with pytest.raises(ValidationError):
            service.get_marine_forecast(latitude=-95.0, longitude=55.5364)
    
    def test_get_marine_forecast_missing_data(self, mock_api_client, valid_coordinates):
        """Test marine forecast with missing response data."""
        mock_api_client.get.return_value = {"daily": {}}
        service = MarineService(api_client=mock_api_client)
        
        with pytest.raises(DataNotFoundError):
            service.get_marine_forecast(
                latitude=valid_coordinates["latitude"],
                longitude=valid_coordinates["longitude"]
            )


class TestMarineServiceGetSST:
    """Test get_sst method."""
    
    def test_get_sst_success(self, mock_api_client, mock_marine_response, valid_coordinates):
        """Test SST retrieval."""
        mock_api_client.get.return_value = mock_marine_response
        service = MarineService(api_client=mock_api_client)
        
        result = service.get_sst(
            latitude=valid_coordinates["latitude"],
            longitude=valid_coordinates["longitude"]
        )
        
        assert result["location"]["latitude"] == valid_coordinates["latitude"]
        assert "sst" in result
        assert "date" in result["sst"]
