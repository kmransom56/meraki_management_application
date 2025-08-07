#!/usr/bin/env python3
"""
Test script to demonstrate FortiGate integration with Meraki topology visualization
This script will add sample FortiGate devices to show multi-vendor topology
"""

import requests
import json
import sys

def test_fortigate_integration():
    """Test FortiGate integration by adding sample devices"""
    
    # Base URL for the web application
    base_url = "http://localhost:5000"
    
    # Sample FortiGate configuration
    sample_fortigate_config = {
        "type": "direct",
        "fortigates": [
            {
                "name": "Main-FortiGate-FW",
                "host": "192.168.1.1",
                "api_key": "sample_api_key_123"
            },
            {
                "name": "Branch-FortiGate-FW",
                "host": "10.0.0.1", 
                "api_key": "sample_api_key_456"
            }
        ]
    }
    
    print("🔥 Testing FortiGate Integration with Meraki Topology")
    print("=" * 60)
    
    # Test 1: Configure FortiGate devices
    print("\n1. Configuring FortiGate devices...")
    try:
        response = requests.post(
            f"{base_url}/api/fortigate/configure",
            json=sample_fortigate_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ FortiGate configuration successful!")
            print(f"   Type: {result.get('type')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ FortiGate configuration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to web application.")
        print("   Make sure the comprehensive web app is running on localhost:5000")
        print("   Run: python comprehensive_web_app.py")
        return False
    except Exception as e:
        print(f"❌ Error configuring FortiGate: {e}")
        return False
    
    # Test 2: Test FortiGate connections
    print("\n2. Testing FortiGate connections...")
    try:
        response = requests.post(f"{base_url}/api/fortigate/test")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Connection test completed!")
            print(f"   Total tested: {result.get('total_tested', 0)}")
            
            for test_result in result.get('results', []):
                status_icon = "✅" if test_result['status'] == 'connected' else "❌"
                print(f"   {status_icon} {test_result['name']} ({test_result['host']}) - {test_result['status']}")
        else:
            print(f"❌ Connection test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing connections: {e}")
    
    # Test 3: Get FortiGate devices
    print("\n3. Retrieving FortiGate devices...")
    try:
        response = requests.get(f"{base_url}/api/fortigate/devices")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {result.get('total', 0)} FortiGate devices")
            
            for device in result.get('devices', []):
                print(f"   🔥 {device.get('name')} - {device.get('host')}")
                print(f"      Serial: {device.get('serial', 'N/A')}")
                print(f"      Platform: {device.get('platform_str', 'N/A')}")
        else:
            print(f"❌ Device retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error retrieving devices: {e}")
    
    # Test 4: Test multi-vendor topology endpoint
    print("\n4. Testing multi-vendor topology endpoint...")
    try:
        # Use a sample network ID
        network_id = "L_123456789"
        response = requests.get(f"{base_url}/api/visualization/{network_id}/multi-vendor/data")
        
        if response.status_code == 200:
            result = response.json()
            nodes = result.get('nodes', [])
            edges = result.get('edges', [])
            
            print(f"✅ Multi-vendor topology data retrieved!")
            print(f"   Nodes: {len(nodes)}")
            print(f"   Edges: {len(edges)}")
            
            # Count device types
            device_types = {}
            for node in nodes:
                device_type = node.get('group', 'unknown')
                device_types[device_type] = device_types.get(device_type, 0) + 1
            
            print("   Device breakdown:")
            for device_type, count in device_types.items():
                icon = {
                    'fortigate': '🔥',
                    'appliance': '🛡️',
                    'switch': '🔌',
                    'wireless': '📶',
                    'client': '💻'
                }.get(device_type, '❓')
                print(f"     {icon} {device_type}: {count}")
                
        elif response.status_code == 503:
            print("⚠️  FortiGate integration not available")
            print("   This is expected if FortiGate modules are not installed")
        else:
            print(f"❌ Multi-vendor topology failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing multi-vendor topology: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Integration Test Complete!")
    print("\nTo view the multi-vendor topology:")
    print("1. Open your web browser")
    print("2. Go to http://localhost:5000")
    print("3. Configure your Meraki API key")
    print("4. Select a network")
    print("5. Click 'View Topology' to see FortiGate + Meraki devices")
    print("\n💡 The visualization will show:")
    print("   🔥 Red FortiGate firewalls")
    print("   🛡️  Blue Meraki MX appliances") 
    print("   🔌 Green Meraki switches")
    print("   📶 Orange Meraki APs")
    print("   💻 Gray client devices")
    
    return True

if __name__ == "__main__":
    test_fortigate_integration()
