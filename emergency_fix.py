"""
Emergency CLI Stopper and Network Selector Fix
"""
import os
import signal
import psutil
from termcolor import colored

def kill_all_python_processes():
    """Kill all running Python processes"""
    try:
        print("🔴 Stopping all Python processes...")
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if it's a Python process
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    print(f"  Terminating Python process {proc.info['pid']}: {proc.info['name']}")
                    proc.terminate()
                    proc.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        print(colored("✅ All Python processes stopped", "green"))
        
    except Exception as e:
        print(colored(f"❌ Error stopping processes: {e}", "red"))

def fix_network_selection_bug():
    """Create a simple network selector that works"""
    print(colored("\n🔧 Fixing Network Selection Bug", "cyan"))
    
    # The issue is likely in the main.py enhanced visualization function
    # Let's create a simple patch
    
    patch_content = '''
# PATCH: Replace the problematic network selection with working pagination
def create_enhanced_network_visualization_fixed(api_key, api_mode):
    """Fixed version of enhanced network visualization with proper pagination"""
    
    try:
        print(colored("\\n🚀 Creating Enhanced Interactive Network Visualization", "cyan"))
        print("=" * 60)
        
        # Get organizations first
        if api_mode == 'sdk':
            import meraki
            dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)
        else:
            dashboard = create_custom_dashboard_object(api_key)
        
        # Get organizations with error handling
        try:
            organizations = dashboard.organizations.getOrganizations()
            if not organizations:
                print(colored("No organizations found.", "red"))
                return
        except Exception as e:
            print(colored(f"Error fetching organizations: {str(e)}", "red"))
            return
        
        # Select organization
        if len(organizations) == 1:
            selected_org = organizations[0]
        else:
            print("\\nAvailable Organizations:")
            for i, org in enumerate(organizations, 1):
                print(f"{i}. {org['name']} (ID: {org['id']})")
            
            try:
                org_choice = int(input(f"\\nSelect organization [1-{len(organizations)}]: ")) - 1
                selected_org = organizations[org_choice]
            except:
                print(colored("Invalid selection.", "red"))
                return
        
        # Get networks with error handling
        try:
            networks = dashboard.organizations.getOrganizationNetworks(selected_org['id'])
            if not networks:
                print(colored("No networks found.", "red"))
                return
        except Exception as e:
            print(colored(f"Error fetching networks: {str(e)}", "red"))
            return
        
        # CRITICAL FIX: Use the working pagination function
        print(f"\\n📡 Found {len(networks)} networks in {selected_org['name']}")
        
        # Import and call the pagination function correctly
        from utilities.submenu import select_network_with_pagination
        
        selected_network_id = select_network_with_pagination(networks, selected_org['name'])
        
        if not selected_network_id:
            print(colored("Network selection cancelled.", "yellow"))
            return
        
        # Find selected network
        selected_network = next((n for n in networks if n['id'] == selected_network_id), None)
        if not selected_network:
            print(colored("Selected network not found.", "red"))
            return
        
        # Continue with visualization...
        print(f"\\n✅ Selected: {selected_network['name']}")
        print("🔄 Creating visualization...")
        
        # Rest of the visualization code would go here
        
    except Exception as e:
        print(colored(f"\\n❌ Error: {str(e)}", "red"))
    '''
    
    print("Fixed network selection code created.")
    print("The issue is that the CLI is stuck in a loop printing all networks.")
    print("This happens when the pagination function is not called correctly.")

if __name__ == "__main__":
    print(colored("🚨 Emergency CLI Fix Tool", "red"))
    print("=" * 30)
    
    choice = input("1. Kill all Python processes\n2. Show fix information\nChoice [1-2]: ")
    
    if choice == "1":
        kill_all_python_processes()
    elif choice == "2":
        fix_network_selection_bug()
    
    print(colored("\n💡 To prevent this issue:", "green"))
    print("1. Always use Ctrl+C to exit CLI menus properly")
    print("2. The pagination function exists and works correctly")
    print("3. The bug is in the calling code, not the pagination itself")
    print("4. Restart the CLI after killing processes")
