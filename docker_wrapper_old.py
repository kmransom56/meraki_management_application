#!/usr/bin/env python3
"""
Docker wrapper for Cisco Meraki CLI - Fixed Flask imports
"""

import os
import sys
import json
import threading
import time
import subprocess
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from datetime import datetime
import logging

# Add the current directory to Python path so we can import your existing code
sys.path.append('/app')

# Try to import your existing main.py functions
try:
    import main
    print("✅ Successfully imported your main.py")
    MAIN_IMPORTED = True
except ImportError as e:
    print(f"⚠️  Could not import main.py: {e}")
    print("Running in standalone mode - you can still access your CLI via container")
    MAIN_IMPORTED = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-me')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/docker_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MerakiAppManager:
    """Manages the Meraki application state and provides web interface"""
    
    def __init__(self):
        self.app_status = "running"
        self.last_error = None
        self.api_configured = False
        self.ensure_directories()
        self.check_main_py()
        
    def ensure_directories(self):
        """Create necessary directories"""
        directories = ['/app/logs', '/app/data', '/app/config', '/app/static', '/app/templates']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def check_main_py(self):
        """Check if main.py exists and is accessible"""
        if os.path.exists('/app/main.py'):
            logger.info("✅ main.py found")
            return True
        else:
            logger.warning("⚠️  main.py not found in /app/")
            return False
    
    def run_original_main(self):
        """Run your original main.py application"""
        try:
            if MAIN_IMPORTED:
                # If we can import main.py, try to run it
                logger.info("Running main.py via import...")
                return main.main() if hasattr(main, 'main') else "main.py imported but no main() function found"
            else:
                # Run as subprocess
                logger.info("Running main.py as subprocess...")
                result = subprocess.run([sys.executable, '/app/main.py'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=30)
                return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            logger.error(f"Error running main.py: {e}")
            return f"Error: {e}"
    
    def get_organizations(self):
        """Get organizations - integrate with your existing function"""
        try:
            if MAIN_IMPORTED and hasattr(main, 'get_organizations'):
                return main.get_organizations()
            # Add your specific function call here
            return []
        except Exception as e:
            logger.error(f"Error getting organizations: {e}")
            return []
    
    def get_networks(self, org_id):
        """Get networks - integrate with your existing function"""
        try:
            if MAIN_IMPORTED and hasattr(main, 'get_networks'):
                return main.get_networks(org_id)
            # Add your specific function call here
            return []
        except Exception as e:
            logger.error(f"Error getting networks: {e}")
            return []

# Initialize the manager
meraki_manager = MerakiAppManager()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template_or_simple('dashboard.html', 'Cisco Meraki CLI - Docker Edition')

@app.route('/health')
def health():
    """Health check endpoint for Docker and monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "cisco-meraki-cli-docker",
        "timestamp": datetime.now().isoformat(),
        "main_py_available": MAIN_IMPORTED,
        "main_py_exists": os.path.exists('/app/main.py'),
        "api_configured": meraki_manager.api_configured,
        "last_error": meraki_manager.last_error
    })

@app.route('/run-original')
def run_original():
    """Run your original main.py application"""
    try:
        result = meraki_manager.run_original_main()
        return jsonify({
            "success": True, 
            "message": "Original main.py executed",
            "output": result
        })
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

@app.route('/cli-access')
def cli_access():
    """Instructions for accessing the CLI directly"""
    instructions = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CLI Access - Cisco Meraki CLI</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; }
            .command { background: #343a40; color: #fff; padding: 15px; border-radius: 5px; font-family: monospace; margin: 10px 0; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 Access Your Original CLI</h1>
            <p>Your CLI works exactly as before! Choose your preferred method:</p>
            
            <h3>Method 1: Direct Access (Recommended)</h3>
            <div class="command">docker exec -it cisco-meraki-cli-app python main.py</div>
            
            <h3>Method 2: Interactive Shell</h3>
            <div class="command">docker exec -it cisco-meraki-cli-app bash<br>python main.py</div>
            
            <h3>Method 3: Via Web Interface</h3>
            <a href="/run-original" class="btn">🚀 Run main.py</a>
            
            <br><br>
            <p><a href="/">← Back to Dashboard</a></p>
        </div>
    </body>
    </html>
    """
    return instructions

@app.route('/api/organizations')
def api_organizations():
    """API endpoint for organizations"""
    try:
        orgs = meraki_manager.get_organizations()
        return jsonify({"success": True, "data": orgs})
    except Exception as e:
        logger.error(f"API organizations error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/networks/<org_id>')
def api_networks(org_id):
    """API endpoint for networks"""
    try:
        networks = meraki_manager.get_networks(org_id)
        return jsonify({"success": True, "data": networks})
    except Exception as e:
        logger.error(f"API networks error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/config')
def config_page():
    """Configuration page"""
    return render_template_or_simple('config.html', 'Configuration')

@app.route('/topology')
def topology():
    """Network topology page - integrate with your D3.js visualization"""
    if os.path.exists('/app/templates/topology.html'):
        return render_template('topology.html')
    elif os.path.exists('/app/static/topology.html'):
        return send_from_directory('/app/static', 'topology.html')
    else:
        # Simple placeholder that you can customize
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Network Topology</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Network Topology</h1>
                <p>Your D3.js topology visualization will appear here.</p>
                <h3>To integrate your existing topology:</h3>
                <ol>
                    <li>Copy your topology HTML to /app/templates/topology.html</li>
                    <li>Copy any JS/CSS files to /app/static/</li>
                    <li>Update this route to serve your topology</li>
                </ol>
                <p><a href="/">← Back to Dashboard</a></p>
            </div>
        </body>
        </html>
        """

# Static file serving (fixed for Flask 2.3.3)
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('/app/static', filename)

def render_template_or_simple(template_name, title):
    """Try to render template, fall back to simple HTML"""
    try:
        return render_template(template_name)
    except:
        # Simple fallback if templates don't exist yet
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .status-healthy {{ color: #28a745; font-weight: bold; }}
                .command {{ background: #343a40; color: #fff; padding: 10px; border-radius: 3px; font-family: monospace; }}
                .card {{ margin: 15px 0; }}
            </style>
        </head>
        <body>
            <nav class="navbar navbar-dark bg-primary">
                <div class="container">
                    <a class="navbar-brand" href="/">🚀 Cisco Meraki CLI - Docker Edition</a>
                </div>
            </nav>
            <div class="container mt-4">
                <h1>{title}</h1>
                
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5>🔧 Original CLI</h5>
                                <p>Access your existing main.py application</p>
                                <a href="/cli-access" class="btn btn-primary">Access CLI</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5>📊 Network Topology</h5>
                                <p>View your D3.js network visualization</p>
                                <a href="/topology" class="btn btn-success">View Topology</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5>⚙️ Configuration</h5>
                                <p>Manage API keys and settings</p>
                                <a href="/config" class="btn btn-warning">Configure</a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <div class="card">
                        <div class="card-body">
                            <h3>📈 System Status</h3>
                            <p><strong>Main.py Available:</strong> <span class="status-healthy">{'✅ Yes' if MAIN_IMPORTED else '⚠️ Import Failed'}</span></p>
                            <p><strong>Main.py File Exists:</strong> <span class="status-healthy">{'✅ Yes' if os.path.exists('/app/main.py') else '❌ No'}</span></p>
                            <p><strong>Docker Status:</strong> <span class="status-healthy">✅ Running</span></p>
                            
                            <h4>🚀 Quick Access</h4>
                            <div class="command">docker exec -it cisco-meraki-cli-app python main.py</div>
                            <small class="text-muted">This runs your CLI exactly as before - all features preserved!</small>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

if __name__ == '__main__':
    # Create necessary directories
    meraki_manager.ensure_directories()
    
    # Log startup information
    logger.info("🚀 Starting Cisco Meraki CLI Docker Interface")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"🐍 Python path: {sys.path}")
    logger.info(f"📄 Main.py exists: {os.path.exists('/app/main.py')}")
    logger.info(f"📦 Main.py imported: {MAIN_IMPORTED}")
    
    # Start the Flask application
    print("🌐 Web interface starting at http://localhost:5000")
    print("🔧 Original CLI access: docker exec -it cisco-meraki-cli-app python main.py")
    app.run(host='0.0.0.0', port=5000, debug=False)