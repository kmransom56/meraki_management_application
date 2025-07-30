#!/usr/bin/env python3
"""
New Docker startup script for Cisco Meraki Web Application
This replaces the CLI-based approach with a modern web interface
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_environment():
    """Setup the environment for the web application"""
    # Create necessary directories
    os.makedirs('/app/logs', exist_ok=True)
    os.makedirs('/app/data', exist_ok=True)
    os.makedirs('/app/config', exist_ok=True)
    os.makedirs('/app/templates', exist_ok=True)
    os.makedirs('/app/static', exist_ok=True)
    
    # Set working directory
    os.chdir('/app')
    
    # Add to Python path
    sys.path.insert(0, '/app')
    
    logging.info("Environment setup complete")

def start_web_application():
    """Start the main web application"""
    try:
        logging.info("Starting Cisco Meraki Web Management Interface...")
        
        # Import and start the web application
        from web_app import app
        
        # Start the Flask application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        logging.error(f"Failed to start web application: {e}")
        # Fallback to original docker_wrapper if web app fails
        try:
            logging.info("Falling back to original docker wrapper...")
            import docker_wrapper
            docker_wrapper.app.run(host='0.0.0.0', port=5000, debug=False)
        except Exception as fallback_error:
            logging.error(f"Fallback also failed: {fallback_error}")
            raise

def main():
    """Main startup function"""
    print("🌐 Cisco Meraki Web Management Interface")
    print("=" * 50)
    print("🚀 Starting up...")
    
    try:
        # Setup environment
        setup_environment()
        
        # Wait a moment for any dependencies
        time.sleep(2)
        
        print("✅ Environment ready")
        print("🌐 Web interface starting on http://localhost:5000")
        print("📱 Modern dashboard with network topology visualization")
        print("🔧 No CLI commands needed - everything is web-based!")
        print("📝 Access http://localhost:5000 to get started")
        
        # Start the web application
        start_web_application()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        logging.info("Application shutdown requested")
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        logging.error(f"Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
