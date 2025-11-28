"""
Cyclone Tracker - Demo Application

This module demonstrates cyclone detection for multiple locations
in the Indian Ocean region.
"""

import logging
import sys
from pathlib import Path

from src.config.settings import settings
from src.utils.api_client import APIClient
from src.services.weather_service import WeatherService
from src.services.marine_service import MarineService
from src.services.cyclone_detector import CycloneDetector
from src.utils.error_handler import APIError, ValidationError


# Configure logging
def setup_logging():
    """Configure application logging."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_dir / "cyclone_tracker.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def display_results(location_name: str, detection_result: dict):
    """
    Display cyclone detection results in a formatted way.
    
    Args:
        location_name: Name of the location
        detection_result: Detection result from CycloneDetector
    """
    print(f"\n{'=' * 70}")
    print(f"ANALYSE CYCLONIQUE - {location_name}")
    print(f"{'=' * 70}")
    
    location = detection_result["location"]
    print(f"Coordonnées: {location['latitude']}, {location['longitude']}")
    print(f"Date d'analyse: {detection_result['details']['analysis_date']}")
    
    print(f"\nCATEGORIE: {detection_result['category']}")
    print(f"Severite: {detection_result['severity_score']:.2%}")
    
    print("\nCONDITIONS METEOROLOGIQUES:")
    conditions = detection_result["conditions"]
    
    # SST
    sst = conditions["sst"]
    status = "[OK]" if sst["met"] else "[NO]" 
    print(f"  {status} Temperature de surface: {sst['value']:.1f}C (seuil: >{sst['threshold']:.1f}C)")
    
    # Pressure
    pressure = conditions["pressure"]
    status = "[OK]" if pressure["met"] else "[NO]"
    print(f"  {status} Pression de surface: {pressure['value']:.1f} hPa (seuil: <{pressure['threshold']:.1f} hPa)")
    
    # Wind
    wind = conditions["wind"]
    status = "[OK]" if wind["met"] else "[NO]"
    print(f"  {status} Vitesse du vent: {wind['value']:.1f} km/h (seuil: >{wind['threshold']:.1f} km/h)")
    
    print("\nTEMPERATURES:")
    details = detection_result["details"]
    print(f"  Maximum: {details['temperature_max']:.1f}C")
    print(f"  Minimum: {details['temperature_min']:.1f}C")
    
    print(f"{'=' * 70}\n")


def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 70)
    logger.info("CYCLONE TRACKER - Brief 2")
    logger.info("=" * 70)
    
    # Display configuration
    settings.display()
    
    # Initialize services
    logger.info("\nInitialisation des services...")
    api_client = APIClient()
    weather_service = WeatherService(api_client)
    marine_service = MarineService(api_client)
    cyclone_detector = CycloneDetector()
    
    # Define locations to analyze (Indian Ocean region)
    locations = [
        {"name": "La Réunion", "lat": -21.1151, "lon": 55.5364},
        {"name": "Maurice (Île)", "lat": -20.1609, "lon": 57.5012},
        {"name": "Madagascar (Antananarivo)", "lat": -18.8792, "lon": 47.5079},
        {"name": "Comores (Moroni)", "lat": -11.6986, "lon": 43.2551},
    ]
    
    print("\n" + "=" * 70)
    print("ANALYSE DE DÉTECTION CYCLONIQUE - OCÉAN INDIEN")
    print("=" * 70)
    
    # Analyze each location
    results = []
    for location in locations:
        try:
            logger.info(f"\nAnalyse de {location['name']}...")
            
            # Get weather data
            weather_data = weather_service.get_forecast(
                latitude=location["lat"],
                longitude=location["lon"],
                forecast_days=7
            )
            
            # Get marine data (optional, for better accuracy)
            try:
                marine_data = marine_service.get_marine_forecast(
                    latitude=location["lat"],
                    longitude=location["lon"],
                    forecast_days=7
                )
            except APIError as e:
                logger.warning(f"Marine data unavailable: {e}")
                marine_data = None
            
            # Detect cyclone conditions
            detection_result = cyclone_detector.detect(
                weather_data=weather_data,
                marine_data=marine_data
            )
            
            results.append({
                "location": location["name"],
                "result": detection_result
            })
            
            # Display results
            display_results(location["name"], detection_result)
        
        except ValidationError as e:
            logger.error(f"[X] Erreur de validation pour {location['name']}: {e}")
            print(f"\n[X] ERREUR: {e}\n")
        
        except APIError as e:
            logger.error(f"[X] Erreur API pour {location['name']}: {e}")
            print(f"\n[X] ERREUR API: {e}\n")
        
        except Exception as e:
            logger.exception(f"[X] Erreur inattendue pour {location['name']}: {e}")
            print(f"\n[X] ERREUR INATTENDUE: {e}\n")
    
    # Summary
    print("\n" + "=" * 70)
    print("RÉSUMÉ DE L'ANALYSE")
    print("=" * 70)
    
    for item in results:
        result = item["result"]
        category = result["category"]
        severity = result["severity_score"]
        
        icon = "[HIGH]" if severity > 0.7 else "[MED]" if severity > 0.4 else "[LOW]"
        print(f"{icon} {item['location']}: {category} (Severite: {severity:.2%})")
    
    print("=" * 70)
    
    # Cleanup
    api_client.close()
    logger.info("\n[OK] Analyse terminee avec succes")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Programme interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logging.exception(f"Erreur fatale: {e}")
        sys.exit(1)
