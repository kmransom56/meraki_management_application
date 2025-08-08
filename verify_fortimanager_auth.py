#!/usr/bin/env python3
"""
FortiManager Authentication Verification
Test different authentication methods and verify credentials
"""
import requests
import json
import os
from dotenv import load_dotenv

# Apply SSL fixes
try:
    from ssl_universal_fix import apply_all_ssl_fixes
    apply_all_ssl_fixes(verbose=False)
    print("[Auth Verify] SSL fixes applied successfully")
except ImportError:
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning
    urllib3.disable_warnings(InsecureRequestWarning)
    print("[Auth Verify] Using manual SSL bypass")

# Load environment variables
load_dotenv()

def test_fortimanager_auth_methods(host, username, password, port=443):
    """Test different FortiManager authentication methods"""
    print(f"\nTesting authentication methods for {host}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    
    session = requests.Session()
    session.verify = False
    
    base_url = f"https://{host}:{port}"
    
    # Method 1: Standard JSON-RPC login
    print("\n1. Testing JSON-RPC login method...")
    try:
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
        
        response = session.post(f"{base_url}/jsonrpc", json=payload, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
                
                if 'result' in result and len(result['result']) > 0:
                    status = result['result'][0].get('status', {})
                    code = status.get('code')
                    message = status.get('message', 'No message')
                    
                    print(f"   Status Code: {code}")
                    print(f"   Status Message: {message}")
                    
                    if code == 0:
                        session_id = result.get('session')
                        print(f"   ✅ SUCCESS! Session ID: {session_id}")
                        return True, session_id, "json-rpc"
                    else:
                        print(f"   ❌ Authentication failed: {message}")
                else:
                    print(f"   ❌ Unexpected response format")
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response")
                print(f"   Raw response: {response.text[:200]}...")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Method 2: Try alternative login URL
    print("\n2. Testing alternative login URL...")
    try:
        payload = {
            "method": "exec",
            "params": [{
                "url": "/sys/login",
                "data": {
                    "user": username,
                    "passwd": password
                }
            }],
            "id": 1
        }
        
        response = session.post(f"{base_url}/jsonrpc", json=payload, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
                
                if 'result' in result and len(result['result']) > 0:
                    status = result['result'][0].get('status', {})
                    if status.get('code') == 0:
                        print(f"   ✅ Alternative login successful!")
                        return True, result.get('session'), "json-rpc-alt"
                    else:
                        print(f"   ❌ Alternative login failed: {status.get('message')}")
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Method 3: Check if web login works (to verify credentials)
    print("\n3. Testing web interface login...")
    try:
        # Try to access login page
        response = session.get(f"{base_url}/p/login/", timeout=30)
        print(f"   Login page status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Web interface accessible")
            
            # Try to find login form
            if 'login' in response.text.lower() or 'password' in response.text.lower():
                print(f"   ✅ Login form detected")
            else:
                print(f"   ⚠️ No login form found")
        else:
            print(f"   ❌ Web interface not accessible")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Method 4: Check API status/info endpoints
    print("\n4. Testing API status endpoints...")
    status_endpoints = ["/sys/status", "/api/v2/monitor/system/status", "/api/v2/cmdb/system/global"]
    
    for endpoint in status_endpoints:
        try:
            payload = {
                "method": "get",
                "params": [{"url": endpoint}],
                "id": 1
            }
            
            response = session.post(f"{base_url}/jsonrpc", json=payload, timeout=10)
            print(f"   {endpoint}: Status {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if 'result' in result:
                        status = result['result'][0].get('status', {})
                        if status.get('code') == 0:
                            print(f"     ✅ Endpoint accessible without auth")
                        elif status.get('code') == -11:
                            print(f"     🔒 Authentication required")
                        else:
                            print(f"     ❌ Error: {status.get('message', 'Unknown')}")
                except json.JSONDecodeError:
                    print(f"     ❌ Invalid JSON")
            
        except Exception as e:
            print(f"     ❌ Exception: {str(e)[:50]}...")
    
    return False, None, None

def main():
    """Test authentication for all FortiManager instances"""
    print("FortiManager Authentication Verification")
    print("=" * 50)
    
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
        print("❌ No FortiManager configurations found in environment")
        return
    
    print(f"Testing {len(fortimanagers)} FortiManager instances")
    
    results = {}
    
    for fm in fortimanagers:
        print(f"\n{'='*50}")
        print(f"TESTING {fm['name']} FORTIMANAGER")
        print(f"{'='*50}")
        
        success, session_id, method = test_fortimanager_auth_methods(
            fm['host'], fm['username'], fm['password']
        )
        
        results[fm['name']] = {
            'success': success,
            'session_id': session_id,
            'method': method
        }
    
    # Summary
    print(f"\n{'='*50}")
    print("AUTHENTICATION TEST SUMMARY")
    print(f"{'='*50}")
    
    successful = 0
    for site, result in results.items():
        if result['success']:
            print(f"✅ {site}: SUCCESS ({result['method']})")
            successful += 1
        else:
            print(f"❌ {site}: FAILED")
    
    print(f"\nResults: {successful}/{len(fortimanagers)} FortiManager instances authenticated successfully")
    
    if successful == 0:
        print("\n🔍 Troubleshooting suggestions:")
        print("1. Verify username/password are correct")
        print("2. Check if JSON-RPC API is enabled in FortiManager")
        print("3. Verify user has API access permissions")
        print("4. Check if user account is locked or disabled")
        print("5. Try logging into web interface manually to verify credentials")
        print("6. Check FortiManager logs for authentication attempts")
    else:
        print(f"\n🎉 {successful} FortiManager instance(s) working!")
        print("Your multi-instance FortiManager integration is ready!")

if __name__ == "__main__":
    main()
