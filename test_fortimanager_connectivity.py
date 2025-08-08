#!/usr/bin/env python3
"""
FortiManager Network Connectivity Test
Simple test to check if FortiManager instances are reachable
"""
import socket
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_tcp_connection(host, port, timeout=5):
    """Test TCP connection to host:port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"   Error testing {host}:{port} - {str(e)}")
        return False

def test_fortimanager_connectivity(name, host):
    """Test connectivity to FortiManager instance"""
    print(f"\nTesting {name} FortiManager: {host}")
    print("-" * 40)
    
    # Test common FortiManager ports
    ports_to_test = [
        (443, "HTTPS/JSON-RPC"),
        (80, "HTTP"),
        (22, "SSH"),
        (541, "FortiManager"),
        (8080, "Alt HTTP"),
        (8443, "Alt HTTPS")
    ]
    
    reachable_ports = []
    
    for port, description in ports_to_test:
        print(f"Testing port {port} ({description})...", end=" ")
        if test_tcp_connection(host, port, timeout=10):
            print("OPEN")
            reachable_ports.append((port, description))
        else:
            print("CLOSED/TIMEOUT")
    
    if reachable_ports:
        print(f"\nReachable ports on {host}:")
        for port, desc in reachable_ports:
            print(f"  - {port}: {desc}")
        return True
    else:
        print(f"\nNo ports reachable on {host}")
        return False

def ping_test(host):
    """Test basic ping connectivity"""
    print(f"\nPing test for {host}:")
    try:
        # Use Windows ping command
        import subprocess
        result = subprocess.run(['ping', '-n', '3', host], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("  PING: SUCCESS")
            # Extract ping statistics
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Average' in line or 'Lost' in line or 'Received' in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print("  PING: FAILED")
            print(f"  Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  PING: ERROR - {str(e)}")
        return False

def main():
    """Test connectivity to all FortiManager instances"""
    print("FortiManager Network Connectivity Test")
    print("=" * 50)
    
    # Get FortiManager hosts from environment
    fortimanagers = []
    
    if os.getenv('ARBYS_FORTIMANAGER_HOST'):
        fortimanagers.append(('ARBYS', os.getenv('ARBYS_FORTIMANAGER_HOST')))
    if os.getenv('BWW_FORTIMANAGER_HOST'):
        fortimanagers.append(('BWW', os.getenv('BWW_FORTIMANAGER_HOST')))
    if os.getenv('SONIC_FORTIMANAGER_HOST'):
        fortimanagers.append(('SONIC', os.getenv('SONIC_FORTIMANAGER_HOST')))
    
    if not fortimanagers:
        print("No FortiManager hosts found in environment variables")
        return
    
    print(f"Testing connectivity to {len(fortimanagers)} FortiManager instances")
    
    results = {}
    
    for name, host in fortimanagers:
        print(f"\n{'='*50}")
        print(f"TESTING {name} FORTIMANAGER")
        print(f"{'='*50}")
        
        # Basic ping test
        ping_success = ping_test(host)
        
        # Port connectivity test
        port_success = test_fortimanager_connectivity(name, host)
        
        results[name] = {
            'host': host,
            'ping': ping_success,
            'ports': port_success
        }
    
    # Summary
    print(f"\n{'='*50}")
    print("CONNECTIVITY TEST SUMMARY")
    print(f"{'='*50}")
    
    reachable_count = 0
    for name, result in results.items():
        status = "REACHABLE" if result['ports'] else "UNREACHABLE"
        ping_status = "OK" if result['ping'] else "FAIL"
        
        print(f"{name}: {status} (Ping: {ping_status})")
        print(f"  Host: {result['host']}")
        
        if result['ports']:
            reachable_count += 1
    
    print(f"\nOverall: {reachable_count}/{len(fortimanagers)} FortiManager instances reachable")
    
    if reachable_count == 0:
        print("\nTroubleshooting suggestions:")
        print("1. Check if you're connected to the correct network/VPN")
        print("2. Verify FortiManager IP addresses are correct")
        print("3. Check firewall rules blocking access")
        print("4. Confirm FortiManager instances are powered on")
        print("5. Try accessing from jumpbox VMs if required")
    elif reachable_count < len(fortimanagers):
        print(f"\nPartial connectivity - {len(fortimanagers) - reachable_count} instance(s) unreachable")
        print("Check network routing and firewall rules for unreachable instances")
    else:
        print("\nAll FortiManager instances are network reachable!")
        print("Authentication issues may be the next step to resolve")

if __name__ == "__main__":
    main()
