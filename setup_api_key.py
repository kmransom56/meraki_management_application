#!/usr/bin/env python3
"""
Simple API Key Setup Script
Prompts for and saves your Meraki API key securely
"""

import getpass
from api_key_storage import save_meraki_api_key, load_meraki_api_key

def setup_api_key():
    """Interactive API key setup"""
    print("=" * 60)
    print("Meraki API Key Setup")
    print("=" * 60)
    print("This will securely save your Meraki API key so you don't")
    print("have to enter it repeatedly in the web interface.")
    print()
    
    # Check if there's already a saved key
    existing_key = load_meraki_api_key()
    if existing_key:
        print(f"Found existing API key: {existing_key[:10]}...{existing_key[-4:]}")
        response = input("Do you want to replace it? (y/N): ").lower()
        if response != 'y':
            print("Keeping existing API key.")
            return
    
    # Get new API key
    print("Please enter your Meraki API key:")
    print("(You can find this in your Meraki Dashboard under Organization > Settings > Dashboard API access)")
    api_key = getpass.getpass("API Key: ").strip()
    
    if not api_key:
        print("No API key entered. Exiting.")
        return
    
    # Validate format (basic check)
    if len(api_key) < 20:
        print("Warning: API key seems too short. Meraki API keys are typically 40+ characters.")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            return
    
    # Save the API key
    if save_meraki_api_key(api_key):
        print()
        print("✅ API key saved successfully!")
        print("You won't need to enter it again in the web interface.")
        print()
        print("To start the application, run:")
        print("  python comprehensive_web_app.py")
    else:
        print("❌ Failed to save API key. Please try again.")

if __name__ == "__main__":
    setup_api_key()
