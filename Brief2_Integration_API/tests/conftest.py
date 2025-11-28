"""
Pytest fixtures for Cyclone Tracker tests.

This module provides reusable fixtures for testing.
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any


@pytest.fixture
def valid_coordinates():
    """Valid geographic coordinates in Indian Ocean."""
    return {
        "latitude": -21.1151,
        "longitude": 55.5364
    }


@pytest.fixture
def invalid_coordinates():
    """Invalid geographic coordinates for testing validation."""
    return [
        {"latitude": -95.0, "longitude": 55.5364},  # Latitude out of range
        {"latitude": -21.1151, "longitude": 185.0},  # Longitude out of range
        {"latitude": "invalid", "longitude": 55.5364},  # Invalid type
    ]


@pytest.fixture
def mock_weather_response():
    """Mock successful weather API response."""
    return {
        "latitude": -21.1151,
        "longitude": 55.5364,
        "timezone": "Indian/Reunion",
        "daily": {
            "time": ["2024-01-15", "2024-01-16", "2024-01-17"],
            "temperature_2m_max": [30.5, 31.2, 29.8],
            "temperature_2m_min": [24.3, 25.1, 23.9],
            "surface_pressure": [975.2, 973.5, 978.1],
            "wind_speed_10m_max": [125.3, 118.7, 95.2]
        }
    }


@pytest.fixture
def mock_marine_response():
    """Mock successful marine API response."""
    return {
        "latitude": -21.1151,
        "longitude": 55.5364,
        "timezone": "Indian/Reunion",
        "daily": {
            "time": ["2024-01-15", "2024-01-16", "2024-01-17"],
            "wave_height_max": [8.5, 9.2, 7.3],
            "wave_direction_dominant": [135, 142, 128],
            "ocean_current_velocity": [2.3, 2.5, 2.1],
            "ocean_current_direction": [140, 145, 135]
        }
    }


@pytest.fixture
def mock_current_weather_response():
    """Mock successful current weather API response."""
    return {
        "latitude": -21.1151,
        "longitude": 55.5364,
        "timezone": "Indian/Reunion",
        "current": {
            "time": "2024-01-15T14:00",
            "temperature_2m": 28.5,
            "surface_pressure": 975.2,
            "wind_speed_10m": 125.3
        }
    }


@pytest.fixture
def cyclone_conditions():
    """Weather data representing cyclone conditions."""
    return {
        "location": {
            "latitude": -21.1151,
            "longitude": 55.5364
        },
        "forecast": [
            {
                "date": "2024-01-15",
                "temperature_2m_max": 30.5,
                "temperature_2m_min": 24.3,
                "surface_pressure": 970.0,  # Below threshold (980)
                "wind_speed_10m_max": 130.0  # Above threshold (117)
            }
        ]
    }


@pytest.fixture
def non_cyclone_conditions():
    """Weather data representing normal conditions."""
    return {
        "location": {
            "latitude": -21.1151,
            "longitude": 55.5364
        },
        "forecast": [
            {
                "date": "2024-01-15",
                "temperature_2m_max": 25.0,
                "temperature_2m_min": 20.0,
                "surface_pressure": 1013.0,  # Normal pressure
                "wind_speed_10m_max": 30.0  # Normal wind
            }
        ]
    }


@pytest.fixture
def mock_api_client(monkeypatch):
    """Mock APIClient for testing without real API calls."""
    mock_client = Mock()
    mock_client.get.return_value = {
        "latitude": -21.1151,
        "longitude": 55.5364,
        "daily": {
            "time": ["2024-01-15"],
            "temperature_2m_max": [30.5],
            "temperature_2m_min": [24.3],
            "surface_pressure": [1013.0],
            "wind_speed_10m_max": [50.0]
        }
    }
    return mock_client
