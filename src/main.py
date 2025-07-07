"""
Main CLI application with improved error handling and debugging capabilities.
"""
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from api.meraki_client import MerakiClient
from api.error_handler import handle_api_errors, format_error_message
from web.app import create_app
from utils.logger import setup_logger, setup_api_logger, log_network_topology
from utils.ssl_helper import validate_meraki_api_ssl, diagnose_ssl_issues


def load_config():
    """Load configuration from environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    config = {
        'api_key': os.getenv('MERAKI_API_KEY'),
        'base_url': os.getenv('MERAKI_BASE_URL', 'https://api.meraki.com/api/v1'),
        'ssl_verify': os.getenv('SSL_VERIFY', 'True').lower() == 'true',
        'timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
        'flask_port': int(os.getenv('FLASK_PORT', '5001')),
        'flask_debug': os.getenv('FLASK_DEBUG', 'True').lower() == 'true',
        'log_level': os.getenv('LOG_LEVEL', 'INFO')
    }
    
    return config


def test_ssl_connectivity(logger):
    """Test SSL connectivity to Meraki API."""
    logger.info("Testing SSL connectivity to Meraki API...")
    
    if validate_meraki_api_ssl():
        logger.info("✓ SSL connectivity test passed")
        return True
    else:
        logger.warning("✗ SSL connectivity test failed")
        
        # Diagnose issues
        diagnosis = diagnose_ssl_issues('https://api.meraki.com')
        logger.info("SSL Diagnosis Results:")
        for recommendation in diagnosis['recommendations']:
            logger.warning(f"  - {recommendation}")
        
        return False


@handle_api_errors
def select_organization(client: MerakiClient, logger) -> str:
    """Select organization interactively."""
    logger.info("Fetching organizations...")
    orgs = client.get_organizations()
    
    if not orgs:
        raise Exception("No organizations found or API request failed")
    
    print("\nAvailable Organizations:")
    for i, org in enumerate(orgs, 1):
        print(f"{i}. {org['name']}")
    
    while True:
        try:
            choice = int(input("\nSelect an Organization (enter the number): "))
            if 1 <= choice <= len(orgs):
                selected_org = orgs[choice - 1]
                logger.info(f"Selected organization: {selected_org['name']} (ID: {selected_org['id']})")
                return selected_org['id']
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


@handle_api_errors
def select_network(client: MerakiClient, org_id: str, logger) -> Dict[str, Any]:
    """Select network interactively."""
    logger.info(f"Fetching networks for organization {org_id}...")
    networks = client.get_networks(org_id)
    
    if not networks:
        raise Exception("No networks found or API request failed")
    
    print(f"\nFound {len(networks)} networks:")
    for i, network in enumerate(networks[:20], 1):  # Show first 20
        print(f"{i}. {network['name']}")
    
    if len(networks) > 20:
        print(f"... and {len(networks) - 20} more networks")
    
    while True:
        try:
            choice = int(input("\nSelect a Network (enter the number): "))
            if 1 <= choice <= min(20, len(networks)):
                selected_network = networks[choice - 1]
                logger.info(f"Selected network: {selected_network['name']} (ID: {selected_network['id']})")
                return selected_network
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


@handle_api_errors
def gather_network_data(client: MerakiClient, network_id: str, logger) -> Dict[str, Any]:
    """Gather comprehensive network data."""
    logger.info(f"Gathering network data for {network_id}...")
    
    # Get network details
    network = client.get_network(network_id)
    if not network:
        raise Exception(f"Could not retrieve network details for {network_id}")
    
    # Get devices
    devices = client.get_devices(network_id)
    logger.info(f"Found {len(devices)} devices")
    
    # Get clients
    clients = client.get_clients(network_id)
    logger.info(f"Found {len(clients)} clients")
    
    # Try to get topology links
    topology_links = client.get_topology_links(network_id)
    
    # If no API topology, build manually
    if not topology_links:
        logger.info("Building topology manually...")
        topology = client.build_manual_topology(devices, clients)
    else:
        topology = {
            'nodes': [],
            'links': topology_links,
            'metadata': {
                'source': 'api',
                'linkCount': len(topology_links)
            }
        }
    
    # Log topology information
    log_network_topology(logger, devices, clients, topology.get('links', []))
    
    network_data = {
        'network': network,
        'devices': devices,
        'clients': clients,
        'topology': topology,
        'lastUpdated': datetime.now().isoformat(),
        'metadata': {
            'deviceCount': len(devices),
            'clientCount': len(clients),
            'networkId': network_id,
            'networkName': network['name']
        }
    }
    
    return network_data


def start_web_visualization(network_data: Dict[str, Any], config: Dict[str, Any], logger):
    """Start the web visualization server."""
    logger.info("Starting web visualization server...")
    
    app = create_app(network_data)
    
    print(f"\n🌐 Network Topology Visualization")
    print(f"📊 Network: {network_data['network']['name']}")
    print(f"🔧 Devices: {len(network_data['devices'])}")
    print(f"💻 Clients: {len(network_data['clients'])}")
    print(f"🌐 Server: http://localhost:{config['flask_port']}")
    print(f"📝 Press Ctrl+C to stop the server\n")
    
    try:
        app.run(
            host='0.0.0.0', 
            port=config['flask_port'], 
            debug=config['flask_debug']
        )
    except KeyboardInterrupt:
        logger.info("Web server stopped by user")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='Meraki Network Topology Debugger')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--test-ssl', action='store_true', help='Test SSL connectivity only')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    parser.add_argument('--org-id', help='Organization ID (skip interactive selection)')
    parser.add_argument('--network-id', help='Network ID (skip interactive selection)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if not config['api_key']:
        print("Error: MERAKI_API_KEY environment variable not set")
        print("Please create a .env file with your API key:")
        print("MERAKI_API_KEY=your_api_key_here")
        return 1
    
    # Set up logging
    log_level = 'DEBUG' if args.debug or args.verbose else config['log_level']
    logger = setup_logger(log_level=log_level)
    api_logger = setup_api_logger()
    
    logger.info("Starting Meraki Network Topology Debugger")
    logger.info(f"Configuration: SSL Verify: {config['ssl_verify']}, Timeout: {config['timeout']}s")
    
    # Test SSL connectivity if requested
    if args.test_ssl:
        test_ssl_connectivity(logger)
        return 0
    
    try:
        # Test SSL connectivity
        if not test_ssl_connectivity(logger):
            logger.warning("SSL connectivity issues detected, but continuing...")
        
        # Create Meraki client
        client = MerakiClient(
            api_key=config['api_key'],
            base_url=config['base_url'],
            timeout=config['timeout'],
            ssl_verify=config['ssl_verify']
        )
        
        # Select organization
        if args.org_id:
            org_id = args.org_id
            logger.info(f"Using provided organization ID: {org_id}")
        else:
            org_id = select_organization(client, logger)
        
        # Select network
        if args.network_id:
            network_id = args.network_id
            logger.info(f"Using provided network ID: {network_id}")
            # Get network details
            network = client.get_network(network_id)
            if not network:
                logger.error(f"Network {network_id} not found")
                return 1
        else:
            network = select_network(client, org_id, logger)
            network_id = network['id']
        
        # Gather network data
        network_data = gather_network_data(client, network_id, logger)
        
        # Start web visualization
        start_web_visualization(network_data, config, logger)
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        return 0
        
    except Exception as e:
        error_msg = format_error_message(e)
        logger.error(f"Application error: {error_msg}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
