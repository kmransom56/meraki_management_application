#!/usr/bin/env python3
"""
FortiManager API Test with Complete SSL/TLS Bypass
Final test with all SSL verification completely disabled
"""
import requests
import json
import os
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv
import warnings

# Load environment variables
load_dotenv()

# Completely disable all SSL warnings and verification
urllib3.disable_warnings()
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
requests.packages.urllib3.disable_warnings()

def test_fortimanager_complete_bypass(host, username, password, port=443):
    """Test FortiManager with complete SSL/TLS bypass"""
    print(f"\nTesting FortiManager: {host}")
    print(f"Username: {username}")
    
    try:
        # Create session with complete SSL bypass
        session = requests.Session()
        session.verify = False
        
        # Create custom HTTPAdapter that completely ignores SSL
        from requests.adapters import HTTPAdapter
        from urllib3.poolmanager import PoolManager
        import ssl
        
        class NoSSLAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                # Create SSL context that ignores everything
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.set_ciphers('DEFAULT@SECLEVEL=1')
                
                kwargs['ssl_context'] = context
                return super().init_poolmanager(*args, **kwargs)
        
        # Mount the no-SSL adapter
        session.mount('https://', NoSSLAdapter())
        
        # Set additional headers that FortiManager might expect
        session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FortiManager-API-Client/1.0'
        })
        
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
        
        print(f"Connecting to: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Make the request with extended timeout
        response = session.post(url, json=payload, timeout=60)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response JSON: {json.dumps(result, indent=2)}")
                
                # Check for successful login
                if 'result' in result and len(result['result']) > 0:
                    status = result['result'][0].get('status', {})
                    if status.get('code') == 0:
                        session_id = result.get('session')
                        print(f"[SUCCESS] Login successful!")
                        print(f"Session ID: {session_id}")
                        return True, session_id, session
                    else:
                        error_code = status.get('code', 'Unknown')
                        error_msg = status.get('message', 'Unknown error')
                        print(f"[ERROR] Login failed - Code: {error_code}, Message: {error_msg}")
                        return False, None, None
                else:
                    print(f"[ERROR] Unexpected response format")
                    return False, None, None
                    
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid JSON response: {str(e)}")
                print(f"Raw response (first 500 chars): {response.text[:500]}")
                return False, None, None
        else:
            print(f"[ERROR] HTTP error: {response.status_code}")
            print(f"Response text (first 500 chars): {response.text[:500]}")
            return False, None, None
            
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] Request timeout: {str(e)}")
        return False, None, None
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection error: {str(e)}")
        return False, None, None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False, None, None

def test_device_retrieval(host, session_id, session, port=443):
    """Test device retrieval with established session"""
    print(f"\nTesting Device Retrieval: {host}")
    
    try:
        url = f"https://{host}:{port}/jsonrpc"
        
        payload = {
            "method": "get",
            "params": [{
                "url": "/dvmdb/device"
            }],
            "session": session_id,
            "id": 2
        }
        
        print(f"Requesting device list...")
        
        response = session.post(url, json=payload, timeout=60)
        
        print(f"Device Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Device Response: {json.dumps(result, indent=2)[:1000]}...")
                
                if 'result' in result and len(result['result']) > 0:
                    status = result['result'][0].get('status', {})
                    if status.get('code') == 0:
                        devices = result['result'][0].get('data', [])
                        print(f"[SUCCESS] Found {len(devices)} devices")
                        
                        # Show device details
                        for i, device in enumerate(devices[:5]):
                            name = device.get('name', 'Unknown')
                            ip = device.get('ip', 'N/A')
                            model = device.get('platform_str', device.get('model', 'N/A'))
                            status = 'Online' if device.get('conn_status') == 1 else 'Offline'
                            print(f"  Device {i+1}: {name} ({ip}) - {model} - {status}")
                        
                        if len(devices) > 5:
                            print(f"  ... and {len(devices) - 5} more devices")
                        
                        return True, devices
                    else:
                        error_code = status.get('code', 'Unknown')
                        error_msg = status.get('message', 'Unknown error')
                        print(f"[ERROR] Device retrieval failed - Code: {error_code}, Message: {error_msg}")
                        return False, []
                else:
                    print(f"[ERROR] Unexpected device response format")
                    return False, []
                    
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid JSON in device response: {str(e)}")
                return False, []
        else:
            print(f"[ERROR] Device retrieval HTTP error: {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"[ERROR] Device retrieval error: {str(e)}")
        return False, []

def main():
    """Test all FortiManager instances with complete SSL bypass"""
    print("FortiManager API Test - Complete SSL Bypass")
    print("=" * 60)
    
    # Get FortiManager configurations
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
        print("[ERROR] No FortiManager configurations found")
        return
    
    print(f"Testing {len(fortimanagers)} FortiManager instances")
    
    results = {}
    
    for fm in fortimanagers:
        print(f"\n{'='*60}")
        print(f"TESTING {fm['name']} FORTIMANAGER")
        print(f"{'='*60}")
        
        # Test login
        login_success, session_id, session = test_fortimanager_complete_bypass(
            fm['host'], fm['username'], fm['password']
        )
        
        results[fm['name']] = {
            'login': login_success,
            'devices': 0,
            'device_list': []
        }
        
        if login_success and session_id and session:
            # Test device retrieval
            device_success, devices = test_device_retrieval(
                fm['host'], session_id, session
            )
            
            if device_success:
                results[fm['name']]['devices'] = len(devices)
                results[fm['name']]['device_list'] = devices
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"FINAL TEST RESULTS")
    print(f"{'='*60}")
    
    total_success = 0
    total_devices = 0
    
    for site, result in results.items():
        status = "[SUCCESS]" if result['login'] else "[FAILED]"
        print(f"{status} {site}:")
        print(f"  Login: {result['login']}")
        print(f"  Devices: {result['devices']}")
        
        if result['login']:
            total_success += 1
            total_devices += result['devices']
    
    print(f"\nOverall Results:")
    print(f"  Working FortiManagers: {total_success}/{len(fortimanagers)}")
    print(f"  Total Devices Found: {total_devices}")
    
    if total_success > 0:
        print(f"\n[SUCCESS] {total_success} FortiManager instance(s) working!")
        print("Your multi-instance FortiManager platform is ready!")
        
        if total_success == len(fortimanagers):
            print("All FortiManager instances are fully operational!")
        else:
            print(f"Note: {len(fortimanagers) - total_success} instance(s) need attention.")
    else:
        print("\n[ISSUE] No FortiManager instances are responding correctly.")
        print("This may indicate:")
        print("1. JSON-RPC API is not enabled on FortiManager")
        print("2. Different authentication method required")
        print("3. Network/firewall restrictions")
        print("4. Different API endpoint or port")

if __name__ == "__main__":
    main()
