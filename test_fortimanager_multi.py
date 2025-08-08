#!/usr/bin/env python3
"""
Test script for multi-instance FortiManager configuration
"""
import requests
import json

def test_fortimanager_endpoints():
    """Test the multi-instance FortiManager API endpoints"""
    base_url = "http://localhost:10000"
    
    # Test data for the three FortiManager instances
    test_configs = [
        {
            "site": "arbys",
            "host": "ibue1pnftmfg05",
            "username": "test_user",
            "password": "test_pass",
            "port": 443
        },
        {
            "site": "bww", 
            "host": "ibue1pnftmfg02",
            "username": "test_user",
            "password": "test_pass",
            "port": 443
        },
        {
            "site": "sonic",
            "host": "ibue1pnftmfg04", 
            "username": "test_user",
            "password": "test_pass",
            "port": 443
        }
    ]
    
    print("Testing Multi-Instance FortiManager Configuration")
    print("=" * 60)
    
    # Test configuration saving for each site
    for config in test_configs:
        print(f"\nTesting {config['site'].upper()} FortiManager configuration...")
        
        try:
            response = requests.post(
                f"{base_url}/api/fortimanager/configure",
                json=config,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"[OK] {config['site'].upper()} configuration saved successfully")
                else:
                    print(f"[ERROR] {config['site'].upper()} configuration failed: {result.get('error')}")
            else:
                print(f"[ERROR] {config['site'].upper()} HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] {config['site'].upper()} exception: {str(e)}")
    
    # Test connection testing for each site
    print(f"\nTesting FortiManager connections...")
    for config in test_configs:
        print(f"\nTesting {config['site'].upper()} FortiManager connection...")
        
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
                else:
                    print(f"[ERROR] {config['site'].upper()} connection failed: {result.get('error')}")
            else:
                print(f"[ERROR] {config['site'].upper()} HTTP error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] {config['site'].upper()} exception: {str(e)}")
    
    # Test aggregated device retrieval
    print(f"\nTesting aggregated device retrieval...")
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
            else:
                print(f"[ERROR] Aggregated device retrieval failed: {result.get('error')}")
        else:
            print(f"[ERROR] HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
    
    print(f"\nMulti-Instance FortiManager Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_fortimanager_endpoints()
