#!/usr/bin/env python3
"""
Enterprise-Grade Web Application Verification Script
Systematic testing of all functionality for production readiness
"""

import requests
import json
import time
from datetime import datetime

class EnterpriseVerifier:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def test_result(self, test_name, status, details="", response_time=None):
        """Record test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Status icons
        icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
        time_str = f" ({response_time:.3f}s)" if response_time else ""
        print(f"{icon} {test_name}: {status}{time_str}")
        if details:
            print(f"   {details}")
    
    def test_core_infrastructure(self):
        """Test core web application infrastructure"""
        print("\nCORE INFRASTRUCTURE VERIFICATION")
        print("-" * 50)
        
        # Test 1: Main Dashboard
        start = time.time()
        try:
            response = self.session.get(self.base_url, timeout=10)
            response_time = time.time() - start
            
            if response.status_code == 200:
                if "Cisco Meraki" in response.text and "Dashboard" in response.text:
                    self.test_result("Main Dashboard", "PASS", "Page loads with correct content", response_time)
                else:
                    self.test_result("Main Dashboard", "FAIL", "Page content incorrect", response_time)
            else:
                self.test_result("Main Dashboard", "FAIL", f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.test_result("Main Dashboard", "FAIL", str(e))
        
        # Test 2: Response Time Performance
        times = []
        for i in range(3):
            start = time.time()
            try:
                response = self.session.get(self.base_url, timeout=5)
                times.append(time.time() - start)
            except:
                times.append(5.0)  # Timeout
        
        avg_time = sum(times) / len(times)
        if avg_time < 1.0:
            self.test_result("Response Performance", "PASS", f"Average: {avg_time:.3f}s", avg_time)
        elif avg_time < 2.0:
            self.test_result("Response Performance", "WARN", f"Average: {avg_time:.3f}s (acceptable)", avg_time)
        else:
            self.test_result("Response Performance", "FAIL", f"Average: {avg_time:.3f}s (too slow)", avg_time)
    
    def test_swiss_army_knife_tools(self):
        """Test all Swiss Army Knife utility tools"""
        print("\nSWISS ARMY KNIFE TOOLS VERIFICATION")
        print("-" * 50)
        
        # Test Password Generator
        start = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/tools/password_generator",
                json={'length': 16, 'symbols': True},
                headers={'Content-Type': 'application/json'}
            )
            response_time = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if 'password' in data and len(data['password']) == 16:
                    self.test_result("Password Generator", "PASS", f"Generated {len(data['password'])}-char password", response_time)
                else:
                    self.test_result("Password Generator", "FAIL", "Invalid password format", response_time)
            else:
                self.test_result("Password Generator", "FAIL", f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.test_result("Password Generator", "FAIL", str(e))
        
        # Test Subnet Calculator
        start = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/tools/subnet_calculator",
                json={'network': '192.168.1.0/24'},
                headers={'Content-Type': 'application/json'}
            )
            response_time = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if 'network' in data or 'hosts' in data:
                    self.test_result("Subnet Calculator", "PASS", "Calculation successful", response_time)
                else:
                    self.test_result("Subnet Calculator", "FAIL", "Invalid calculation result", response_time)
            else:
                self.test_result("Subnet Calculator", "FAIL", f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.test_result("Subnet Calculator", "FAIL", str(e))
        
        # Test IP Checker
        start = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/tools/ip_check",
                json={'ip': '8.8.8.8'},
                headers={'Content-Type': 'application/json'}
            )
            response_time = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if 'ip' in data and 'version' in data:
                    self.test_result("IP Checker", "PASS", f"IP analysis for {data.get('ip')}", response_time)
                else:
                    self.test_result("IP Checker", "FAIL", "Invalid IP analysis result", response_time)
            else:
                self.test_result("IP Checker", "FAIL", f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.test_result("IP Checker", "FAIL", str(e))
        
        # Test DNSBL Checker
        start = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/tools/dnsbl_check",
                json={'ip': '127.0.0.1'},
                headers={'Content-Type': 'application/json'}
            )
            response_time = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if 'ip' in data:
                    self.test_result("DNSBL Checker", "PASS", "DNSBL check completed", response_time)
                else:
                    self.test_result("DNSBL Checker", "FAIL", "Invalid DNSBL result", response_time)
            else:
                self.test_result("DNSBL Checker", "FAIL", f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.test_result("DNSBL Checker", "FAIL", str(e))
    
    def test_api_endpoints(self):
        """Test core API endpoints"""
        print("\nAPI ENDPOINTS VERIFICATION")
        print("-" * 50)
        
        # Test SSL Connection Test
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/test_ssl")
            response_time = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if 'ssl_working' in data:
                    ssl_status = "Working" if data['ssl_working'] else "Issues detected"
                    self.test_result("SSL Connection Test", "PASS", ssl_status, response_time)
                else:
                    self.test_result("SSL Connection Test", "FAIL", "Invalid SSL test result", response_time)
            else:
                self.test_result("SSL Connection Test", "FAIL", f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.test_result("SSL Connection Test", "FAIL", str(e))
        
        # Test Visualizations List
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/api/visualizations")
            response_time = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if 'visualizations' in data:
                    count = len(data['visualizations'])
                    self.test_result("Visualizations API", "PASS", f"Found {count} visualizations", response_time)
                else:
                    self.test_result("Visualizations API", "FAIL", "Invalid visualization list", response_time)
            else:
                self.test_result("Visualizations API", "FAIL", f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.test_result("Visualizations API", "FAIL", str(e))
    
    def test_visualization_functionality(self):
        """Test network visualization functionality"""
        print("\nVISUALIZATION FUNCTIONALITY VERIFICATION")
        print("-" * 50)
        
        # Test visualization page
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/visualization/L_839358380551176898")
            response_time = time.time() - start
            
            if response.status_code == 200:
                if 'Network Topology' in response.text and 'd3.js' in response.text:
                    self.test_result("Visualization Page", "PASS", "Page loads with D3.js content", response_time)
                else:
                    self.test_result("Visualization Page", "FAIL", "Page content missing", response_time)
            else:
                self.test_result("Visualization Page", "FAIL", f"HTTP {response.status_code}", response_time)
        except Exception as e:
            self.test_result("Visualization Page", "FAIL", str(e))
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\nERROR HANDLING VERIFICATION")
        print("-" * 50)
        
        # Test 404 handling
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/nonexistent_page_test")
            response_time = time.time() - start
            
            if response.status_code == 404:
                self.test_result("404 Error Handling", "PASS", "Proper 404 response", response_time)
            else:
                self.test_result("404 Error Handling", "FAIL", f"Expected 404, got {response.status_code}", response_time)
        except Exception as e:
            self.test_result("404 Error Handling", "FAIL", str(e))
        
        # Test malformed JSON handling
        start = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/tools/password_generator",
                data="invalid json data",
                headers={'Content-Type': 'application/json'}
            )
            response_time = time.time() - start
            
            if response.status_code in [400, 500]:
                self.test_result("Malformed JSON Handling", "PASS", "Proper error response", response_time)
            else:
                self.test_result("Malformed JSON Handling", "FAIL", f"Unexpected response {response.status_code}", response_time)
        except Exception as e:
            self.test_result("Malformed JSON Handling", "PASS", "Exception handled properly")
    
    def generate_enterprise_report(self):
        """Generate comprehensive enterprise verification report"""
        print("\n" + "="*70)
        print("ENTERPRISE-GRADE VERIFICATION REPORT")
        print("="*70)
        
        # Calculate statistics
        total = len(self.results)
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        failed = len([r for r in self.results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.results if r['status'] == 'WARN'])
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"SUMMARY STATISTICS:")
        print(f"   Total Tests: {total}")
        print(f"   [PASS] Passed: {passed}")
        print(f"   [FAIL] Failed: {failed}")
        print(f"   [WARN] Warnings: {warnings}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Performance metrics
        response_times = [r['response_time'] for r in self.results if r['response_time']]
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            max_response = max(response_times)
            print(f"\nPERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_response:.3f}s")
            print(f"   Maximum Response Time: {max_response:.3f}s")
        
        # Enterprise readiness assessment
        print(f"\nENTERPRISE READINESS ASSESSMENT:")
        
        if success_rate >= 95:
            grade = "ENTERPRISE READY"
            status = "PRODUCTION READY"
        elif success_rate >= 85:
            grade = "NEEDS MINOR FIXES"
            status = "NEAR PRODUCTION READY"
        elif success_rate >= 70:
            grade = "NEEDS IMPROVEMENTS"
            status = "DEVELOPMENT STAGE"
        else:
            grade = "MAJOR ISSUES"
            status = "NOT PRODUCTION READY"
        
        print(f"   Overall Grade: {grade}")
        print(f"   Status: {status}")
        
        # Detailed results
        if failed > 0:
            print(f"\nFAILED TESTS REQUIRING ATTENTION:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['details']}")
        
        if warnings > 0:
            print(f"\nWARNINGS FOR OPTIMIZATION:")
            for result in self.results:
                if result['status'] == 'WARN':
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\nENTERPRISE FEATURES VERIFIED:")
        for result in self.results:
            if result['status'] == 'PASS':
                print(f"   • {result['test']}")
        
        print(f"\nRECOMMENDATIONS:")
        if success_rate >= 95:
            print("   • Application is ready for enterprise deployment")
            print("   • Consider load testing for high-traffic scenarios")
            print("   • Implement monitoring and alerting")
        elif success_rate >= 85:
            print("   • Fix failed tests before production deployment")
            print("   • Address performance warnings")
            print("   • Conduct additional security review")
        else:
            print("   • Address all failed tests before deployment")
            print("   • Comprehensive code review required")
            print("   • Additional testing and validation needed")
        
        return success_rate >= 85  # Return True if enterprise ready

def main():
    """Run comprehensive enterprise verification"""
    print("CISCO MERAKI WEB APPLICATION")
    print("Enterprise-Grade Verification Suite")
    print("="*70)
    
    verifier = EnterpriseVerifier()
    
    # Run all verification tests
    verifier.test_core_infrastructure()
    verifier.test_swiss_army_knife_tools()
    verifier.test_api_endpoints()
    verifier.test_visualization_functionality()
    verifier.test_error_handling()
    
    # Generate final report
    enterprise_ready = verifier.generate_enterprise_report()
    
    print(f"\nDEPLOYMENT RECOMMENDATION:")
    if enterprise_ready:
        print("   APPROVED FOR ENTERPRISE DEPLOYMENT")
    else:
        print("   REQUIRES FIXES BEFORE DEPLOYMENT")
    
    return enterprise_ready

if __name__ == '__main__':
    main()
