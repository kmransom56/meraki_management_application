"""
Test script to verify Meraki API connectivity with real data
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Apply SSL fixes for corporate environments FIRST
import ssl_patch  # This applies all SSL fixes automatically

# Load environment variables
load_dotenv()

def test_meraki_api():
    """Test the Meraki API with the API key from .env file"""
    
    api_key = os.getenv('MERAKI_API_KEY')
    if not api_key:
        print("❌ No API key found in environment variables")
        return False
    
    print(f"🔑 Testing Meraki API with key: {api_key[:10]}...")
    
    base_url = "https://api.meraki.com/api/v1"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Get organizations
        print("\n🏢 Testing: Get Organizations")
        response = requests.get(
            f"{base_url}/organizations",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            orgs = response.json()
            print(f"✅ Found {len(orgs)} organizations")
            
            if orgs:
                # Use the first organization for further testing
                org_id = orgs[0]['id']
                org_name = orgs[0]['name']
                print(f"📊 Testing with organization: {org_name} (ID: {org_id})")
                
                # Test 2: Get networks
                print("\n🌐 Testing: Get Networks")
                response = requests.get(
                    f"{base_url}/organizations/{org_id}/networks",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    networks = response.json()
                    print(f"✅ Found {len(networks)} networks")
                    
                    if networks:
                        # Test with first network
                        network_id = networks[0]['id']
                        network_name = networks[0]['name']
                        print(f"🔧 Testing with network: {network_name} (ID: {network_id})")
                        
                        # Test 3: Get devices
                        print("\n🖥️  Testing: Get Devices")
                        response = requests.get(
                            f"{base_url}/networks/{network_id}/devices",
                            headers=headers,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            devices = response.json()
                            print(f"✅ Found {len(devices)} devices")
                            
                            # Display device information
                            for device in devices[:5]:  # Show first 5 devices
                                print(f"  📱 {device.get('name', 'Unnamed Device')} - {device.get('model', 'Unknown Model')} - {device.get('serial', 'No Serial')}")
                            
                            # Test 4: Get clients (optional)
                            print("\n👥 Testing: Get Clients")
                            response = requests.get(
                                f"{base_url}/networks/{network_id}/clients",
                                headers=headers,
                                params={'timespan': 300},  # Last 5 minutes
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                clients = response.json()
                                print(f"✅ Found {len(clients)} clients")
                                
                                return {
                                    'success': True,
                                    'org_id': org_id,
                                    'org_name': org_name,
                                    'network_id': network_id,
                                    'network_name': network_name,
                                    'devices': devices,
                                    'clients': clients
                                }
                            else:
                                print(f"⚠️ Could not get clients: {response.status_code}")
                                return {
                                    'success': True,
                                    'org_id': org_id,
                                    'org_name': org_name,
                                    'network_id': network_id,
                                    'network_name': network_name,
                                    'devices': devices,
                                    'clients': []
                                }
                        else:
                            print(f"❌ Could not get devices: {response.status_code}")
                    else:
                        print("⚠️ No networks found")
                else:
                    print(f"❌ Could not get networks: {response.status_code}")
            else:
                print("⚠️ No organizations found")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False
    
    return False

if __name__ == "__main__":
    print("🧪 Meraki API Connectivity Test")
    print("=" * 40)
    
    result = test_meraki_api()
    if result and result.get('success'):
        print("\n🎉 API test successful! Your Meraki API key is working.")
        print("✅ Ready to run the topology visualization with real data.")
    else:
        print("\n❌ API test failed. Please check your API key and network connectivity.")
