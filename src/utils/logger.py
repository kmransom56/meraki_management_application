"""
Enhanced logging setup for the Meraki CLI tool.
Provides detailed logging for debugging API issues and SSL problems.
"""
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


def setup_logger(name: str = __name__, 
                log_level: str = 'INFO',
                log_file: Optional[str] = None,
                console_output: bool = True) -> logging.Logger:
    """
    Set up enhanced logging with both file and console output.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console_output: Whether to output to console
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Rotating file handler (10MB max, 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_api_logger() -> logging.Logger:
    """Set up logger specifically for API operations."""
    log_dir = os.path.join(os.getcwd(), 'logs')
    log_file = os.path.join(log_dir, 'api.log')
    
    return setup_logger(
        name='meraki_api',
        log_level='DEBUG',
        log_file=log_file,
        console_output=True
    )


def setup_ssl_logger() -> logging.Logger:
    """Set up logger specifically for SSL operations."""
    log_dir = os.path.join(os.getcwd(), 'logs')
    log_file = os.path.join(log_dir, 'ssl.log')
    
    return setup_logger(
        name='ssl_handler',
        log_level='DEBUG',
        log_file=log_file,
        console_output=True
    )


def setup_web_logger() -> logging.Logger:
    """Set up logger specifically for web application."""
    log_dir = os.path.join(os.getcwd(), 'logs')
    log_file = os.path.join(log_dir, 'web.log')
    
    return setup_logger(
        name='web_app',
        log_level='INFO',
        log_file=log_file,
        console_output=True
    )


def log_api_request(logger: logging.Logger, method: str, url: str, 
                   headers: dict = None, data: dict = None):
    """Log API request details."""
    logger.info(f"API Request: {method} {url}")
    
    if headers:
        # Don't log sensitive headers
        safe_headers = {k: v for k, v in headers.items() 
                       if k.lower() not in ['authorization', 'x-cisco-meraki-api-key']}
        logger.debug(f"Request Headers: {safe_headers}")
    
    if data:
        logger.debug(f"Request Data: {data}")


def log_api_response(logger: logging.Logger, response, duration: float = None):
    """Log API response details."""
    logger.info(f"API Response: {response.status_code} {response.reason}")
    
    if duration:
        logger.info(f"Request Duration: {duration:.2f}s")
    
    logger.debug(f"Response Headers: {dict(response.headers)}")
    
    # Log response body (truncated if too long)
    try:
        response_text = response.text
        if len(response_text) > 500:
            response_text = response_text[:500] + "... (truncated)"
        logger.debug(f"Response Body: {response_text}")
    except Exception as e:
        logger.debug(f"Could not log response body: {e}")


def log_ssl_error(logger: logging.Logger, error: Exception, url: str):
    """Log SSL error details."""
    logger.error(f"SSL Error for {url}: {error}")
    logger.debug(f"SSL Error Type: {type(error)}")
    logger.debug(f"SSL Error Details: {str(error)}")


def log_network_topology(logger: logging.Logger, devices: list, clients: list, links: list):
    """Log network topology information for debugging."""
    logger.info(f"Network Topology Summary:")
    logger.info(f"  - Devices: {len(devices)}")
    logger.info(f"  - Clients: {len(clients)}")
    logger.info(f"  - Links: {len(links)}")
    
    # Log device types
    device_types = {}
    for device in devices:
        device_type = device.get('productType', 'unknown')
        device_types[device_type] = device_types.get(device_type, 0) + 1
    
    logger.info(f"Device Types: {device_types}")
    
    # Log client connection status
    connected_clients = sum(1 for client in clients if client.get('recentDeviceSerial'))
    logger.info(f"Connected Clients: {connected_clients}/{len(clients)}")


class RequestLogger:
    """Context manager for logging API requests."""
    
    def __init__(self, logger: logging.Logger, method: str, url: str):
        self.logger = logger
        self.method = method
        self.url = url
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.method} request to {self.url}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(f"Request failed after {duration:.2f}s: {exc_val}")
        else:
            self.logger.info(f"Request completed in {duration:.2f}s")
        
        return False  # Don't suppress exceptions
