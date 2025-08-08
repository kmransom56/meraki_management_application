#!/usr/bin/env python3
"""
Comprehensive Link Checker for Professional FortiGate Network Management Application
Tests all links, routes, and navigation throughout the entire application
"""

import requests
import json
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import sys
from datetime import datetime
import time

class ComprehensiveLinkChecker:
    def __init__(self, base_url="http://127.0.0.1:10000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        self.tested_urls = set()
        self.results = {
            'working_links': [],
            'broken_links': [],
            'redirects': [],
            'api_endpoints': [],
            'static_files': [],
            'javascript_errors': [],
            'missing_templates': []
        }
        
    def test_url(self, url, description="", expected_status=200):
        """Test a single URL and return detailed results"""
        try:
            if url in self.tested_urls:
                return None
            
            self.tested_urls.add(url)
            response = self.session.get(url)
            
            result = {
                'url': url,
                'description': description,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.content),
                'success': response.status_code == expected_status
            }
            
            if response.status_code == expected_status:
                self.results['working_links'].append(result)
                print(f"[PASS] {response.status_code} - {description or url}")
            elif 300 <= response.status_code < 400:
                self.results['redirects'].append(result)
                print(f"[REDIRECT] {response.status_code} - {description or url}")
            else:
                self.results['broken_links'].append(result)
                print(f"[FAIL] {response.status_code} - {description or url}")
            
            return result
            
        except Exception as e:
            error_result = {
                'url': url,
                'description': description,
                'error': str(e),
                'success': False
            }
            self.results['broken_links'].append(error_result)
            print(f"[ERROR] {description or url}: {str(e)}")
            return error_result
    
    def extract_links_from_page(self, url):
        """Extract all links from a webpage"""
        try:
            response = self.session.get(url)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            # Extract href links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                link_text = link.get_text(strip=True)
                links.append({
                    'url': full_url,
                    'text': link_text,
                    'type': 'navigation'
                })
            
            # Extract form actions
            for form in soup.find_all('form', action=True):
                action = form['action']
                full_url = urljoin(url, action)
                links.append({
                    'url': full_url,
                    'text': f"Form action: {action}",
                    'type': 'form'
                })
            
            # Extract script sources
            for script in soup.find_all('script', src=True):
                src = script['src']
                if not src.startswith(('http://', 'https://')):
                    full_url = urljoin(url, src)
                    links.append({
                        'url': full_url,
                        'text': f"Script: {src}",
                        'type': 'static'
                    })
            
            # Extract CSS links
            for link in soup.find_all('link', href=True):
                href = link['href']
                if not href.startswith(('http://', 'https://')):
                    full_url = urljoin(url, href)
                    links.append({
                        'url': full_url,
                        'text': f"CSS: {href}",
                        'type': 'static'
                    })
            
            return links
            
        except Exception as e:
            print(f"[ERROR] Could not extract links from {url}: {str(e)}")
            return []
    
    def test_api_endpoints(self):
        """Test all known API endpoints"""
        print("\n[API ENDPOINTS] Testing API functionality")
        print("-" * 50)
        
        api_endpoints = [
            ('/api/health', 'Health Check API'),
            ('/api/devices', 'Device List API'),
            ('/api/networks', 'Networks API'),
            ('/api/organizations', 'Organizations API'),
            ('/api/fortimanager/devices', 'FortiManager Devices API'),
            ('/api/fortimanager/config', 'FortiManager Config API'),
            ('/api/fortimanager/test', 'FortiManager Test API'),
            ('/api/fortimanager/all-devices', 'All FortiManager Devices API'),
            ('/api/visualization/demo/multi-vendor/data', 'Demo Visualization Data'),
            ('/api/ai-maintenance/status', 'AI Maintenance Status'),
            ('/api/ai-maintenance/metrics', 'AI Maintenance Metrics'),
        ]
        
        for endpoint, description in api_endpoints:
            url = urljoin(self.base_url, endpoint)
            result = self.test_url(url, description)
            if result:
                self.results['api_endpoints'].append(result)
    
    def test_main_pages(self):
        """Test all main application pages"""
        print("\n[MAIN PAGES] Testing primary application pages")
        print("-" * 50)
        
        main_pages = [
            ('/', 'Main Dashboard'),
            ('/visualization', 'Visualization Index'),
            ('/visualization/', 'Visualization Index (trailing slash)'),
            ('/fortigate-topology', 'FortiGate Topology Page'),
            ('/fortigate-devices', 'FortiGate Device Inventory'),
            ('/fortimanager-config', 'FortiManager Configuration'),
            ('/network-visualization', 'Network Visualization'),
        ]
        
        for page, description in main_pages:
            url = urljoin(self.base_url, page)
            self.test_url(url, description)
    
    def test_static_files(self):
        """Test common static file paths"""
        print("\n[STATIC FILES] Testing static resources")
        print("-" * 50)
        
        static_files = [
            ('/static/css/style.css', 'Main Stylesheet'),
            ('/static/js/app.js', 'Main JavaScript'),
            ('/static/images/logo.png', 'Logo Image'),
            ('/favicon.ico', 'Favicon'),
        ]
        
        for file_path, description in static_files:
            url = urljoin(self.base_url, file_path)
            result = self.test_url(url, description, expected_status=200)
            if result:
                self.results['static_files'].append(result)
    
    def crawl_and_test_all_links(self):
        """Crawl the application and test all discovered links"""
        print("\n[LINK CRAWLING] Discovering and testing all application links")
        print("-" * 60)
        
        # Start with main pages
        start_urls = [
            self.base_url + '/',
            self.base_url + '/fortigate-topology',
            self.base_url + '/fortigate-devices',
        ]
        
        discovered_links = set()
        
        for start_url in start_urls:
            print(f"\n[CRAWLING] Extracting links from: {start_url}")
            links = self.extract_links_from_page(start_url)
            
            for link_info in links:
                link_url = link_info['url']
                
                # Only test internal links
                if self.base_url in link_url and link_url not in discovered_links:
                    discovered_links.add(link_url)
                    description = f"{link_info['type']}: {link_info['text'][:50]}"
                    self.test_url(link_url, description)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("[COMPREHENSIVE LINK CHECK REPORT]")
        print("=" * 80)
        print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        print(f"Total URLs tested: {len(self.tested_urls)}")
        
        # Summary statistics
        working_count = len(self.results['working_links'])
        broken_count = len(self.results['broken_links'])
        redirect_count = len(self.results['redirects'])
        
        print(f"\n[SUMMARY STATISTICS]")
        print(f"Working links: {working_count}")
        print(f"Broken links: {broken_count}")
        print(f"Redirects: {redirect_count}")
        print(f"API endpoints tested: {len(self.results['api_endpoints'])}")
        
        # Success rate
        total_tests = working_count + broken_count + redirect_count
        if total_tests > 0:
            success_rate = (working_count / total_tests) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        # Detailed broken links
        if self.results['broken_links']:
            print(f"\n[BROKEN LINKS] {len(self.results['broken_links'])} issues found:")
            print("-" * 50)
            for link in self.results['broken_links']:
                status = link.get('status_code', 'ERROR')
                error = link.get('error', '')
                print(f"[{status}] {link['description']} - {link['url']}")
                if error:
                    print(f"      Error: {error}")
        
        # Working API endpoints
        working_apis = [api for api in self.results['api_endpoints'] if api.get('success', False)]
        if working_apis:
            print(f"\n[WORKING API ENDPOINTS] {len(working_apis)} endpoints active:")
            print("-" * 50)
            for api in working_apis:
                print(f"[{api['status_code']}] {api['description']}")
        
        # Overall assessment
        print(f"\n[OVERALL ASSESSMENT]")
        if broken_count == 0:
            print("[EXCELLENT] All links and endpoints are working perfectly!")
        elif broken_count <= 2:
            print("[GOOD] Most links working, minor issues detected")
        elif broken_count <= 5:
            print("[FAIR] Some issues detected, may need attention")
        else:
            print("[NEEDS ATTENTION] Multiple broken links detected")
        
        print("=" * 80)
        
        return self.results

def main():
    print("Starting comprehensive link check for FortiGate Network Management Application...")
    print("This will test all pages, links, API endpoints, and static resources.")
    print()
    
    checker = ComprehensiveLinkChecker()
    
    # Test main application components
    checker.test_main_pages()
    checker.test_api_endpoints()
    checker.test_static_files()
    checker.crawl_and_test_all_links()
    
    # Generate final report
    results = checker.generate_report()
    
    # Save results to file
    with open('link_check_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: link_check_results.json")
    
    return results

if __name__ == "__main__":
    main()
