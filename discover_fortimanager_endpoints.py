#!/usr/bin/env python3
"""
FortiManager Endpoint Discovery
Check what endpoints and APIs are available on FortiManager instances
"""
import requests
import json
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv
import socket

# Load environment variables
load_dotenv()

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

def test_endpoint_accessibility(host, port=443):
    """Test various FortiManager endpoints to see what's available"""
    print(f"\nDiscovering endpoints on {host}:{port}")
    
    # Create session with SSL verification disabled
    session = requests.Session()
    session.verify = False
    
    endpoints_to_test = [
        "/",
        "/jsonrpc",
        "/api/v2/",
        "/api/",
        "/login",
        "/logincheck",
        "/remote_login",
        "/p/login/",
        "/ng/login",
        "/fmglogin"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        url = f"https://{host}:{port}{endpoint}"
        try:
            print(f"Testing: {endpoint}")
            response = session.get(url, timeout=10, allow_redirects=False)
            
            results[endpoint] = {
                'status_code': response.status_code,
                'content_type': response.headers.get('Content-Type', 'N/A'),
                'content_length': len(response.content),
                'headers': dict(response.headers),
                'accessible': True
            }
            
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"  Content-Length: {len(response.content)}")
            
            # Check if response contains FortiManager indicators
            content_lower = response.text.lower()
            if any(indicator in content_lower for indicator in ['fortimanager', 'fortinet', 'fmg']):
                print(f"  [FortiManager detected in response]")
                results[endpoint]['fortimanager_detected'] = True
            
        except requests.exceptions.SSLError as e:
            print(f"  SSL Error: {str(e)}")
            results[endpoint] = {'error': f'SSL Error: {str(e)}', 'accessible': False}
        except requests.exceptions.ConnectionError as e:
            print(f"  Connection Error: {str(e)}")
            results[endpoint] = {'error': f'Connection Error: {str(e)}', 'accessible': False}
        except requests.exceptions.Timeout as e:
            print(f"  Timeout: {str(e)}")
            results[endpoint] = {'error': f'Timeout: {str(e)}', 'accessible': False}
        except Exception as e:
            print(f"  Error: {str(e)}")
            results[endpoint] = {'error': str(e), 'accessible': False}
    
    return results

def test_json_rpc_methods(host, port=443):
    """Test different JSON-RPC methods and endpoints"""
    print(f"\nTesting JSON-RPC methods on {host}:{port}")
    
    session = requests.Session()
    session.verify = False
    
    # Different JSON-RPC endpoints to try
    jsonrpc_endpoints = [
        "/jsonrpc",
        "/json-rpc",
        "/rpc",
        "/api/jsonrpc",
        "/api/v2/jsonrpc"
    ]
    
    # Different methods to try
    test_methods = [
        {
            "method": "get",
            "params": [{"url": "/sys/status"}],
            "id": 1
        },
        {
            "method": "exec",
            "params": [{"url": "/sys/status"}],
            "id": 1
        },
        {
            "method": "get",
            "params": [{"url": "/cli/global/system/status"}],
            "id": 1
        }
    ]
    
    for endpoint in jsonrpc_endpoints:
        url = f"https://{host}:{port}{endpoint}"
        print(f"\nTesting JSON-RPC endpoint: {endpoint}")
        
        for method_data in test_methods:
            try:
                print(f"  Method: {method_data['method']}")
                response = session.post(url, json=method_data, timeout=10)
                
                print(f"    Status: {response.status_code}")
                print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        print(f"    Response: {json.dumps(result, indent=4)[:200]}...")
                        
                        # Check if it looks like a valid FortiManager response
                        if 'result' in result or 'error' in result:
                            print(f"    [Valid JSON-RPC response detected]")
                            return True, endpoint, method_data
                    except json.JSONDecodeError:
                        print(f"    Non-JSON response: {response.text[:100]}...")
                else:
                    print(f"    Response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"    Error: {str(e)}")
    
    return False, None, None

def check_fortimanager_version(host, port=443):
    """Try to determine FortiManager version and capabilities"""
    print(f"\nChecking FortiManager version/info on {host}:{port}")
    
    session = requests.Session()
    session.verify = False
    
    try:
        # Try to get the main page and look for version info
        response = session.get(f"https://{host}:{port}/", timeout=10)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Look for version indicators
            version_indicators = ['version', 'build', 'fortios', 'fortimanager']
            found_info = []
            
            for indicator in version_indicators:
                if indicator in content:
                    # Try to extract version info
                    lines = content.split('\n')
                    for line in lines:
                        if indicator in line.lower():
                            found_info.append(line.strip()[:100])
            
            if found_info:
                print("Found version/build information:")
                for info in found_info[:5]:  # Show first 5 matches
                    print(f"  {info}")
            else:
                print("No version information found in main page")
                
        # Check for API documentation or help endpoints
        help_endpoints = ["/help", "/api", "/api/help", "/docs"]
        for endpoint in help_endpoints:
            try:
                response = session.get(f"https://{host}:{port}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"Found accessible endpoint: {endpoint}")
            except:
                pass
                
    except Exception as e:
        print(f"Error checking version: {str(e)}")

def main():
    """Discover FortiManager endpoints and capabilities"""
    print("FortiManager Endpoint Discovery")
    print("=" * 50)
    
    # Get FortiManager hosts from environment
    hosts = []
    if os.getenv('ARBYS_FORTIMANAGER_HOST'):
        hosts.append(('ARBYS', os.getenv('ARBYS_FORTIMANAGER_HOST')))
    if os.getenv('BWW_FORTIMANAGER_HOST'):
        hosts.append(('BWW', os.getenv('BWW_FORTIMANAGER_HOST')))
    if os.getenv('SONIC_FORTIMANAGER_HOST'):
        hosts.append(('SONIC', os.getenv('SONIC_FORTIMANAGER_HOST')))
    
    if not hosts:
        print("No FortiManager hosts found in environment")
        return
    
    for name, host in hosts:
        print(f"\n{'='*50}")
        print(f"DISCOVERING {name} FORTIMANAGER: {host}")
        print(f"{'='*50}")
        
        # Test basic connectivity
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, 443))
            sock.close()
            
            if result == 0:
                print(f"[OK] TCP connection to {host}:443 successful")
            else:
                print(f"[ERROR] Cannot connect to {host}:443")
                continue
        except Exception as e:
            print(f"[ERROR] Connection test failed: {str(e)}")
            continue
        
        # Discover endpoints
        endpoint_results = test_endpoint_accessibility(host)
        
        # Test JSON-RPC
        jsonrpc_success, working_endpoint, working_method = test_json_rpc_methods(host)
        
        # Check version info
        check_fortimanager_version(host)
        
        # Summary for this host
        print(f"\nSUMMARY FOR {name}:")
        accessible_endpoints = [ep for ep, data in endpoint_results.items() if data.get('accessible', False)]
        print(f"  Accessible endpoints: {len(accessible_endpoints)}")
        print(f"  JSON-RPC working: {jsonrpc_success}")
        if jsonrpc_success:
            print(f"  Working endpoint: {working_endpoint}")
            print(f"  Working method: {working_method['method']}")
    
    print(f"\n{'='*50}")
    print("DISCOVERY COMPLETE")
    print(f"{'='*50}")
    print("\nNext steps:")
    print("1. Check if JSON-RPC API is enabled in FortiManager settings")
    print("2. Verify API user permissions and authentication method")
    print("3. Consider using REST API if JSON-RPC is not available")
    print("4. Check FortiManager documentation for API configuration")

if __name__ == "__main__":
    main()
