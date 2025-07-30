#!/usr/bin/env python3
"""
Quick test to verify the topology visualization fix is working
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from enhanced_visualizer import create_enhanced_visualization, build_topology_from_api_data, create_vis_network_data
        print("✅ Enhanced visualizer imports successful")
        return True
    except ImportError as e:
        print(f"❌ Enhanced visualizer import failed: {e}")
        return False

def test_submenu_changes():
    """Test if the submenu changes are present"""
    print("\n🔍 Checking submenu changes...")
    
    try:
        with open('utilities/submenu.py', 'r') as f:
            content = f.read()
        
        if "🔍 Fetching network devices and clients..." in content:
            print("✅ Debug messages found in submenu.py")
            return True
        else:
            print("❌ Debug messages NOT found in submenu.py")
            return False
    except Exception as e:
        print(f"❌ Error reading submenu.py: {e}")
        return False

def main():
    print("🧪 TOPOLOGY VISUALIZATION FIX TEST")
    print("=" * 50)
    
    imports_ok = test_imports()
    submenu_ok = test_submenu_changes()
    
    print("\n📊 TEST RESULTS:")
    print(f"   Enhanced visualizer imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Submenu changes detected: {'✅ PASS' if submenu_ok else '❌ FAIL'}")
    
    if imports_ok and submenu_ok:
        print("\n🎉 All tests passed! The fix should be working.")
        print("   Try running the topology visualization again.")
    else:
        print("\n⚠️  Some tests failed. The fix may not be working properly.")
    
    print("\n💡 Next steps:")
    print("   1. Run this test inside the Docker container:")
    print("      docker exec -it cisco-meraki-cli-app python test_topology_fix.py")
    print("   2. If tests pass, try the topology visualization again")
    print("   3. Look for the debug messages in the terminal output")

if __name__ == "__main__":
    main()
