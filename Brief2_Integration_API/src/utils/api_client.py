"""
HTTP API Client with retry logic and error handling.

This module provides a reusable API client for making HTTP requests
with automatic retry, exponential backoff, and comprehensive error handling.
"""

import time
import logging
from typing import Dict, Any, Optional
import requests

from ..config.settings import settings
from .error_handler import (
    APIError,
    ValidationError,
    RateLimitError,
    TimeoutError as CustomTimeoutError,
)

logger = logging.getLogger(__name__)


class APIClient:
    """
    HTTP client for API calls with retry logic and error handling.
    
    Features:
    - Automatic retry with exponential backoff
    - Rate limit handling (HTTP 429)
    - Timeout management
    - Request validation
    - Detailed logging
    - Optional Redis caching
    """
    
    def __init__(
        self,
        timeout: Optional[int] = None,
        retry_count: Optional[int] = None,
        retry_delay: Optional[int] = None
    ):
        """
        Initialize API client.
        
        Args:
            timeout: Request timeout in seconds (default: from settings)
            retry_count: Number of retry attempts (default: from settings)
            retry_delay: Initial delay between retries (default: from settings)
        """
        self.timeout = timeout or settings.TIMEOUT
        self.retry_count = retry_count or settings.RETRY_COUNT
        self.retry_delay = retry_delay or settings.RETRY_DELAY
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "CycloneTracker/1.0.0 (Educational Project)"
        })
        
        logger.info(
            f"APIClient initialized: timeout={self.timeout}s, "
            f"retry_count={self.retry_count}"
        )
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make GET request with retry logic.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            timeout: Request timeout (overrides default)
        
        Returns:
            Parsed JSON response
        
        Raises:
            ValidationError: If parameters are invalid
            RateLimitError: If rate limit exceeded (429)
            CustomTimeoutError: If request times out
            APIError: For other API errors
        """
        # Validate parameters
        if params:
            self._validate_params(params)
        
        # Use provided timeout or default
        request_timeout = timeout or self.timeout
        
        # Log request
        logger.info(f"API call: GET {url} with params {params}")
        
        # Retry loop
        last_exception = None
        for attempt in range(self.retry_count + 1):
            try:
                start_time = time.time()
                
                response = self.session.get(
                    url,
                    params=params,
                    timeout=request_timeout
                )
                
                elapsed = time.time() - start_time
                
                # Handle HTTP errors
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limit exceeded. Retry after {retry_after}s")
                    raise RateLimitError(
                        f"Rate limit exceeded. Retry after {retry_after} seconds"
                    )
                
                if response.status_code == 400:
                    error_msg = response.json().get("reason", "Bad request")
                    logger.error(f"Bad request (400): {error_msg}")
                    raise ValidationError(f"Bad request: {error_msg}")
                
                if response.status_code >= 500:
                    logger.error(f"Server error ({response.status_code})")
                    raise APIError(
                        f"Server error ({response.status_code}): {response.text[:200]}"
                    )
                
                response.raise_for_status()
                
                # Success
                logger.info(f"API call successful (status: 200, time: {elapsed:.2f}s)")
                return response.json()
            
            except requests.exceptions.Timeout as e:
                last_exception = CustomTimeoutError(
                    f"Request timeout after {request_timeout}s"
                )
                logger.warning(
                    f"Timeout on attempt {attempt + 1}/{self.retry_count + 1}"
                )
            
            except requests.exceptions.ConnectionError as e:
                last_exception = APIError(f"Connection failed: {e}")
                logger.warning(
                    f"Connection error on attempt {attempt + 1}/{self.retry_count + 1}: {e}"
                )
            
            except (RateLimitError, ValidationError) as e:
                # Don't retry on validation or rate limit errors
                raise
            
            except APIError as e:
                last_exception = e
                logger.warning(
                    f"API error on attempt {attempt + 1}/{self.retry_count + 1}: {e}"
                )
            
            # Calculate backoff delay
            if attempt < self.retry_count:
                delay = self._calculate_backoff_delay(attempt)
                logger.info(f"Retrying in {delay}s...")
                time.sleep(delay)
        
        # All retries exhausted
        logger.error(f"All {self.retry_count + 1} attempts failed")
        raise last_exception or APIError("Request failed after all retries")
    
    def _validate_params(self, params: Dict[str, Any]):
        """
        Validate request parameters.
        
        Args:
            params: Parameters to validate
        
        Raises:
            ValidationError: If parameters are invalid
        """
        if "latitude" in params:
            lat = params["latitude"]
            try:
                lat = float(lat)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Latitude must be a number, got: {type(lat).__name__}"
                )
            
            if not -90 <= lat <= 90:
                raise ValidationError(
                    f"Latitude must be between -90 and 90, got: {lat}"
                )
        
        if "longitude" in params:
            lon = params["longitude"]
            try:
                lon = float(lon)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Longitude must be a number, got: {type(lon).__name__}"
                )
            
            if not -180 <= lon <= 180:
                raise ValidationError(
                    f"Longitude must be between -180 and 180, got: {lon}"
                )
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        
        Formula: min(RETRY_DELAY * (2 ^ attempt), MAX_RETRY_DELAY)
        
        Args:
            attempt: Current attempt number (0-indexed)
        
        Returns:
            Delay in seconds
        """
        delay = self.retry_delay * (2 ** attempt)
        return min(delay, settings.MAX_RETRY_DELAY)
    
    def close(self):
        """Close HTTP session."""
        self.session.close()
        logger.info("APIClient session closed")
