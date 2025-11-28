"""
Integration tests for Cyclone Tracker.

These tests make real API calls to verify end-to-end functionality.
Run with: pytest -m integration
"""

import pytest

from src.utils.api_client import APIClient
from src.services.weather_service import WeatherService
from src.services.marine_service import MarineService
from src.services.cyclone_detector import CycloneDetector
from src.utils.error_handler import APIError


@pytest.mark.integration
class TestWeatherIntegration:
    """Integration tests for Weather API."""
    
    def test_get_forecast_real_api(self):
        """Test real API call for weather forecast."""
        client = APIClient()
        service = WeatherService(api_client=client)
        
        result = service.get_forecast(
            latitude=-21.1151,
            longitude=55.5364,
            forecast_days=3
        )
        
        assert result["location"]["latitude"] == -21.1151
        assert len(result["forecast"]) == 3
        assert all("temperature_2m_max" in day for day in result["forecast"])
        
        client.close()
    
    def test_get_current_weather_real_api(self):
        """Test real API call for current weather."""
        client = APIClient()
        service = WeatherService(api_client=client)
        
        result = service.get_current_weather(
            latitude=-21.1151,
            longitude=55.5364
        )
        
        assert result["location"]["latitude"] == -21.1151
        assert "current" in result
        assert "temperature_2m" in result["current"]
        
        client.close()


@pytest.mark.integration
class TestMarineIntegration:
    """Integration tests for Marine API."""
    
    def test_get_marine_forecast_real_api(self):
        """Test real API call for marine forecast."""
        client = APIClient()
        service = MarineService(api_client=client)
        
        result = service.get_marine_forecast(
            latitude=-21.1151,
            longitude=55.5364,
            forecast_days=3
        )
        
        assert result["location"]["latitude"] == -21.1151
        assert len(result["marine_forecast"]) == 3
        assert all("wave_height" in day for day in result["marine_forecast"])
        
        client.close()


@pytest.mark.integration
class TestCycloneDetectionIntegration:
    """Integration tests for complete cyclone detection workflow."""
    
    def test_full_detection_workflow(self):
        """Test complete detection workflow with real APIs."""
        # Initialize services
        client = APIClient()
        weather_service = WeatherService(api_client=client)
        marine_service = MarineService(api_client=client)
        detector = CycloneDetector()
        
        # Get weather data
        weather_data = weather_service.get_forecast(
            latitude=-21.1151,
            longitude=55.5364,
            forecast_days=7
        )
        
        # Get marine data
        try:
            marine_data = marine_service.get_marine_forecast(
                latitude=-21.1151,
                longitude=55.5364,
                forecast_days=7
            )
        except APIError:
            marine_data = None
        
        # Detect cyclone
        result = detector.detect(
            weather_data=weather_data,
            marine_data=marine_data
        )
        
        # Verify result structure
        assert "location" in result
        assert "category" in result
        assert "severity_score" in result
        assert "conditions" in result
        assert 0 <= result["severity_score"] <= 1
        
        client.close()
    
    def test_multiple_locations(self):
        """Test detection for multiple Indian Ocean locations."""
        locations = [
            {"name": "La Réunion", "lat": -21.1151, "lon": 55.5364},
            {"name": "Maurice", "lat": -20.1609, "lon": 57.5012},
        ]
        
        client = APIClient()
        weather_service = WeatherService(api_client=client)
        detector = CycloneDetector()
        
        results = []
        for location in locations:
            weather_data = weather_service.get_forecast(
                latitude=location["lat"],
                longitude=location["lon"],
                forecast_days=3
            )
            
            result = detector.detect(weather_data=weather_data)
            results.append(result)
        
        # Verify all results are valid
        assert len(results) == 2
        assert all("category" in r for r in results)
        
        client.close()


@pytest.mark.integration
@pytest.mark.slow
class TestAPIReliability:
    """Integration tests for API reliability and error handling."""
    
    def test_api_timeout_handling(self):
        """Test API timeout handling."""
        client = APIClient(timeout=1)  # Very short timeout
        service = WeatherService(api_client=client)
        
        # This may timeout or succeed depending on network
        try:
            result = service.get_forecast(-21.1151, 55.5364)
            assert result is not None
        except APIError as e:
            # Timeout is acceptable
            assert "timeout" in str(e).lower() or "failed" in str(e).lower()
        finally:
            client.close()
    
    def test_api_retry_on_failure(self):
        """Test API retry mechanism."""
        client = APIClient(retry_count=2, retry_delay=1)
        service = WeatherService(api_client=client)
        
        # Should succeed with retries if needed
        result = service.get_forecast(-21.1151, 55.5364, forecast_days=1)
        assert result is not None
        
        client.close()
