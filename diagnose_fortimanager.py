#!/usr/bin/env python3
"""
FortiManager API Diagnostic Script
Helps troubleshoot FortiManager JSON-RPC API connectivity issues
"""
import requests
import json
import os
import socket
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging for detailed output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

def test_basic_connectivity(host, port=443):
    """Test basic TCP connectivity to FortiManager"""
    print(f"\n[1] Testing basic TCP connectivity to {host}:{port}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"[OK] TCP connection to {host}:{port} successful")
            return True
        else:
            print(f"[ERROR] TCP connection to {host}:{port} failed (error code: {result})")
            return False
    except Exception as e:
        print(f"[ERROR] TCP connectivity test failed: {str(e)}")
        return False

def test_ssl_connectivity(host, port=443):
    """Test SSL/TLS connectivity to FortiManager"""
    print(f"\n[2] Testing SSL/TLS connectivity to {host}:{port}")
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"[OK] SSL/TLS connection to {host}:{port} successful")
                print(f"   SSL Version: {ssock.version()}")
                print(f"   Cipher: {ssock.cipher()}")
                return True
    except Exception as e:
        print(f"[ERROR] SSL/TLS connectivity test failed: {str(e)}")
        return False

def test_http_connectivity(host, port=443):
    """Test basic HTTP/HTTPS connectivity to FortiManager"""
    print(f"\n[3] Testing HTTP/HTTPS connectivity to {host}:{port}")
    try:
        session = requests.Session()
        session.verify = False
        # Disable SSL warnings for this session
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Test basic HTTPS connection
        url = f"https://{host}:{port}/"
        response = session.get(url, timeout=10)
        
        print(f"[OK] HTTPS connection to {host}:{port} successful")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Server: {response.headers.get('Server', 'N/A')}")
        
        # Check if it looks like a FortiManager response
        if 'fortinet' in response.text.lower() or 'fortimanager' in response.text.lower():
            print(f"[OK] Response appears to be from FortiManager")
        else:
            print(f"[WARNING] Response may not be from FortiManager")
            
        return True
    except Exception as e:
        print(f"[ERROR] HTTP/HTTPS connectivity test failed: {str(e)}")
        return False

def test_jsonrpc_endpoint(host, port=443):
    """Test FortiManager JSON-RPC endpoint accessibility"""
    print(f"\n[4] Testing JSON-RPC endpoint accessibility")
    try:
        session = requests.Session()
        session.verify = False
        # Disable SSL warnings for this session
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Test JSON-RPC endpoint
        url = f"https://{host}:{port}/jsonrpc"
        
        # Try a simple ping or invalid request to see if endpoint responds
        test_payload = {
            "method": "get",
            "params": [{"url": "/sys/status"}],
            "id": 1
        }
        
        response = session.post(url, json=test_payload, timeout=10)
        
        print(f"[OK] JSON-RPC endpoint responded")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response is valid JSON")
                print(f"   Response preview: {json.dumps(result, indent=2)[:200]}...")
                
                # Check if it's a FortiManager JSON-RPC response
                if 'result' in result or 'error' in result:
                    print(f"[OK] Response appears to be valid JSON-RPC format")
                    return True
                else:
                    print(f"[WARNING] Response may not be valid JSON-RPC format")
                    return False
            except json.JSONDecodeError:
                print(f"[WARNING] Response is not valid JSON")
                print(f"   Raw response: {response.text[:200]}...")
                return False
        else:
            print(f"[WARNING] Non-200 status code from JSON-RPC endpoint")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"[ERROR] JSON-RPC endpoint test failed: {str(e)}")
        return False

def test_fortimanager_login(host, username, password, port=443):
    """Test FortiManager login with actual credentials"""
    print(f"\n[5] Testing FortiManager login with credentials")
    print(f"   Host: {host}:{port}")
    print(f"   Username: {username}")
    
    try:
        session = requests.Session()
        session.verify = False
        # Disable SSL warnings for this session
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        url = f"https://{host}:{port}/jsonrpc"
        
        payload = {
            "method": "exec",
            "params": [{
                "url": "/sys/login/user",
                "data": {
                    "user": username,
                    "passwd": password
                }
            }],
            "id": 1
        }
        
        print(f"   Sending login request...")
        response = session.post(url, json=payload, timeout=30)
        
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response JSON: {json.dumps(result, indent=2)}")
                
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    session_id = result.get('session')
                    print(f"[OK] Login successful!")
                    print(f"   Session ID: {session_id}")
                    return True, session_id
                else:
                    error_code = result.get('result', [{}])[0].get('status', {}).get('code', 'Unknown')
                    error_msg = result.get('result', [{}])[0].get('status', {}).get('message', 'Unknown error')
                    print(f"[ERROR] Login failed - Code: {error_code}, Message: {error_msg}")
                    return False, None
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid JSON response: {str(e)}")
                print(f"   Raw response: {response.text}")
                return False, None
        else:
            print(f"[ERROR] HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"[ERROR] Login test failed: {str(e)}")
        return False, None

def diagnose_fortimanager(site_name, host, username, password, port=443):
    """Run comprehensive FortiManager diagnostics"""
    print(f"\n{'='*60}")
    print(f"FORTIMANAGER DIAGNOSTIC - {site_name.upper()}")
    print(f"{'='*60}")
    print(f"Host: {host}:{port}")
    print(f"Username: {username}")
    
    results = {}
    
    # Test 1: Basic TCP connectivity
    results['tcp'] = test_basic_connectivity(host, port)
    
    # Test 2: SSL/TLS connectivity
    results['ssl'] = test_ssl_connectivity(host, port)
    
    # Test 3: HTTP/HTTPS connectivity
    results['http'] = test_http_connectivity(host, port)
    
    # Test 4: JSON-RPC endpoint
    results['jsonrpc'] = test_jsonrpc_endpoint(host, port)
    
    # Test 5: FortiManager login
    results['login'], session_id = test_fortimanager_login(host, username, password, port)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"DIAGNOSTIC SUMMARY - {site_name.upper()}")
    print(f"{'='*60}")
    
    for test, result in results.items():
        status = "[OK]" if result else "[FAILED]"
        print(f"{status} {test.upper()} Test")
    
    if all(results.values()):
        print(f"\n[SUCCESS] All tests passed for {site_name.upper()}!")
        print(f"FortiManager API should be working correctly.")
    else:
        print(f"\n[ISSUES DETECTED] Some tests failed for {site_name.upper()}")
        print(f"Review the detailed output above to identify the problem.")
    
    return results

def main():
    """Run diagnostics for all FortiManager instances"""
    print("FortiManager API Connectivity Diagnostics")
    print("="*60)
    
    # Get FortiManager configurations from environment
    fortimanagers = []
    
    if all([os.getenv('ARBYS_FORTIMANAGER_HOST'), os.getenv('ARBYS_USERNAME'), os.getenv('ARBYS_PASSWORD')]):
        fortimanagers.append({
            'name': 'arbys',
            'host': os.getenv('ARBYS_FORTIMANAGER_HOST'),
            'username': os.getenv('ARBYS_USERNAME'),
            'password': os.getenv('ARBYS_PASSWORD')
        })
    
    if all([os.getenv('BWW_FORTIMANAGER_HOST'), os.getenv('BWW_USERNAME'), os.getenv('BWW_PASSWORD')]):
        fortimanagers.append({
            'name': 'bww',
            'host': os.getenv('BWW_FORTIMANAGER_HOST'),
            'username': os.getenv('BWW_USERNAME'),
            'password': os.getenv('BWW_PASSWORD')
        })
    
    if all([os.getenv('SONIC_FORTIMANAGER_HOST'), os.getenv('SONIC_USERNAME'), os.getenv('SONIC_PASSWORD')]):
        fortimanagers.append({
            'name': 'sonic',
            'host': os.getenv('SONIC_FORTIMANAGER_HOST'),
            'username': os.getenv('SONIC_USERNAME'),
            'password': os.getenv('SONIC_PASSWORD')
        })
    
    if not fortimanagers:
        print("[ERROR] No FortiManager configurations found in environment variables")
        return
    
    print(f"Found {len(fortimanagers)} FortiManager configurations")
    
    all_results = {}
    for fm in fortimanagers:
        all_results[fm['name']] = diagnose_fortimanager(
            fm['name'], fm['host'], fm['username'], fm['password']
        )
    
    # Overall summary
    print(f"\n{'='*60}")
    print(f"OVERALL SUMMARY")
    print(f"{'='*60}")
    
    for site, results in all_results.items():
        success_count = sum(1 for r in results.values() if r)
        total_count = len(results)
        print(f"{site.upper()}: {success_count}/{total_count} tests passed")
    
    print(f"\nDiagnostics complete!")

if __name__ == "__main__":
    main()
