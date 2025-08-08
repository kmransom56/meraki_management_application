#!/usr/bin/env python3
"""
FortiManager API Test with Proper SSL Handling
Tests FortiManager connectivity with self-signed certificates properly disabled
"""
import requests
import json
import os
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Completely disable SSL warnings and verification
urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Create a custom SSL context that ignores all certificate issues
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def test_fortimanager_login_fixed(host, username, password, port=443):
    """Test FortiManager login with proper SSL handling for self-signed certificates"""
    print(f"\nTesting FortiManager Login - {host}")
    print(f"Username: {username}")
    print(f"Port: {port}")
    
    try:
        # Create session with all SSL verification disabled
        session = requests.Session()
        session.verify = False
        
        # Create custom adapter that completely ignores SSL
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        from urllib3.poolmanager import PoolManager
        
        class SSLIgnoreAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                kwargs['ssl_context'] = ssl_context
                return super().init_poolmanager(*args, **kwargs)
        
        # Mount the custom adapter
        session.mount('https://', SSLIgnoreAdapter())
        
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
        
        print(f"Sending login request to: {url}")
        
        response = session.post(url, json=payload, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response JSON: {json.dumps(result, indent=2)}")
                
                # Check if login was successful
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    session_id = result.get('session')
                    print(f"[SUCCESS] Login successful!")
                    print(f"Session ID: {session_id}")
                    return True, session_id
                else:
                    error_code = result.get('result', [{}])[0].get('status', {}).get('code', 'Unknown')
                    error_msg = result.get('result', [{}])[0].get('status', {}).get('message', 'Unknown error')
                    print(f"[ERROR] Login failed - Code: {error_code}, Message: {error_msg}")
                    return False, None
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid JSON response: {str(e)}")
                print(f"Raw response: {response.text}")
                return False, None
        else:
            print(f"[ERROR] HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"[ERROR] Login test failed: {str(e)}")
        return False, None

def test_device_list(host, username, password, session_id, port=443):
    """Test getting device list from FortiManager"""
    print(f"\nTesting Device List Retrieval - {host}")
    
    try:
        # Create session with SSL disabled
        session = requests.Session()
        session.verify = False
        
        class SSLIgnoreAdapter(requests.adapters.HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                kwargs['ssl_context'] = ssl_context
                return super().init_poolmanager(*args, **kwargs)
        
        session.mount('https://', SSLIgnoreAdapter())
        
        url = f"https://{host}:{port}/jsonrpc"
        
        payload = {
            "method": "get",
            "params": [{
                "url": "/dvmdb/device"
            }],
            "session": session_id,
            "id": 1
        }
        
        print(f"Sending device list request...")
        
        response = session.post(url, json=payload, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    devices = result.get('result', [{}])[0].get('data', [])
                    print(f"[SUCCESS] Retrieved {len(devices)} devices")
                    
                    # Show first few devices
                    for i, device in enumerate(devices[:3]):
                        print(f"  Device {i+1}: {device.get('name', 'Unknown')} ({device.get('ip', 'N/A')})")
                    
                    if len(devices) > 3:
                        print(f"  ... and {len(devices) - 3} more devices")
                    
                    return True, devices
                else:
                    error_code = result.get('result', [{}])[0].get('status', {}).get('code', 'Unknown')
                    error_msg = result.get('result', [{}])[0].get('status', {}).get('message', 'Unknown error')
                    print(f"[ERROR] Device list failed - Code: {error_code}, Message: {error_msg}")
                    return False, []
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid JSON response: {str(e)}")
                return False, []
        else:
            print(f"[ERROR] HTTP error: {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"[ERROR] Device list test failed: {str(e)}")
        return False, []

def main():
    """Test all FortiManager instances with proper SSL handling"""
    print("FortiManager API Test with SSL Fix")
    print("=" * 50)
    
    # Get FortiManager configurations from environment
    fortimanagers = []
    
    if all([os.getenv('ARBYS_FORTIMANAGER_HOST'), os.getenv('ARBYS_USERNAME'), os.getenv('ARBYS_PASSWORD')]):
        fortimanagers.append({
            'name': 'ARBYS',
            'host': os.getenv('ARBYS_FORTIMANAGER_HOST'),
            'username': os.getenv('ARBYS_USERNAME'),
            'password': os.getenv('ARBYS_PASSWORD')
        })
    
    if all([os.getenv('BWW_FORTIMANAGER_HOST'), os.getenv('BWW_USERNAME'), os.getenv('BWW_PASSWORD')]):
        fortimanagers.append({
            'name': 'BWW',
            'host': os.getenv('BWW_FORTIMANAGER_HOST'),
            'username': os.getenv('BWW_USERNAME'),
            'password': os.getenv('BWW_PASSWORD')
        })
    
    if all([os.getenv('SONIC_FORTIMANAGER_HOST'), os.getenv('SONIC_USERNAME'), os.getenv('SONIC_PASSWORD')]):
        fortimanagers.append({
            'name': 'SONIC',
            'host': os.getenv('SONIC_FORTIMANAGER_HOST'),
            'username': os.getenv('SONIC_USERNAME'),
            'password': os.getenv('SONIC_PASSWORD')
        })
    
    if not fortimanagers:
        print("[ERROR] No FortiManager configurations found in environment variables")
        return
    
    print(f"Found {len(fortimanagers)} FortiManager configurations")
    
    results = {}
    
    for fm in fortimanagers:
        print(f"\n{'='*50}")
        print(f"TESTING {fm['name']} FORTIMANAGER")
        print(f"{'='*50}")
        
        # Test login
        login_success, session_id = test_fortimanager_login_fixed(
            fm['host'], fm['username'], fm['password']
        )
        
        results[fm['name']] = {
            'login': login_success,
            'devices': 0
        }
        
        if login_success and session_id:
            # Test device retrieval
            device_success, devices = test_device_list(
                fm['host'], fm['username'], fm['password'], session_id
            )
            
            if device_success:
                results[fm['name']]['devices'] = len(devices)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"FINAL RESULTS")
    print(f"{'='*50}")
    
    total_success = 0
    total_devices = 0
    
    for site, result in results.items():
        status = "[SUCCESS]" if result['login'] else "[FAILED]"
        print(f"{status} {site}: Login={result['login']}, Devices={result['devices']}")
        
        if result['login']:
            total_success += 1
            total_devices += result['devices']
    
    print(f"\nSummary: {total_success}/{len(fortimanagers)} FortiManager instances working")
    print(f"Total devices found: {total_devices}")
    
    if total_success == len(fortimanagers):
        print("\n[SUCCESS] All FortiManager instances are working correctly!")
        print("The multi-instance FortiManager platform is ready for production!")
    else:
        print(f"\n[PARTIAL SUCCESS] {total_success} out of {len(fortimanagers)} instances working")
        print("Check the detailed output above for specific issues.")

if __name__ == "__main__":
    main()
