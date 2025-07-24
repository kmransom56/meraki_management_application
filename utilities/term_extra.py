"""
Terminal extra utilities module for Cisco Meraki CLI
Provides terminal functionality with fallback support
"""
import os
import sys

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ascii_art():
    """Print ASCII art banner"""
    print("🌐 Cisco Meraki CLI Tool - Enhanced")
    print("=" * 50)
    print("📡 Network Topology Visualization")
    print("🔧 Device Management & Monitoring")
    print("📊 Real-time Network Analytics")
    print("=" * 50)

def print_footer(footer_text):
    """Print footer text"""
    print("\n" + "─" * 50)
    print(footer_text)
    print("─" * 50)

def print_banner(title, subtitle=""):
    """Print a formatted banner"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    print("=" * 60)

def print_section(section_name):
    """Print a section header"""
    print(f"\n📋 {section_name}")
    print("─" * (len(section_name) + 4))

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️ {message}")
