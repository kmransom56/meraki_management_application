"""
Centralized error handling for the Meraki CLI tool.
"""
import logging
from typing import Optional, Dict, Any
from functools import wraps


class MerakiAPIError(Exception):
    """Custom exception for Meraki API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class SSLError(Exception):
    """Custom exception for SSL-related errors."""
    pass


class NetworkError(Exception):
    """Custom exception for network-related errors."""
    pass


def handle_api_errors(func):
    """Decorator to handle API errors consistently."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper


def log_api_response(response, logger):
    """Log API response details for debugging."""
    logger.debug(f"Response Status: {response.status_code}")
    logger.debug(f"Response Headers: {dict(response.headers)}")
    
    # Log response body (truncated if too long)
    try:
        response_text = response.text
        if len(response_text) > 1000:
            response_text = response_text[:1000] + "... (truncated)"
        logger.debug(f"Response Body: {response_text}")
    except Exception:
        logger.debug("Could not log response body")


def handle_rate_limit(response, logger):
    """Handle rate limiting from Meraki API."""
    if response.status_code == 429:
        retry_after = response.headers.get('Retry-After', '60')
        logger.warning(f"Rate limited. Retry after {retry_after} seconds")
        return int(retry_after)
    return None


def format_error_message(error: Exception) -> str:
    """Format error messages for user display."""
    if isinstance(error, MerakiAPIError):
        if error.status_code == 404:
            return "Resource not found. Please check your network/organization ID."
        elif error.status_code == 401:
            return "Authentication failed. Please check your API key."
        elif error.status_code == 403:
            return "Access forbidden. Check your API key permissions."
        elif error.status_code == 429:
            return "Rate limit exceeded. Please wait before making more requests."
        else:
            return f"API Error ({error.status_code}): {error.message}"
    
    elif isinstance(error, SSLError):
        return "SSL certificate verification failed. Check your network connection."
    
    elif isinstance(error, NetworkError):
        return "Network connection error. Please check your internet connection."
    
    else:
        return f"Unexpected error: {str(error)}"
