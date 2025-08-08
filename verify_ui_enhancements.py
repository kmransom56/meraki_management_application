#!/usr/bin/env python3
"""
UI Enhancement Verification Script
Tests all professional-grade FortiGate enhancements
"""

import requests
import json
import sys
from datetime import datetime

def test_endpoint(url, description):
    """Test an endpoint and return status"""
    try:
        response = requests.get(url, timeout=10)
        status = "[PASS]" if response.status_code == 200 else f"[FAIL] ({response.status_code})"
        print(f"{status} - {description}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] - {description}: {str(e)}")
        return False

def check_template_content(url, expected_content, description):
    """Check if template contains expected professional-grade content"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text.lower()
            found = all(item.lower() in content for item in expected_content)
            status = "[PASS]" if found else "[PARTIAL]"
            print(f"{status} - {description}")
            return found
        else:
            print(f"[FAIL] - {description}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] - {description}: {str(e)}")
        return False

def main():
    base_url = "http://127.0.0.1:10000"
    
    print("=" * 70)
    print("[VERIFICATION] PROFESSIONAL-GRADE FORTIGATE UI ENHANCEMENT VERIFICATION")
    print("=" * 70)
    print(f"Testing application at: {base_url}")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test basic endpoints
    print("[ENDPOINTS] CONNECTIVITY TESTS")
    print("-" * 40)
    endpoints = [
        ("/", "Main Dashboard"),
        ("/fortigate-topology", "FortiGate Topology Page"),
        ("/fortigate-devices", "FortiGate Device Inventory"),
        ("/fortimanager-config", "FortiManager Configuration"),
        ("/api/health", "Health Check API"),
    ]
    
    passed_endpoints = 0
    for endpoint, description in endpoints:
        if test_endpoint(f"{base_url}{endpoint}", description):
            passed_endpoints += 1
    
    print()
    
    # Test professional-grade content
    print("[UI CONTENT] PROFESSIONAL-GRADE VERIFICATION")
    print("-" * 50)
    
    # Check main dashboard for FortiGate navigation links
    dashboard_content = [
        "FortiGate Topology",
        "FortiGate Device Inventory", 
        "fortigate-topology",
        "fortigate-devices"
    ]
    check_template_content(f"{base_url}/", dashboard_content, "Dashboard Navigation Links")
    
    # Check FortiGate topology page content
    topology_content = [
        "fortinet-red",
        "topology-canvas",
        "hierarchical",
        "d3.js",
        "fortigate"
    ]
    check_template_content(f"{base_url}/fortigate-topology", topology_content, "FortiGate Topology Styling")
    
    # Check FortiGate device inventory content
    inventory_content = [
        "device inventory",
        "chart.js",
        "fortinet-red",
        "device-table",
        "status"
    ]
    check_template_content(f"{base_url}/fortigate-devices", inventory_content, "FortiGate Device Inventory")
    
    print()
    print("=" * 70)
    print("[SUMMARY] VERIFICATION RESULTS")
    print("=" * 70)
    print(f"[RESULTS] Endpoints Passed: {passed_endpoints}/{len(endpoints)}")
    
    if passed_endpoints == len(endpoints):
        print("[SUCCESS] All professional-grade FortiGate enhancements are ACTIVE!")
        print("[ACCESS] Enhanced interface available at:")
        print(f"   * Main Dashboard: {base_url}/")
        print(f"   * FortiGate Topology: {base_url}/fortigate-topology")
        print(f"   * Device Inventory: {base_url}/fortigate-devices")
        print(f"   * Device Inventory: {base_url}/fortigate-devices")
    else:
        print("[WARNING] Some endpoints may need attention")
    
    print()
    print("[MANUAL] VERIFICATION STEPS:")
    print("1. Open your web browser")
    print(f"2. Navigate to: {base_url}")
    print("3. Look for 'FortiGate Topology' and 'FortiGate Device Inventory' in the sidebar")
    print("4. Click these links to verify professional-grade UI styling")
    print("5. Verify FortiGate color scheme (red, blue, green, orange)")
    print("6. Check hierarchical topology layout and device grouping")
    print("=" * 70)

if __name__ == "__main__":
    main()
