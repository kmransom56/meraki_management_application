"""
SSL certificate utilities and helper functions.
Addresses SSL certificate verification issues with the Meraki API.
"""
import ssl
import certifi
import socket
import logging
from typing import Optional, Tuple
from urllib.parse import urlparse


def create_ssl_context(verify: bool = True) -> ssl.SSLContext:
    """
    Create a properly configured SSL context.
    
    Args:
        verify: Whether to verify SSL certificates
    
    Returns:
        Configured SSL context
    """
    if verify:
        # Create default context with certificate verification
        context = ssl.create_default_context(cafile=certifi.where())
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Set modern security settings
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
    else:
        # Create context without verification (for debugging only)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    
    return context


def test_ssl_connection(hostname: str, port: int = 443, timeout: int = 10) -> Tuple[bool, Optional[str]]:
    """
    Test SSL connection to a hostname.
    
    Args:
        hostname: Target hostname
        port: Target port (default 443)
        timeout: Connection timeout in seconds
    
    Returns:
        Tuple of (success, error_message)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Create SSL context
        context = create_ssl_context(verify=True)
        
        # Test connection
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                logger.info(f"SSL connection to {hostname}:{port} successful")
                logger.debug(f"SSL version: {ssock.version()}")
                logger.debug(f"Cipher: {ssock.cipher()}")
                return True, None
                
    except ssl.SSLCertVerificationError as e:
        error_msg = f"SSL certificate verification failed: {e}"
        logger.error(error_msg)
        return False, error_msg
        
    except ssl.SSLError as e:
        error_msg = f"SSL error: {e}"
        logger.error(error_msg)
        return False, error_msg
        
    except socket.timeout:
        error_msg = f"Connection timeout to {hostname}:{port}"
        logger.error(error_msg)
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg)
        return False, error_msg


def get_certificate_info(hostname: str, port: int = 443) -> Optional[dict]:
    """
    Get certificate information for a hostname.
    
    Args:
        hostname: Target hostname
        port: Target port (default 443)
    
    Returns:
        Certificate information dictionary or None if failed
    """
    logger = logging.getLogger(__name__)
    
    try:
        context = ssl.create_default_context()
        
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                cert_info = {
                    'subject': dict(x[0] for x in cert['subject']),
                    'issuer': dict(x[0] for x in cert['issuer']),
                    'version': cert['version'],
                    'serial_number': cert['serialNumber'],
                    'not_before': cert['notBefore'],
                    'not_after': cert['notAfter'],
                    'signature_algorithm': cert.get('signatureAlgorithm'),
                    'dns_names': []
                }
                
                # Extract DNS names from SAN extension
                for extension in cert.get('subjectAltName', []):
                    if extension[0] == 'DNS':
                        cert_info['dns_names'].append(extension[1])
                
                logger.info(f"Retrieved certificate info for {hostname}")
                return cert_info
                
    except Exception as e:
        logger.error(f"Failed to get certificate info for {hostname}: {e}")
        return None


def validate_meraki_api_ssl() -> bool:
    """
    Validate SSL connection to Meraki API endpoints.
    
    Returns:
        True if SSL validation passes, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    meraki_endpoints = [
        'api.meraki.com',
        'dashboard.meraki.com'
    ]
    
    all_valid = True
    
    for endpoint in meraki_endpoints:
        logger.info(f"Testing SSL connection to {endpoint}")
        success, error = test_ssl_connection(endpoint)
        
        if success:
            logger.info(f"✓ SSL connection to {endpoint} successful")
        else:
            logger.error(f"✗ SSL connection to {endpoint} failed: {error}")
            all_valid = False
    
    return all_valid


def diagnose_ssl_issues(url: str) -> dict:
    """
    Diagnose SSL issues for a given URL.
    
    Args:
        url: Target URL to diagnose
    
    Returns:
        Dictionary with diagnosis results
    """
    logger = logging.getLogger(__name__)
    parsed = urlparse(url)
    hostname = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    
    diagnosis = {
        'url': url,
        'hostname': hostname,
        'port': port,
        'ssl_test': None,
        'certificate_info': None,
        'recommendations': []
    }
    
    if parsed.scheme != 'https':
        diagnosis['recommendations'].append('URL is not using HTTPS')
        return diagnosis
    
    # Test SSL connection
    success, error = test_ssl_connection(hostname, port)
    diagnosis['ssl_test'] = {
        'success': success,
        'error': error
    }
    
    if not success:
        diagnosis['recommendations'].append('SSL connection failed - check network connectivity')
        diagnosis['recommendations'].append('Consider using requests with verify=False for debugging (not recommended for production)')
    
    # Get certificate info
    cert_info = get_certificate_info(hostname, port)
    diagnosis['certificate_info'] = cert_info
    
    if cert_info:
        # Check certificate validity
        from datetime import datetime
        try:
            not_after = datetime.strptime(cert_info['not_after'], '%b %d %H:%M:%S %Y %Z')
            if not_after < datetime.now():
                diagnosis['recommendations'].append('Certificate has expired')
        except:
            pass
    
    # Check if certifi bundle is up to date
    try:
        cert_bundle_path = certifi.where()
        logger.info(f"Using certificate bundle: {cert_bundle_path}")
    except Exception as e:
        diagnosis['recommendations'].append(f'Issue with certificate bundle: {e}')
    
    return diagnosis
