"""
Cyclone Detection Service.

This service analyzes weather and marine data to detect potential
tropical cyclone conditions using meteorological criteria.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from ..utils.error_handler import ValidationError
from ..config.settings import settings

logger = logging.getLogger(__name__)


class CycloneCategory(Enum):
    """Tropical cyclone categories based on severity."""
    NONE = "Aucun"
    TROPICAL_DEPRESSION = "Dépression Tropicale"
    TROPICAL_STORM = "Tempête Tropicale"
    CYCLONE = "Cyclone"


class CycloneDetector:
    """
    Service for detecting cyclone conditions from weather and marine data.
    
    Detection Algorithm:
    - Sea Surface Temperature (SST) > 26.5°C (threshold configurable)
    - Surface Pressure < 980 hPa (threshold configurable)
    - Wind Speed > 117 km/h (threshold configurable)
    
    All three conditions must be met to classify as CYCLONE.
    Partial conditions indicate TROPICAL_STORM or TROPICAL_DEPRESSION.
    """
    
    def __init__(
        self,
        sst_threshold: Optional[float] = None,
        pressure_threshold: Optional[float] = None,
        wind_threshold: Optional[float] = None
    ):
        """
        Initialize Cyclone Detector.
        
        Args:
            sst_threshold: SST threshold in °C (default: from settings)
            pressure_threshold: Pressure threshold in hPa (default: from settings)
            wind_threshold: Wind speed threshold in km/h (default: from settings)
        """
        self.sst_threshold = sst_threshold or settings.CYCLONE_SST_THRESHOLD
        self.pressure_threshold = pressure_threshold or settings.CYCLONE_PRESSURE_THRESHOLD
        self.wind_threshold = wind_threshold or settings.CYCLONE_WIND_THRESHOLD
        
        logger.info(
            f"CycloneDetector initialized: "
            f"SST>{self.sst_threshold}°C, "
            f"Pressure<{self.pressure_threshold}hPa, "
            f"Wind>{self.wind_threshold}km/h"
        )
    
    def detect(
        self,
        weather_data: Dict[str, Any],
        marine_data: Optional[Dict[str, Any]] = None,
        sst: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Detect cyclone conditions from weather and marine data.
        
        Args:
            weather_data: Weather data from WeatherService
            marine_data: Optional marine data from MarineService
            sst: Optional sea surface temperature in °C (if marine_data not provided)
        
        Returns:
            Dictionary with detection results:
            {
                "location": {"latitude": float, "longitude": float},
                "category": str,
                "severity_score": float (0-1),
                "conditions": {
                    "sst": {"value": float, "threshold": float, "met": bool},
                    "pressure": {"value": float, "threshold": float, "met": bool},
                    "wind": {"value": float, "threshold": float, "met": bool}
                },
                "details": {
                    "temperature_max": float,
                    "temperature_min": float,
                    "analysis_date": str
                }
            }
        
        Raises:
            ValidationError: If required data is missing or invalid
        """
        # Extract location
        try:
            location = weather_data["location"]
        except KeyError:
            raise ValidationError("weather_data must contain 'location' field")
        
        # Extract weather parameters
        try:
            forecast = weather_data["forecast"]
            if not forecast:
                raise ValidationError("weather_data forecast is empty")
            
            # Use first day of forecast
            first_day = forecast[0]
            
            temperature_max = first_day["temperature_2m_max"]
            temperature_min = first_day["temperature_2m_min"]
            surface_pressure = first_day["surface_pressure"]
            wind_speed = first_day["wind_speed_10m_max"]
            # Extract wind gusts if available
            wind_gusts = first_day.get("wind_gusts_10m_max", wind_speed * 1.5)  # Estimate if not available
            analysis_date = first_day["date"]
        
        except (KeyError, IndexError) as e:
            raise ValidationError(f"Invalid weather_data structure: {e}")
        
        # Determine SST
        if sst is None:
            if marine_data:
                # Try to extract SST from marine data
                try:
                    sst_data = marine_data.get("sst", {})
                    sst = sst_data.get("temperature")
                except (KeyError, AttributeError):
                    pass
            
            # If still None, use simplified estimate based on air temperature
            if sst is None:
                sst = self._estimate_sst(temperature_max, temperature_min)
                logger.warning(
                    f"SST not provided, using estimated value: {sst:.1f}°C"
                )
        
        # Analyze conditions (including wind gusts)
        conditions = self._analyze_conditions(sst, surface_pressure, wind_speed, wind_gusts)
        
        # Calculate severity score and category
        severity_score = self._calculate_severity_score(conditions)
        category = self._classify_cyclone(conditions, severity_score)
        
        # Build result
        result = {
            "location": location,
            "category": category.value,
            "severity_score": severity_score,
            "conditions": conditions,
            "details": {
                "temperature_max": temperature_max,
                "temperature_min": temperature_min,
                "analysis_date": analysis_date
            }
        }
        
        logger.info(
            f"Cyclone detection for ({location['latitude']}, {location['longitude']}): "
            f"{category.value} (severity: {severity_score:.2f})"
        )
        
        return result
    
    def get_risk_level_from_gusts(self, wind_gusts_kmh: float) -> tuple[str, str]:
        """
        Determine cyclone risk level based on wind gusts speed.
        
        Args:
            wind_gusts_kmh: Wind gusts speed in km/h
        
        Returns:
            Tuple of (risk_level, status_class)
        """
        if wind_gusts_kmh >= 120:
            return "CYCLONE DÉTECTÉ", "status-danger"
        elif wind_gusts_kmh >= 90:
            return "ALERTE CYCLONE", "status-warning"
        elif wind_gusts_kmh >= 70:
            return "VIGILANCE RENFORCÉE", "status-caution"
        elif wind_gusts_kmh >= 50:
            return "SURVEILLANCE", "status-normal"
        else:
            return "CONDITIONS NORMALES", "status-safe"
    
    def get_gust_risk_message(self, wind_gusts_kmh: float) -> str:
        """
        Get detailed risk message based on wind gust speed.
        
        Args:
            wind_gusts_kmh: Wind gusts speed in km/h
        
        Returns:
            Detailed risk assessment message
        """
        if wind_gusts_kmh >= 120:
            return "Rafales extrêmes détectées ! Formation cyclonique confirmée. Risque majeur pour les structures et la navigation."
        elif wind_gusts_kmh >= 90:
            return "Rafales très fortes observées. Conditions pré-cycloniques probables. Prudence maximale recommandée."
        elif wind_gusts_kmh >= 70:
            return "Rafales importantes. Surveillance météorologique renforcée nécessaire. Éviter les activités extérieures."
        elif wind_gusts_kmh >= 50:
            return "Rafales modérées détectées. Conditions météorologiques instables. Vigilance recommandée."
        else:
            return "Rafales faibles. Conditions météorologiques stables dans la zone d'analyse."
    
    def _analyze_conditions(
        self,
        sst: float,
        pressure: float,
        wind_speed: float,
        wind_gusts: float
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze meteorological conditions against thresholds.
        
        Args:
            sst: Sea surface temperature in °C
            pressure: Surface pressure in hPa
            wind_speed: Wind speed in km/h
            wind_gusts: Wind gusts speed in km/h
        
        Returns:
            Dictionary with condition analysis
        """
        # Define wind gusts thresholds for cyclone detection
        wind_gusts_threshold = 120.0  # km/h - Strong cyclone indication
        
        conditions = {
            "sst": {
                "value": sst,
                "threshold": self.sst_threshold,
                "met": sst > self.sst_threshold
            },
            "pressure": {
                "value": pressure,
                "threshold": self.pressure_threshold,
                "met": pressure < self.pressure_threshold
            },
            "wind": {
                "value": wind_speed,
                "threshold": self.wind_threshold,
                "met": wind_speed > self.wind_threshold
            },
            "wind_gusts": {
                "value": wind_gusts,
                "threshold": wind_gusts_threshold,
                "met": wind_gusts >= wind_gusts_threshold
            }
        }
        
        return conditions
    
    def _calculate_severity_score(self, conditions: Dict[str, Dict[str, Any]]) -> float:
        """
        Calculate cyclone severity score (0-1).
        
        Score calculation:
        - SST: normalized distance above threshold
        - Pressure: normalized distance below threshold
        - Wind: normalized distance above threshold
        - Wind Gusts: normalized distance above threshold (weighted more heavily)
        - Weighted average of four normalized values
        
        Args:
            conditions: Analyzed conditions
        
        Returns:
            Severity score between 0 and 1
        """
        # SST score (0-1)
        sst_value = conditions["sst"]["value"]
        sst_threshold = conditions["sst"]["threshold"]
        sst_max = 30.0  # Maximum expected SST
        sst_score = max(0, min(1, (sst_value - sst_threshold) / (sst_max - sst_threshold)))
        
        # Pressure score (0-1)
        pressure_value = conditions["pressure"]["value"]
        pressure_threshold = conditions["pressure"]["threshold"]
        pressure_min = 900.0  # Extreme low pressure
        pressure_score = max(0, min(1, (pressure_threshold - pressure_value) / (pressure_threshold - pressure_min)))
        
        # Wind score (0-1)
        wind_value = conditions["wind"]["value"]
        wind_threshold = conditions["wind"]["threshold"]
        wind_max = 250.0  # Category 5 hurricane
        wind_score = max(0, min(1, (wind_value - wind_threshold) / (wind_max - wind_threshold)))
        
        # Wind gusts score (0-1) - More heavily weighted
        gusts_value = conditions["wind_gusts"]["value"]
        gusts_threshold = conditions["wind_gusts"]["threshold"]
        gusts_max = 300.0  # Extreme wind gusts
        gusts_score = max(0, min(1, (gusts_value - gusts_threshold) / (gusts_max - gusts_threshold)))
        
        # Weighted average score (wind gusts have 2x weight due to cyclone significance)
        severity_score = (sst_score + pressure_score + wind_score + (gusts_score * 2)) / 5.0
        
        return severity_score
    
    def _classify_cyclone(
        self,
        conditions: Dict[str, Dict[str, Any]],
        severity_score: float
    ) -> CycloneCategory:
        """
        Classify cyclone category based on conditions and severity.
        
        Classification:
        - CYCLONE: All 3 conditions met
        - TROPICAL_STORM: 2 conditions met OR severity > 0.5
        - TROPICAL_DEPRESSION: 1 condition met OR severity > 0.3
        - NONE: No significant conditions
        
        Args:
            conditions: Analyzed conditions
            severity_score: Calculated severity score
        
        Returns:
            Cyclone category
        """
        # Count met conditions
        met_count = sum(1 for c in conditions.values() if c["met"])
        
        if met_count == 3:
            return CycloneCategory.CYCLONE
        elif met_count == 2 or severity_score > 0.5:
            return CycloneCategory.TROPICAL_STORM
        elif met_count == 1 or severity_score > 0.3:
            return CycloneCategory.TROPICAL_DEPRESSION
        else:
            return CycloneCategory.NONE
    
    def _estimate_sst(self, temp_max: float, temp_min: float) -> float:
        """
        Estimate SST from air temperature (simplified).
        
        This is a rough approximation. In production, always use
        actual SST data from marine API or satellite data.
        
        Args:
            temp_max: Maximum air temperature in °C
            temp_min: Minimum air temperature in °C
        
        Returns:
            Estimated SST in °C
        """
        # SST is typically 1-2°C warmer than air temperature in tropics
        avg_temp = (temp_max + temp_min) / 2.0
        estimated_sst = avg_temp + 1.5
        
        logger.debug(f"Estimated SST: {estimated_sst:.1f}°C (from air temp: {avg_temp:.1f}°C)")
        
        return estimated_sst
