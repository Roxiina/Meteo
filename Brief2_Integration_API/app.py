"""
Flask API Server for Cyclone Detection.

This module provides a REST API endpoint for cyclone detection
and serves the frontend web interface.
"""

import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from src.utils.api_client import APIClient
from src.services.weather_service import WeatherService
from src.services.marine_service import MarineService
from src.services.cyclone_detector import CycloneDetector
from src.utils.error_handler import APIError, ValidationError

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
api_client = APIClient()
weather_service = WeatherService(api_client)
marine_service = MarineService(api_client)
cyclone_detector = CycloneDetector()

logger.info("Services initialized successfully")


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/api/detect', methods=['GET', 'POST'])
def detect_cyclone():
    """
    Detect cyclone conditions for a given location.
    
    GET: Returns API info and usage
    POST: Performs cyclone detection
    
    Expected JSON body for POST:
    {
        "latitude": float,
        "longitude": float,
        "location_name": string (optional)
    }
    
    Returns:
    {
        "success": bool,
        "location_name": string,
        "data": {
            "location": {"latitude": float, "longitude": float},
            "category": string,
            "severity_score": float,
            "conditions": {...},
            "details": {...}
        },
        "error": string (if success is false)
    }
    """
    
    # Handle GET request - return API info
    if request.method == 'GET':
        return jsonify({
            "message": "Cyclone Tracker API",
            "status": "operational",
            "endpoint": "/api/detect",
            "method": "POST",
            "usage": {
                "description": "Détecte les conditions cycloniques pour une localisation donnée",
                "required_params": ["latitude", "longitude"],
                "optional_params": ["location_name"],
                "example": {
                    "latitude": -21.1151,
                    "longitude": 55.5364,
                    "location_name": "La Réunion"
                }
            },
            "frontend_url": "http://127.0.0.1:5000/"
        })
    
    # Handle POST request - perform detection
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Extract parameters
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        location_name = data.get('location_name', f"{latitude}, {longitude}")
        analysis_date = data.get('analysis_date')  # New parameter for historical analysis
        
        # Validate parameters
        if latitude is None or longitude is None:
            return jsonify({
                "success": False,
                "error": "Missing required parameters: latitude and longitude"
            }), 400
        
        # Convert to float
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid latitude or longitude format"
            }), 400
        
        # Validate date if provided
        historical_analysis = False
        if analysis_date:
            try:
                parsed_date = datetime.fromisoformat(analysis_date)
                historical_analysis = True
                logger.info(f"Historical analysis requested for date: {analysis_date}")
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "Invalid date format. Use YYYY-MM-DD format."
                }), 400
        
        logger.info(f"Analyzing location: {location_name} ({latitude}, {longitude})")
        if historical_analysis:
            logger.info(f"Historical analysis for date: {analysis_date}")
        
        # Get weather data (with date if historical)
        if historical_analysis:
            # Historical data with specific date
            weather_data = weather_service.get_forecast(
                latitude=latitude,
                longitude=longitude,
                start_date=analysis_date,
                end_date=analysis_date
            )
        else:
            weather_data = weather_service.get_forecast(
                latitude=latitude,
                longitude=longitude,
                forecast_days=7
            )
        
        # Get marine data (optional)
        marine_data = None
        try:
            if historical_analysis:
                # Historical marine data with specific date
                marine_data = marine_service.get_marine_forecast(
                    latitude=latitude,
                    longitude=longitude,
                    start_date=analysis_date,
                    end_date=analysis_date
                )
            else:
                marine_data = marine_service.get_marine_forecast(
                    latitude=latitude,
                    longitude=longitude,
                    forecast_days=7
                )
        except Exception as e:
            logger.warning(f"Could not fetch marine data: {e}")
        
        # Detect cyclone
        detection_result = cyclone_detector.detect(
            weather_data=weather_data,
            marine_data=marine_data
        )
        
        # Add analysis type and date to result
        if historical_analysis:
            detection_result['details']['analysis_type'] = 'historical'
            detection_result['details']['requested_date'] = analysis_date
        else:
            detection_result['details']['analysis_type'] = 'real_time'
        
        detection_result['details']['analysis_date'] = analysis_date if analysis_date else datetime.now().isoformat()
        
        logger.info(f"Detection complete: {detection_result['category']}")
        
        # Return result
        return jsonify({
            "success": True,
            "location_name": location_name,
            "data": detection_result
        })
    
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            "success": False,
            "error": f"Validation error: {str(e)}"
        }), 400
    
    except APIError as e:
        logger.error(f"API error: {e}")
        return jsonify({
            "success": False,
            "error": f"API error: {str(e)}"
        }), 502
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Cyclone Tracker API"
    })


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("CYCLONE TRACKER API SERVER")
    print("=" * 60)
    print("\nServer starting...")
    print("Frontend: http://127.0.0.1:5000")
    print("API endpoint: http://127.0.0.1:5000/api/detect")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
