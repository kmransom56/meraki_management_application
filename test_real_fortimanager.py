#!/usr/bin/env python3
"""
Test script for multi-instance FortiManager with real credentials from .env
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_real_fortimanager_endpoints():
    """Test the multi-instance FortiManager API endpoints with real credentials"""
    base_url = "http://localhost:10000"
    
    print("Testing Multi-Instance FortiManager with Real Credentials")
    print("=" * 60)
    
    # Test loading configurations from environment
    print("\n[1] Testing environment configuration loading...")
    try:
        response = requests.post(f"{base_url}/api/fortimanager/load-env-configs")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"[OK] Environment configurations loaded successfully")
                print(f"   Sites: {', '.join(result.get('sites', []))}")
                print(f"   Message: {result.get('message')}")
                
                # Show loaded configurations (without passwords)
                for site, config in result.get('configs', {}).items():
                    print(f"   {site.upper()}: {config.get('host')} (user: {config.get('username')})")
            else:
                print(f"[ERROR] Environment configuration loading failed: {result.get('error')}")
        else:
            print(f"[ERROR] HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
    
    # Test connection to each FortiManager with real credentials
    print(f"\n[2] Testing FortiManager connections with real credentials...")
    
    # Get credentials from environment
    test_configs = []
    
    if all([os.getenv('ARBYS_FORTIMANAGER_HOST'), os.getenv('ARBYS_USERNAME'), os.getenv('ARBYS_PASSWORD')]):
        test_configs.append({
            "site": "arbys",
            "host": os.getenv('ARBYS_FORTIMANAGER_HOST'),
            "username": os.getenv('ARBYS_USERNAME'),
            "password": os.getenv('ARBYS_PASSWORD'),
            "port": 443
        })
    
    if all([os.getenv('BWW_FORTIMANAGER_HOST'), os.getenv('BWW_USERNAME'), os.getenv('BWW_PASSWORD')]):
        test_configs.append({
            "site": "bww",
            "host": os.getenv('BWW_FORTIMANAGER_HOST'),
            "username": os.getenv('BWW_USERNAME'),
            "password": os.getenv('BWW_PASSWORD'),
            "port": 443
        })
    
    if all([os.getenv('SONIC_FORTIMANAGER_HOST'), os.getenv('SONIC_USERNAME'), os.getenv('SONIC_PASSWORD')]):
        test_configs.append({
            "site": "sonic",
            "host": os.getenv('SONIC_FORTIMANAGER_HOST'),
            "username": os.getenv('SONIC_USERNAME'),
            "password": os.getenv('SONIC_PASSWORD'),
            "port": 443
        })
    
    print(f"Found {len(test_configs)} FortiManager configurations in environment")
    
    for config in test_configs:
        print(f"\nTesting {config['site'].upper()} FortiManager connection...")
        print(f"   Host: {config['host']}")
        print(f"   Username: {config['username']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/fortimanager/test",
                json=config,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"[OK] {config['site'].upper()} connection test successful")
                    print(f"   Device count: {result.get('device_count', 'N/A')}")
                    print(f"   Message: {result.get('message')}")
                else:
                    print(f"[ERROR] {config['site'].upper()} connection failed: {result.get('error')}")
            else:
                print(f"[ERROR] {config['site'].upper()} HTTP error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] {config['site'].upper()} exception: {str(e)}")
    
    # Test aggregated device retrieval with real data
    print(f"\n[3] Testing aggregated device retrieval with real data...")
    try:
        response = requests.get(f"{base_url}/api/fortimanager/devices/all")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"[OK] Aggregated device retrieval successful")
                print(f"   Total devices: {result.get('total_devices', 0)}")
                print(f"   Configured sites: {', '.join(result.get('configured_sites', []))}")
                
                # Show site status
                site_status = result.get('site_status', {})
                for site, status in site_status.items():
                    status_icon = "[OK]" if status['status'] == 'connected' else "[ERROR]"
                    print(f"   {status_icon} {site.upper()}: {status['status']} ({status['device_count']} devices)")
                    if 'error' in status:
                        print(f"      Error: {status['error']}")
                
                # Show some device details if available
                devices = result.get('devices', [])
                if devices:
                    print(f"\n   Sample devices:")
                    for device in devices[:5]:  # Show first 5 devices
                        print(f"   - {device.get('name', 'Unknown')} ({device.get('model', 'N/A')}) - {device.get('fortimanager_site', 'N/A')}")
                    if len(devices) > 5:
                        print(f"   ... and {len(devices) - 5} more devices")
            else:
                print(f"[ERROR] Aggregated device retrieval failed: {result.get('error')}")
        else:
            print(f"[ERROR] HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
    
    print(f"\nReal FortiManager Multi-Instance Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_real_fortimanager_endpoints()
