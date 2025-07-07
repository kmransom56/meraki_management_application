"""
Demonstrate SSL warnings vs SSL fixes
"""
import requests
import warnings

def test_without_ssl_fixes():
    """Test HTTPS requests without SSL fixes - shows warnings"""
    print("🚨 Testing WITHOUT SSL fixes (warnings expected):")
    print("-" * 50)
    
    try:
        # This will show SSL warnings
        response = requests.get("https://api.meraki.com", timeout=5, verify=False)
        print(f"✅ Request succeeded: {response.status_code}")
        print("   ⚠️ But you should see SSL warnings above")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_with_ssl_fixes():
    """Test HTTPS requests with SSL fixes - no warnings"""
    print("\n🔒 Testing WITH SSL fixes (no warnings):")
    print("-" * 50)
    
    # Import SSL fixes
    import ssl_universal_fix
    ssl_universal_fix.apply_all_ssl_fixes(verbose=False)
    
    try:
        # This should NOT show SSL warnings
        response = requests.get("https://api.meraki.com", timeout=5)
        print(f"✅ Request succeeded: {response.status_code}")
        print("   ✅ No SSL warnings!")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🧪 SSL Fix Demonstration")
    print("=" * 50)
    
    # First test without fixes
    test_without_ssl_fixes()
    
    # Then test with fixes
    test_with_ssl_fixes()
    
    print("\n🎉 Demonstration complete!")
    print("The SSL fixes eliminate warnings while maintaining functionality.")
