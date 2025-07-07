#!/usr/bin/env python3
"""
Test script for network pagination functionality
"""

import os
import sys
import json

# Add the CLI directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pagination():
    """Test the pagination function with mock data"""
    
    # Create mock network data
    mock_networks = []
    for i in range(150):  # Create 150 mock networks
        mock_networks.append({
            'id': f'N_12345678901234567{i:03d}',
            'name': f'IBRBR#{330000 + i}',
            'productTypes': ['switch', 'wireless']
        })
    
    print("🧪 Testing Network Pagination")
    print("=" * 40)
    print(f"Created {len(mock_networks)} mock networks")
    
    # Test the pagination function
    try:
        from utilities.submenu import select_network_with_pagination
        
        print("\n🚀 Starting pagination test...")
        print("  • Page size should be 20 networks")
        print("  • Navigation options: P (Previous), N (Next), S (Search), Q (Quit)")
        print("  • Enter a number to select a network")
        
        selected_id = select_network_with_pagination(mock_networks, "Test Organization")
        
        if selected_id:
            # Find the selected network
            selected = next((n for n in mock_networks if n['id'] == selected_id), None)
            if selected:
                print(f"\n✅ Test completed successfully!")
                print(f"Selected network: {selected['name']} (ID: {selected['id']})")
            else:
                print("\n❌ Error: Selected network not found in mock data")
        else:
            print("\n⚠️ Test cancelled by user")
            
    except Exception as e:
        print(f"\n❌ Error testing pagination: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pagination()
