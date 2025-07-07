#!/usr/bin/env python3
"""
Simple SSL test script for Cisco Meraki CLI directory
"""

# Import SSL fixes first
import ssl_patch

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def quick_ssl_test():
    """Quick test to verify SSL fixes are working"""
    print("🔒 SSL Quick Test")
    print("=" * 20)
    
    # Test basic HTTPS connectivity
    test_urls = [
        "https://www.google.com",
        "https://api.meraki.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - Success (no SSL warnings)")
            else:
                print(f"⚠️ {url} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    
    # Test Meraki API if key is available
    api_key = os.getenv('MERAKI_API_KEY')
    if api_key:
        print(f"\n🔑 Testing Meraki API with key: {api_key[:10]}...")
        try:
            response = requests.get(
                "https://api.meraki.com/api/v1/organizations",
                headers={"X-Cisco-Meraki-API-Key": api_key},
                timeout=10
            )
            if response.status_code == 200:
                orgs = response.json()
                print(f"✅ Meraki API: Found {len(orgs)} organizations")
            else:
                print(f"⚠️ Meraki API: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Meraki API: {e}")
    else:
        print("⚠️ No Meraki API key found in environment")

if __name__ == "__main__":
    quick_ssl_test()
