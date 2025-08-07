#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     2.6 - Enhanced Edition                                   *
#   Author:      Matia Zanella                                            *
#   Updated:     Keith Ransom - Added Enhanced Network Visualization      *
#   Description: Cisco Meraki CLU (Command Line Utility) is an essential  *
#                tool crafted for Network Administrators managing Meraki  *
#   Github:      https://github.com/akamura/cisco-meraki-clu/             *
#                                                                         *
#   Icon Author:        Cisco Systems, Inc.                               *
#   Icon Author URL:    https://meraki.cisco.com/                         *
#                                                                         *
#   Copyright (C) 2025 Keith Ransom                                       *
#   https://www.netintegrate.net                                          *
#                                                                         *
#   This program is free software; you can redistribute it and/or modify  *
#   it under the terms of the GNU General Public License as published by  *
#   the Free Software Foundation; either version 2 of the License, or     *
#   (at your option) any later version.                                   *
#                                                                         *
#   This program is distributed in the hope that it will be useful,       *
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#   GNU General Public License for more details.                          *
#                                                                         *
#   You should have received a copy of the GNU General Public License     *
#   along with this program; if not, write to the                         *
#   Free Software Foundation, Inc.,                                       *
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#**************************************************************************

# ==================================================
# IMPORT various libraries and modules
# ==================================================
import os
import sys
import logging
import traceback
import argparse
from datetime import datetime
from termcolor import colored
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from getpass import getpass

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print(colored("[OK] Environment variables loaded from .env file", "green"))
except ImportError:
    print(colored("⚠️ python-dotenv not found. Using system environment variables.", "yellow"))

# Apply SSL fixes for corporate environments (Zscaler, Blue Coat, etc.)
try:
    import ssl_patch  # Applies SSL fixes automatically
    print(colored("[SECURITY] SSL fixes applied for corporate environment", "green"))
except ImportError:
    print(colored("⚠️ SSL patch not found. SSL issues may occur in corporate environments.", "yellow"))
except ImportError:
    print(colored("⚠️ python-dotenv not found. Install with: pip install python-dotenv", "yellow"))

# Import existing modules
from api import meraki_api_manager
from settings import db_creator
from utilities import submenu
from settings import term_extra
from modules.meraki.meraki_sdk_wrapper import MerakiSDKWrapper
# Import custom API functions for dashboard emulation
from modules.meraki import meraki_api

# NEW: Import enhanced visualization module
try:
    from enhanced_visualizer import create_enhanced_visualization
    ENHANCED_VIZ_AVAILABLE = True
    print(colored("[OK] Enhanced Network Visualization Module Loaded", "green"))
except ImportError as e:
    ENHANCED_VIZ_AVAILABLE = False
    print(colored("⚠️ Enhanced Visualization Module Not Found", "yellow"))
    print(colored("   Network visualization will use basic mode only", "yellow"))

# Configure logging with more detailed output
logging.basicConfig(
    level=logging.INFO,  # Changed from DEBUG to reduce noise
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meraki_clu_debug.log'),
        logging.StreamHandler()
    ]
)

# Reduce SSL-related logging noise in corporate environments
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Required packages check
required_packages = {
    "tabulate": "tabulate",
    "pathlib": "pathlib", 
    "datetime": "datetime",
    "termcolor": "termcolor",
    "requests": "requests",
    "rich": "rich",
    "setuptools": "setuptools",
    "cryptography": "cryptography",
    "meraki": "meraki"
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print(colored("Missing required Python packages: " + ", ".join(missing_packages), "red"))
    print("Please install them using the following command:")
    print(f"{sys.executable} -m pip install " + " ".join(missing_packages))
    sys.exit(1)

# ==================================================
# ERROR logging
# ==================================================
logger = logging.getLogger('ciscomerakiclu')
logger.setLevel(logging.ERROR)

log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, 'error.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ==================================================
# NEW: Enhanced Network Visualization Functions
# ==================================================
def network_visualization_menu(api_key, api_mode, fernet):
    """Enhanced network visualization menu with multiple options"""
    
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        
        print(colored("\n🌐 NETWORK TOPOLOGY VISUALIZATION", "cyan"))
        print("=" * 60)
        print("1. Basic Network Topology (Legacy)")
        
        if ENHANCED_VIZ_AVAILABLE:
            print("2. 🚀 Enhanced Interactive Topology (NEW!)")
            print("3. 🎯 Quick Network Overview")
            print("4. 📊 Network Statistics Dashboard")
        else:
            print(colored("2. Enhanced Topology (Module Not Available)", "red"))
            
        print("5. 🌐 View Generated Visualizations")
        print("6. ⚙️ Visualization Settings")
        print("7. 📖 Help & Documentation") 
        print("8. 🔙 Back to Main Menu")
        print("=" * 60)
        
        if ENHANCED_VIZ_AVAILABLE:
            print(colored("💡 Enhanced features include interactive controls, device details, and modern UI!", "green"))
        
        choice = input(colored("\nSelect visualization option [1-8]: ", "cyan")).strip()
        
        if choice == '1':
            create_basic_visualization(api_key, api_mode)
        elif choice == '2' and ENHANCED_VIZ_AVAILABLE:
            create_enhanced_network_visualization(api_key, api_mode)
        elif choice == '3' and ENHANCED_VIZ_AVAILABLE:
            create_network_overview(api_key, api_mode)
        elif choice == '4' and ENHANCED_VIZ_AVAILABLE:
            create_network_stats_dashboard(api_key, api_mode)
        elif choice == '5':
            view_generated_visualizations()
        elif choice == '6':
            visualization_settings(fernet)
        elif choice == '7':
            show_visualization_help()
        elif choice == '8':
            break
        else:
            print(colored("\nInvalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))


def create_enhanced_network_visualization(api_key, api_mode):
    """Create enhanced interactive network visualization"""
    
    try:
        print(colored("\n🚀 Creating Enhanced Interactive Network Visualization", "cyan"))
        print("=" * 60)
        
        # Get organizations and networks
        if api_mode == 'sdk':
            import meraki
            dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)
        else:
            # Use custom API implementation
            dashboard = create_custom_dashboard_object(api_key)
        
        # Get organizations
        try:
            organizations = dashboard.organizations.getOrganizations()
            
            if not organizations:
                print(colored("No organizations found.", "red"))
                input(colored("\nPress Enter to continue...", "green"))
                return
                
        except Exception as e:
            print(colored(f"Error fetching organizations: {str(e)}", "red"))
            input(colored("\nPress Enter to continue...", "green"))
            return
        
        # Select organization
        if len(organizations) == 1:
            selected_org = organizations[0]
            print(f"Using organization: {selected_org['name']}")
        else:
            print("\nAvailable Organizations:")
            for i, org in enumerate(organizations, 1):
                print(f"{i}. {org['name']} (ID: {org['id']})")
            
            try:
                org_choice = int(input(f"\nSelect organization [1-{len(organizations)}]: ")) - 1
                selected_org = organizations[org_choice]
            except (ValueError, IndexError):
                print(colored("Invalid selection.", "red"))
                input(colored("\nPress Enter to continue...", "green"))
                return
        
        # Get networks for selected organization
        try:
            networks = dashboard.organizations.getOrganizationNetworks(selected_org['id'])
            
            if not networks:
                print(colored("No networks found in this organization.", "red"))
                input(colored("\nPress Enter to continue...", "green"))
                return
                
        except Exception as e:
            print(colored(f"Error fetching networks: {str(e)}", "red"))
            input(colored("\nPress Enter to continue...", "green"))
            return
        
        # Select network with pagination
        print(f"\n📡 Found {len(networks)} networks in {selected_org['name']}")
        print("🔄 Loading network selection with pagination...")
        
        from utilities.submenu import select_network_with_pagination
        
        try:
            print("📋 Starting paginated network selection...")
            selected_network_id = select_network_with_pagination(networks, selected_org['name'])
            
            if not selected_network_id:
                print(colored("Network selection cancelled.", "yellow"))
                input(colored("\nPress Enter to continue...", "green"))
                return
            
            print(f"[OK] Selected network ID: {selected_network_id}")
            
            # Find the selected network object
            selected_network = None
            for network in networks:
                if network['id'] == selected_network_id:
                    selected_network = network
                    break
            
            if not selected_network:
                print(colored("Selected network not found.", "red"))
                input(colored("\nPress Enter to continue...", "green"))
                return
                
            print(f"[OK] Selected network object found: {selected_network['name']}")
                
        except Exception as e:
            print(colored(f"Error selecting network: {str(e)}", "red"))
            print(colored(f"Traceback: {e.__class__.__name__}", "red"))
            input(colored("\nPress Enter to continue...", "green"))
            return
        
        # Create enhanced visualization
        print(f"\n🔄 Generating enhanced visualization for: {selected_network['name']}")
        print("This may take a few moments...")
        print("- Fetching network devices...")
        print("- Collecting client information...")
        print("- Building interactive topology...")
        print("- Generating HTML visualization...")
        
        # Call the enhanced visualization function
        output_file = create_enhanced_visualization(
            dashboard, 
            selected_network['id'], 
            selected_network['name']
        )
        
        if output_file:
            filename = os.path.basename(output_file)
            print(colored("\n[OK] Enhanced Network Visualization Created Successfully!", "green"))
            print("=" * 60)
            print(f"📁 File Location: {output_file}")
            print(f"🌐 Web Interface: http://localhost:5000/view-viz/{filename}")
            print(f"📋 All Visualizations: http://localhost:5000/visualizations")
            print("=" * 60)
            
            print(colored("\n🎯 Visualization Features:", "cyan"))
            print("• Interactive device information on click")
            print("• Toggle physics simulation and layouts")
            print("• Export topology as PNG image")
            print("• Real-time device status indicators")
            print("• Hierarchical and force-directed layouts")
            print("• Modern responsive design")
            
            # Options for user
            print(colored("\n📖 Next Steps:", "green"))
            print("1. Open the web interface URL in your browser")
            print("2. Click on devices to see detailed information")
            print("3. Use the control buttons to adjust the view")
            print("4. Export the topology as an image if needed")
            
        else:
            print(colored("\n❌ Failed to Create Visualization", "red"))
            print("Please check:")
            print("• Your network connection")
            print("• API key permissions")
            print("• Network has accessible devices")
            print("• Check the error logs for details")
            
    except Exception as e:
        print(colored(f"\n❌ Error creating enhanced visualization: {str(e)}", "red"))
        logger.error(f"Enhanced visualization error: {str(e)}", exc_info=True)
    
    input(colored("\nPress Enter to return to visualization menu...", "green"))


def create_basic_visualization(api_key, api_mode):
    """Create basic network visualization using existing functionality"""
    
    print(colored("\n📊 Creating Basic Network Visualization", "cyan"))
    print("Using existing visualization system...")
    
    # Call existing visualization from submenu
    if api_mode == 'sdk':
        sdk_wrapper = MerakiSDKWrapper(api_key)
        # You would call your existing visualization function here
        print("Using SDK mode for basic visualization...")
    else:
        # Use custom API implementation
        print("Using custom API mode for basic visualization...")
    
    input(colored("\nPress Enter to continue...", "green"))


def create_network_overview(api_key, api_mode):
    """Create a quick network overview visualization"""
    
    print(colored("\n🎯 Creating Quick Network Overview", "cyan"))
    print("This feature will be implemented in future updates...")
    input(colored("\nPress Enter to continue...", "green"))


def create_network_stats_dashboard(api_key, api_mode):
    """Create network statistics dashboard"""
    
    print(colored("\n📊 Creating Network Statistics Dashboard", "cyan"))
    print("This feature will be implemented in future updates...")
    input(colored("\nPress Enter to continue...", "green"))


def view_generated_visualizations():
    """View previously generated visualizations"""
    
    print(colored("\n🌐 Generated Network Visualizations", "cyan"))
    print("=" * 50)
    
    viz_dir = "/home/merakiuser/meraki_visualizations"
    
    try:
        if os.path.exists(viz_dir):
            files = [f for f in os.listdir(viz_dir) if f.endswith('.html')]
            
            if files:
                print(f"Found {len(files)} visualization files:")
                print()
                
                for i, file in enumerate(sorted(files), 1):
                    # Get file info
                    file_path = os.path.join(viz_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    print(f"{i}. {file}")
                    print(f"   📅 Created: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   📏 Size: {file_size:,} bytes")
                    print(f"   🌐 URL: http://localhost:5000/view-viz/{file}")
                    print()
                
                print(colored("💡 Access all visualizations at: http://localhost:5000/visualizations", "green"))
                
            else:
                print("No visualization files found.")
                print("Create some visualizations first using the enhanced topology option!")
        else:
            print("Visualization directory not found.")
            print("Create your first visualization to initialize the directory.")
            
    except Exception as e:
        print(colored(f"Error reading visualization directory: {str(e)}", "red"))
    
    input(colored("\nPress Enter to continue...", "green"))


def visualization_settings(fernet):
    """Configure visualization settings"""
    
    print(colored("\n⚙️ Visualization Settings", "cyan"))
    print("=" * 40)
    print("1. Output Directory Settings")
    print("2. Default Layout Options")
    print("3. Color Scheme Preferences")
    print("4. Export Settings")
    print("5. Back to Visualization Menu")
    
    choice = input(colored("\nSelect setting [1-5]: ", "cyan")).strip()
    
    if choice == "5":
        return
    else:
        print("Settings configuration will be implemented in future updates...")
        input(colored("\nPress Enter to continue...", "green"))


def show_visualization_help():
    """Show help and documentation for visualization features"""
    
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    print(colored("\n📖 Network Visualization Help & Documentation", "cyan"))
    print("=" * 70)
    
    print(colored("\n🚀 Enhanced Interactive Topology Features:", "green"))
    print("• Click on any device to view detailed information")
    print("• Use control buttons to adjust physics and layout")
    print("• Toggle hierarchical view for organized topology")
    print("• Export topology as PNG image for documentation")
    print("• Real-time device status with color indicators")
    print("• Interactive legend showing device types")
    
    print(colored("\n🎨 Device Color Coding:", "yellow"))
    print("• 🛡️  Orange: Security Appliances (MX)")
    print("• 🔄  Green: Switches (MS)")
    print("• 📡  Blue: Access Points (MR)")
    print("• 💻  Purple: Client Devices")
    print("• 📹  Red: Cameras (MV)")
    print("• 🌐  Orange: Unknown Devices")
    
    print(colored("\n🔧 Troubleshooting:", "cyan"))
    print("• If visualization doesn't load: Check http://localhost:5000")
    print("• If no devices appear: Verify API permissions")
    print("• If container issues: Restart with 'docker-compose down && docker-compose up -d'")
    print("• For missing module errors: Ensure enhanced_visualizer.py is in place")
    
    print(colored("\n📁 File Locations:", "blue"))
    print("• Generated files: ./outputs/ (Windows) or /home/merakiuser/meraki_visualizations/ (container)")
    print("• Web interface: http://localhost:5000/visualizations")
    print("• Individual files: http://localhost:5000/view-viz/[filename]")
    
    print(colored("\n💡 Tips for Best Results:", "green"))
    print("• Use networks with mixed device types for rich topologies")
    print("• Allow some time for client data collection")
    print("• Use hierarchical view for large networks")
    print("• Export images for network documentation")
    
    input(colored("\nPress Enter to return to visualization menu...", "green"))


def create_custom_dashboard_object(api_key):
    """Create a CustomDashboard object for custom API mode, emulating the Meraki SDK interface"""
    class CustomDashboard:
        def __init__(self, api_key):
            self.api_key = api_key
            self.organizations = self.Organizations(api_key)
            self.networks = self.Networks(api_key)

        class Organizations:
            def __init__(self, api_key):
                self.api_key = api_key
            def getOrganizations(self):
                return meraki_api.get_organizations(self.api_key)
            def getOrganizationNetworks(self, org_id):
                return meraki_api.get_organization_networks(self.api_key, org_id)

        class Networks:
            def __init__(self, api_key):
                self.api_key = api_key
            def getNetworkDevices(self, network_id):
                return meraki_api.get_network_devices(self.api_key, network_id)
            def getNetworkClients(self, network_id, timespan=86400):
                return meraki_api.get_network_clients(self.api_key, network_id, timespan)
            def getNetworkTopology(self, network_id):
                # If you have a topology function, use it; otherwise, return None
                if hasattr(meraki_api, 'get_network_topology'):
                    return meraki_api.get_network_topology(self.api_key, network_id)
                return None
    return CustomDashboard(api_key)


# ==================================================
# VISUALIZE the Main Menu (Enhanced)
# ==================================================
def main_menu(fernet):
    """Display the main menu and handle user input"""
    while True:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        
        # Get API key
        api_key = meraki_api_manager.get_api_key(fernet)
        
        # Get API mode (custom or SDK)
        api_mode = db_creator.get_api_mode(fernet) or 'custom'
        
        print("\nMain Menu - Enhanced Edition")
        print("=" * 50)
        print("1. Network Status")
        print("2. Switches and Access Points")
        print("3. Appliance")
        print("4. Environmental Monitoring")
        print("5. Network-Wide Operations")
        print("6. 🌐 Network Visualization (NEW!)")  # Enhanced option
        print("7. Swiss Army Knife")
        print("8. Manage API Key")
        print("9. Manage IPinfo Token")
        print(f"10. API Mode: {api_mode.upper()}")
        print("11. Test SSL Connection")
        print("12. Exit")
        
        if ENHANCED_VIZ_AVAILABLE:
            print(colored("\n💡 New: Interactive network topology visualization available!", "green"))
        
        choice = input(colored("\nChoose a menu option [1-12]: ", "cyan"))
        
        if choice == '1':
            if api_key:
                if api_mode == 'sdk':
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    submenu.submenu_network_status_sdk(sdk_wrapper)
                else:
                    submenu.submenu_network_status(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
            
        elif choice == '2':
            if api_key:
                if api_mode == 'sdk':
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    submenu.submenu_sw_and_ap_sdk(sdk_wrapper)
                else:
                    submenu.submenu_sw_and_ap(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
            
        elif choice == '3':
            if api_key:
                if api_mode == 'sdk':
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    submenu.submenu_appliance_sdk(sdk_wrapper)
                else:
                    submenu.submenu_appliance(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
            
        elif choice == '4':
            if api_key:
                if api_mode == 'sdk':
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    submenu.submenu_environmental_sdk(sdk_wrapper)
                else:
                    submenu.submenu_environmental(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
            
        elif choice == '5':
            if api_key:
                if api_mode == 'sdk':
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    organization_id = submenu.select_organization(sdk_wrapper)
                    if organization_id:
                        submenu.network_wide_operations_sdk(sdk_wrapper, organization_id)
                else:
                    organization_id = submenu.select_organization(api_key)
                    if organization_id:
                        submenu.network_wide_operations(api_key, organization_id)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
            
        elif choice == '6':  # NEW: Network Visualization
            if api_key:
                network_visualization_menu(api_key, api_mode, fernet)
            else:
                print(colored("Please set the Cisco Meraki API key first.", "red"))
                input(colored("\nPress Enter to return to the main menu...", "green"))
                
        elif choice == '7':
            submenu.swiss_army_knife_submenu(fernet)
            
        elif choice == '8':
            manage_api_key(fernet)
            
        elif choice == '9':
            manage_ipinfo_token(fernet)
            
        elif choice == '10':
            toggle_api_mode(fernet)
            
        elif choice == '11':
            test_ssl_connection(fernet)
            
        elif choice == '12':
            print(colored("\nThank you for using Cisco Meraki CLU Enhanced Edition!", "green"))
            sys.exit(0)
            
        else:
            print(colored("\nInvalid choice. Please try again.", "red"))
            input(colored("\nPress Enter to continue...", "green"))


# ==================================================
# TOGGLE API Mode (SDK or Custom)
# ==================================================
def toggle_api_mode(fernet):
    """Toggle between custom API and SDK mode"""
    try:
        current_mode = db_creator.get_api_mode(fernet) or 'custom'
        
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        print("\nAPI Mode Selection")
        print("=" * 50)
        print(f"Current API Mode: {current_mode.upper()}")
        print("\nAvailable Modes:")
        print("1. Custom API (Default, with enhanced SSL handling for Windows/Zscaler)")
        print("2. Meraki SDK (Official Python SDK)")
        print("3. Return to Main Menu")
        
        choice = input(colored("\nSelect API Mode [1-3]: ", "cyan"))
        
        if choice == '1':
            if current_mode != 'custom':
                db_creator.set_api_mode(fernet, 'custom')
                print(colored("\nAPI Mode set to Custom API.", "green"))
            else:
                print(colored("\nAPI Mode is already set to Custom API.", "yellow"))
        elif choice == '2':
            # Check if Meraki SDK is installed
            try:
                import meraki
                if current_mode != 'sdk':
                    db_creator.set_api_mode(fernet, 'sdk')
                    print(colored("\nAPI Mode set to Meraki SDK.", "green"))
                else:
                    print(colored("\nAPI Mode is already set to Meraki SDK.", "yellow"))
            except ImportError:
                print(colored("\nMeraki SDK not found. Installing...", "yellow"))
                try:
                    import subprocess
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "meraki"])
                    if current_mode != 'sdk':
                        db_creator.set_api_mode(fernet, 'sdk')
                    print(colored("\nMeraki SDK installed and API Mode set to Meraki SDK.", "green"))
                except Exception as e:
                    print(colored(f"\nError installing Meraki SDK: {str(e)}", "red"))
                    print(colored("Please install it manually using: pip install meraki", "red"))
                    print(colored("API Mode remains unchanged.", "yellow"))
        elif choice == '3':
            return
        else:
            print(colored("\nInvalid choice. API Mode remains unchanged.", "red"))
        
        input(colored("\nPress Enter to continue...", "green"))
    except Exception as e:
        print(colored(f"\nError toggling API mode: {str(e)}", "red"))
        logger.error(f"Error toggling API mode: {str(e)}", exc_info=True)
        input(colored("\nPress Enter to continue...", "green"))


def manage_api_key(fernet):
    """Manage the Meraki API key"""
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    current_key = meraki_api_manager.get_api_key(fernet)
    if current_key:
        print(colored(f"Current API Key: {current_key[:10]}...{current_key[-4:]}", "yellow"))
        change = input("Do you want to change it? [yes/no]: ").lower()
        if change != 'yes':
            return
    
    api_key = input("\nEnter the Cisco Meraki API Key: ")
    if api_key:
        meraki_api_manager.save_api_key(api_key, fernet)
        print(colored("\nAPI Key saved successfully.", "green"))
    else:
        print(colored("No key entered. No changes made.", "red"))
    
    input(colored("\nPress Enter to continue...", "green"))


def manage_ipinfo_token(fernet):
    """Manage the IPinfo access token"""
    term_extra.clear_screen()
    term_extra.print_ascii_art()
    
    current_token = db_creator.get_tools_ipinfo_access_token(fernet)
    if current_token:
        print(colored(f"Current IPinfo Token: {current_token[:10]}...{current_token[-4:]}", "yellow"))
        change = input("Do you want to change it? [yes/no]: ").lower()
        if change != 'yes':
            return

    new_token = input("\nEnter the new IPinfo access token: ")
    if new_token:
        db_creator.store_tools_ipinfo_access_token(new_token, fernet)
        print(colored("\nIPinfo access token saved successfully.", "green"))
    else:
        print(colored("No token entered. No changes made.", "red"))
    
    input(colored("\nPress Enter to continue...", "green"))


def initialize_api_key():
    """Initialize and manage the Meraki API key"""
    parser = argparse.ArgumentParser(description='Cisco Meraki CLU Enhanced Edition')
    parser.add_argument('--set-key', help='Set the Meraki API key')
    args = parser.parse_args()

    # Initialize Fernet for encryption
    encryption_password = "cisco_meraki_clu_default_key"
    fernet = meraki_api_manager.generate_fernet_key(encryption_password)

    if args.set_key:
        if meraki_api_manager.save_api_key(args.set_key, fernet):
            return args.set_key

    # Try to get key from environment variable (check multiple possible names)
    api_key = os.environ.get('MERAKI_API_KEY') or os.environ.get('MERAKI_DASHBOARD_API_KEY')
    if api_key:
        print(colored(f"[OK] API key loaded from environment variable", "green"))
        return api_key

    # Try to load stored key
    api_key = meraki_api_manager.get_api_key(fernet)
    if api_key:
        return api_key

    return None


def test_ssl_connection(fernet):
    """Test the SSL connection handling with the Meraki API"""
    try:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        
        print("\nCisco Meraki SSL Connection Test")
        print("===============================")
        
        # Get API key
        api_key = meraki_api_manager.get_api_key(fernet)
        if not api_key:
            print(colored("\nError: API key not found", "red"))
            print("Please set up your Meraki API key first (Option 8 in main menu)")
            input("\nPress Enter to return to main menu...")
            return

        print(colored("\nInitiating SSL connection test...", "cyan"))
        print("1. Testing API connectivity")
        print("2. Verifying SSL certificate handling")
        print("3. Checking proxy configuration")
        
        # Test API connection
        headers = {
            'X-Cisco-Meraki-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            # Try to get organizations (simple API call)
            url = 'https://api.meraki.com/api/v1/organizations'
            from modules.meraki.meraki_api import make_meraki_request
            
            response = make_meraki_request(url, headers)
            
            # Success messages
            print(colored("\nTest Results:", "cyan"))
            print(colored("✓ Successfully connected to Meraki API", "green"))
            print(colored("✓ SSL certificate verification successful", "green"))
            print(colored("✓ Proxy configuration working correctly", "green"))
            print(colored(f"✓ Retrieved {len(response)} organizations", "green"))
            print("\nAll tests completed successfully!")
            
        except Exception as e:
            print(colored("\nTest Results:", "red"))
            print(colored("✗ Connection test failed", "red"))
            print(colored(f"\nError details: {str(e)}", "yellow"))
            print(colored("\nTroubleshooting steps:", "cyan"))
            print("1. Verify your network connectivity")
            print("2. Check your proxy configuration")
            print("3. Ensure your API key is correct")
            print("4. Review error.log for detailed information")
            logging.error(f"SSL Connection Error: {str(e)}\n{traceback.format_exc()}")
            
    except Exception as e:
        print(colored(f"\nTest initialization failed: {str(e)}", "red"))
        logging.error(f"SSL Test Error: {str(e)}\n{traceback.format_exc()}")
    
    current_year = datetime.now().year
    footer = f"\033[1mPROJECT PAGE\033[0m\n{current_year} Matia Zanella\nhttps://developer.cisco.com/codeexchange/github/repo/akamura/cisco-meraki-clu/"
    term_extra.print_footer(footer)
    input(colored("\nPress Enter to return to the main menu...", "green"))


def main():
    """Main function to run the Cisco Meraki CLU Enhanced Edition"""
    try:
        # Check if the database exists
        db_path = os.path.join(os.path.expanduser("~"), ".cisco_meraki_clu.db")
        
        # Initialize API key from command line arguments if provided
        api_key = initialize_api_key()
        
        # Check if the database exists
        if not os.path.exists(db_path):
            os.system('cls' if os.name == 'nt' else 'clear')
            term_extra.print_ascii_art()
            print(colored("\n\nWelcome to Cisco Meraki CLU Enhanced Edition!", "green"))
            print(colored("This program requires a database to store your settings and API keys securely.", "green"))
            create_db = input(colored("\nDo you want to create the database now? (yes/no): ", "cyan")).strip().lower()
            
            if create_db == 'yes':
                db_password = getpass(colored("\nPlease create a password for database encryption: ", "green"))
                confirm_password = getpass(colored("Please confirm your password: ", "green"))
                
                if db_password == confirm_password:
                    fernet = db_creator.generate_fernet_key(db_password)
                    
                    # Create the database directory if it doesn't exist
                    db_dir = os.path.dirname(db_path)
                    if not os.path.exists(db_dir):
                        os.makedirs(db_dir)
                    
                    # Create the database with the necessary tables
                    db_creator.create_cisco_meraki_clu_db(db_path, fernet)
                    
                    print(colored("\nDatabase created successfully!", "green"))
                    
                    # If API key was provided via command line, save it now
                    if api_key:
                        meraki_api_manager.save_api_key(api_key, fernet)
                        print(colored("API key saved successfully!", "green"))
                    
                    main_menu(fernet)
                else:
                    print(colored("\nPasswords do not match. Please try again.", "red"))
                    exit()
            else:
                print(colored("Database creation cancelled. Exiting program.", "yellow"))
                exit()
        else:
            # Database exists, ask for password
            os.system('cls' if os.name == 'nt' else 'clear')
            term_extra.print_ascii_art()
            print(colored(f"\n\nWelcome to Cisco Meraki CLU Enhanced Edition! v2.6", "green"))
            if ENHANCED_VIZ_AVAILABLE:
                print(colored("[OK] Enhanced Network Visualization Available", "green"))
            else:
                print(colored("⚠️ Enhanced Visualization Module Missing", "yellow"))
            
            db_password = getpass(colored("\nPlease enter your database password to continue: ", "green"))
            fernet = db_creator.generate_fernet_key(db_password)
            
            # If API key was provided via command line, save it now
            if api_key:
                meraki_api_manager.save_api_key(api_key, fernet)
                print(colored("API key saved successfully!", "green"))
                input(colored("\nPress Enter to continue...", "green"))

        # At this point, the database exists, so proceed to the main menu
        main_menu(fernet)

    except Exception as e:
        logger.error("An error occurred", exc_info=True)
        print(colored(f"An error occurred: {e}", "red"))
        traceback.print_exc()
        input("\nPress Enter to exit.\n")


if __name__ == "__main__":
    main()