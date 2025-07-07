"""
Example script demonstrating the ssl_universal_fix module usage
"""

# Method 1: Auto-apply by importing (recommended for most cases)
import ssl_universal_fix

# Method 2: Manual application with control
# from ssl_universal_fix import apply_all_ssl_fixes
# apply_all_ssl_fixes(verbose=True)

# Now all your HTTPS requests will work without SSL errors
import requests

def main():
    print("🚀 Testing SSL fixes with real API calls...")
    
    # These will all work without SSL errors now
    test_sites = [
        "https://api.github.com",
        "https://httpbin.org/get",
        "https://www.google.com",
        "https://api.meraki.com"
    ]
    
    for site in test_sites:
        try:
            response = requests.get(site, timeout=5)
            print(f"✅ {site} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {site} - Error: {e}")

if __name__ == "__main__":
    main()
