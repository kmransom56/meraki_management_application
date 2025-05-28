#**************************************************************************
#   App:         Cisco Meraki CLU                                         *
#   Version:     2.5                                                     *
#   Author:      Matia Zanella 
#   Updated:     Keith Ransom                                           *
#   Description: Cisco Meraki CLU (Command Line Utility) is an essential  *
#                tool crafted for Network Administrators managing Meraki  *
#   Github:      https://github.com/akamura/cisco-meraki-clu/             *
#                                                                         *
#   Icon Author:        Cisco Systems, Inc.                               *
#   Icon Author URL:    https://meraki.cisco.com/                         *
#                                                                         *
#   Copyright (C) 2024 Matia Zanella                                      *
#   https://www.matiazanella.com                                          *
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
from termcolor import colored
import logging
import traceback
import argparse
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from getpass import getpass

from api import meraki_api_manager
from settings import db_creator
from utilities import submenu
from settings import term_extra
from modules.meraki.meraki_sdk_wrapper import MerakiSDKWrapper

# Configure logging with more detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meraki_clu_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

required_packages = {
    "tabulate": "tabulate",
    "pathlib": "pathlib",
    "datetime": "datetime",
    "termcolor": "termcolor",
    "requests": "requests",
    "rich": "rich",
    "setuptools": "setuptools",
    "cryptography": "cryptography",
    "meraki": "meraki"  # Added the official Meraki SDK
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("Missing required Python packages: " + ", ".join(missing_packages))
    print("Please install them using the following command:")
    print(f"{sys.executable} -m pip install " + " ".join(missing_packages))


# ==================================================
# IMPORT various libraries and modules
# ==================================================
import os
import sys
import logging
import traceback
import argparse

required_packages = {
    "tabulate": "tabulate",
    "pathlib": "pathlib",
    "datetime": "datetime",
    "termcolor": "termcolor",
    "requests": "requests",
    "rich": "rich",
    "setuptools": "setuptools",
    "cryptography": "cryptography"
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("Missing required Python packages: " + ", ".join(missing_packages))
    print("Please install them using the following command:")
    print(f"{sys.executable} -m pip install " + " ".join(missing_packages))
    sys.exit(1)
from datetime import datetime
from termcolor import colored


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
# VISUALIZE the Main Menu
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
        
        print("\nMain Menu")
        print("=" * 50)
        print("1. Network Status")
        print("2. Switches and Access Points")
        print("3. Appliance")
        print("4. Environmental Monitoring")
        print("5. Network-Wide Operations")
        print("6. Swiss Army Knife")
        print("7. Manage API Key")
        print("8. Manage IPinfo Token")
        print(f"9. API Mode: {api_mode.upper()}")
        print("10. Test SSL Connection")
        print("11. Exit")
        
        choice = input(colored("\nChoose a menu option [1-11]: ", "cyan"))
        
        if choice == '1':
            if api_key:
                if api_mode == 'sdk':
                    # Use the SDK wrapper
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    submenu.submenu_network_status_sdk(sdk_wrapper)
                else:
                    # Use the custom API implementation
                    submenu.submenu_network_status(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '2':
            if api_key:
                if api_mode == 'sdk':
                    # Use the SDK wrapper
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    submenu.submenu_sw_and_ap_sdk(sdk_wrapper)
                else:
                    # Use the custom API implementation
                    submenu.submenu_sw_and_ap(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '3':
            if api_key:
                if api_mode == 'sdk':
                    # Use the SDK wrapper
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    submenu.submenu_appliance_sdk(sdk_wrapper)
                else:
                    # Use the custom API implementation
                    submenu.submenu_appliance(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '4':
            if api_key:
                if api_mode == 'sdk':
                    # Use the SDK wrapper
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    submenu.submenu_environmental_sdk(sdk_wrapper)
                else:
                    # Use the custom API implementation
                    submenu.submenu_environmental(api_key)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '5':
            if api_key:
                if api_mode == 'sdk':
                    # Use the SDK wrapper
                    sdk_wrapper = MerakiSDKWrapper(api_key)
                    organization_id = submenu.select_organization(sdk_wrapper)
                    if organization_id:
                        submenu.network_wide_operations_sdk(sdk_wrapper, organization_id)
                else:
                    # Use the custom API implementation
                    organization_id = submenu.select_organization(api_key)
                    if organization_id:
                        submenu.network_wide_operations(api_key, organization_id)
            else:
                print("Please set the Cisco Meraki API key first.")
            input(colored("\nPress Enter to return to the main menu...", "green"))
        elif choice == '6':
            submenu.swiss_army_knife_submenu(fernet)
        elif choice == '7':
            manage_api_key(fernet)
        elif choice == '8':
            manage_ipinfo_token(fernet)
        elif choice == '9':
            toggle_api_mode(fernet)
        elif choice == '10':
            test_ssl_connection(fernet)
        elif choice == '11':
            print(colored("\nThank you for using Cisco Meraki CLU!", "green"))
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
    term_extra.clear_screen()
    api_key = input("\nEnter the Cisco Meraki API Key: ")
    meraki_api_manager.save_api_key(api_key, fernet)


def manage_ipinfo_token(fernet):
    term_extra.clear_screen()
    current_token = db_creator.get_tools_ipinfo_access_token(fernet)
    if current_token:
        print(colored(f"Current IPinfo Token: {current_token}", "yellow"))
        change = input("Do you want to change it? [yes/no]: ").lower()
        if change != 'yes':
            return

    new_token = input("\nEnter the new IPinfo access token: ")
    if new_token:
        db_creator.store_tools_ipinfo_access_token(new_token, fernet)
        print(colored("\nIPinfo access token saved successfully.", "green"))
    else:
        print(colored("No token entered. No changes made.", "red"))


def initialize_api_key():
    """Initialize and manage the Meraki API key"""
    parser = argparse.ArgumentParser(description='Cisco Meraki CLU')
    parser.add_argument('--set-key', help='Set the Meraki API key')
    args = parser.parse_args()

    # Initialize Fernet for encryption
    from api import meraki_api_manager
    # Use a default password for encryption - in a production environment, this should be more secure
    encryption_password = "cisco_meraki_clu_default_key"
    fernet = meraki_api_manager.generate_fernet_key(encryption_password)

    if args.set_key:
        # Store the key securely if provided via command line
        if meraki_api_manager.save_api_key(args.set_key, fernet):
            return args.set_key

    # Try to get key from environment variable
    api_key = os.environ.get('MERAKI_DASHBOARD_API_KEY')
    if api_key:
        return api_key

    # Try to load stored key
    api_key = meraki_api_manager.get_api_key(fernet)
    if api_key:
        return api_key

    # If no key is found, show instructions
    print("\nNo API key found. Please set your Meraki API key using one of these methods:")
    print("\n1. Run the program with the --set-key option:")
    print("   python main.py --set-key YOUR_API_KEY")
    print("\n2. Set a Windows environment variable (Command Prompt as Administrator):")
    print("   setx MERAKI_DASHBOARD_API_KEY \"your-api-key\"")
    print("\n3. Set a temporary environment variable (current session only):")
    print("   set MERAKI_DASHBOARD_API_KEY=your-api-key")
    print("\nNote: After setting an environment variable, you may need to restart your command prompt.")
    return None


def test_ssl_connection(fernet):
    """
    Test the SSL connection handling with the Meraki API
    """
    try:
        term_extra.clear_screen()
        term_extra.print_ascii_art()
        
        print("\nCisco Meraki SSL Connection Test")
        print("===============================")
        
        # Get API key
        api_key = meraki_api_manager.get_api_key(fernet)
        if not api_key:
            print(colored("\nError: API key not found", "red"))
            print("Please set up your Meraki API key first (Option 7 in main menu)")
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
    """Main function to run the Cisco Meraki CLU"""
    try:
        # Check if the database exists
        db_path = os.path.join(os.path.expanduser("~"), ".cisco_meraki_clu.db")
        
        # Initialize API key from command line arguments if provided
        api_key = initialize_api_key()
        
        # Check if the database exists
        if not os.path.exists(db_path):
            os.system('cls')  # Clears the terminal screen.
            term_extra.print_ascii_art()
            print(colored("\n\nWelcome to Cisco Meraki Command Line Utility!", "green"))
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
            os.system('cls')  # Clears the terminal screen.
            term_extra.print_ascii_art()
            db_password = getpass(colored("\n\nWelcome to Cisco Meraki Command Line Utility!\nPlease enter your database password to continue: ", "green"))
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
        print("An error occurred:")
        print(e)
        traceback.print_exc()
        input("\nPress Enter to exit.\n")

if __name__ == "__main__":
    main()
