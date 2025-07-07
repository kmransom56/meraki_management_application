"""
SSL Diagnostics utility for Cisco Meraki CLI.
Run this to diagnose SSL certificate issues.
"""
import ssl
import socket
import certifi
import requests
import logging
from urllib.parse import urlparse

def test_ssl_connectivity():
    """Test SSL connectivity to Meraki API endpoints."""
    
    print("🔍 SSL Connectivity Diagnostics")
    print("=" * 50)
    
    endpoints = [
        'api.meraki.com',
        'dashboard.meraki.com'
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Testing {endpoint}...")
        
        # Test SSL connection
        success, error = test_ssl_connection(endpoint, 443)
        if success:
            print(f"  ✅ SSL connection successful")
            
            # Get certificate info
            cert_info = get_certificate_info(endpoint)
            if cert_info:
                print(f"  📋 Certificate issuer: {cert_info.get('issuer', {}).get('organizationName', 'Unknown')}")
                print(f"  📅 Valid until: {cert_info.get('notAfter', 'Unknown')}")
        else:
            print(f"  ❌ SSL connection failed: {error}")
    
    # Test API request
    print(f"\n🔧 Testing API request...")
    test_api_request()
    
    print(f"\n📋 Certificate bundle location: {certifi.where()}")

def test_ssl_connection(hostname, port=443, timeout=10):
    """Test SSL connection to hostname."""
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                return True, None
    except Exception as e:
        return False, str(e)

def get_certificate_info(hostname, port=443):
    """Get certificate information."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                return ssock.getpeercert()
    except Exception:
        return None

def test_api_request():
    """Test a simple API request."""
    try:
        # Test with verification
        response = requests.get(
            'https://api.meraki.com/api/v1/organizations',
            headers={'X-Cisco-Meraki-API-Key': 'test'},
            timeout=10,
            verify=certifi.where()
        )
        print("  ✅ HTTPS request with verification successful")
    except requests.exceptions.SSLError as e:
        print(f"  ⚠️  HTTPS request with verification failed: SSL Error")
        
        # Test without verification
        try:
            response = requests.get(
                'https://api.meraki.com/api/v1/organizations',
                headers={'X-Cisco-Meraki-API-Key': 'test'},
                timeout=10,
                verify=False
            )
            print("  ✅ HTTPS request without verification successful")
        except Exception as e2:
            print(f"  ❌ HTTPS request without verification failed: {e2}")
    except Exception as e:
        print(f"  ❌ HTTPS request failed: {e}")

if __name__ == "__main__":
    test_ssl_connectivity()
