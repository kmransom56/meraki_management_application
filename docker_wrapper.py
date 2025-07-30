#!/usr/bin/env python3
"""
Working Docker wrapper for Cisco Meraki CLI
"""

import os
import sys
from flask import Flask, jsonify, send_from_directory, abort
from datetime import datetime

# Add current directory to path
sys.path.append('/app')

# Try to import your main.py
try:
    import main
    MAIN_IMPORTED = True
    print("✅ Successfully imported main.py")
except ImportError as e:
    MAIN_IMPORTED = False
    print(f"⚠️ Could not import main.py: {e}")
    print("CLI still accessible via: docker exec -it cisco-meraki-cli-app python main.py")

app = Flask(__name__)

@app.route('/')
def index():
    """Main page"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cisco Meraki CLI - Docker Edition</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ color: #1e88e5; border-bottom: 2px solid #1e88e5; padding-bottom: 10px; }}
            .card {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #1e88e5; }}
            .status {{ color: #28a745; font-weight: bold; }}
            .btn {{ background: #1e88e5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; display: inline-block; }}
            .btn:hover {{ background: #1565c0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🚀 Cisco Meraki CLI - Docker Edition</h1>
            
            <div class="card">
                <h3>✅ Success! Your Application is Running</h3>
                <p class="status">Docker container is working perfectly!</p>
                <p>Your Cisco Meraki CLI has been successfully containerized.</p>
            </div>

            <div class="card">
                <h3>🔧 Access Your Original CLI</h3>
                <p>Your existing CLI works exactly as before:</p>
                <div class="command">docker exec -it cisco-meraki-cli-app python main.py</div>
                <p><small>This gives you full access to all your existing features.</small></p>
            </div>

            <div class="card">
                <h3>📊 System Status</h3>
                <p><strong>Main.py Imported:</strong> <span class="status">{'✅ Yes' if MAIN_IMPORTED else '⚠️ No (but still accessible)'}</span></p>
                <p><strong>Main.py File Exists:</strong> <span class="status">{'✅ Yes' if os.path.exists('/app/main.py') else '❌ No'}</span></p>
                <p><strong>Docker Status:</strong> <span class="status">✅ Running</span></p>
                <p><strong>Working Directory:</strong> {os.getcwd()}</p>
            </div>

            <div class="card">
                <h3>🎯 Available Endpoints</h3>
                <a href="/health" class="btn">Health Check</a>
                <a href="/cli-instructions" class="btn">CLI Instructions</a>
                <a href="/system-info" class="btn">System Info</a>
                <a href="/visualizations" class="btn">View Visualizations</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "cisco-meraki-cli-docker",
        "timestamp": datetime.now().isoformat(),
        "main_py_imported": MAIN_IMPORTED,
        "main_py_exists": os.path.exists('/app/main.py'),
        "working_directory": os.getcwd(),
        "python_version": sys.version
    })

@app.route('/cli-instructions')
def cli_instructions():
    """CLI access instructions"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CLI Instructions</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .command { background: #343a40; color: #fff; padding: 15px; border-radius: 5px; font-family: monospace; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🔧 CLI Access Instructions</h1>
        
        <h2>Method 1: Direct Access (Recommended)</h2>
        <div class="command">docker exec -it cisco-meraki-cli-app python main.py</div>
        
        <h2>Method 2: Interactive Shell</h2>
        <div class="command">docker exec -it cisco-meraki-cli-app bash<br>python main.py</div>
        
        <h2>Method 3: Check if main.py works</h2>
        <div class="command">docker exec -it cisco-meraki-cli-app python -c "import main; print('main.py is accessible')"</div>
        
        <p><a href="/">← Back to Dashboard</a></p>
    </body>
    </html>
    """

@app.route('/system-info')
def system_info():
    """System information"""
    try:
        files_in_app = os.listdir('/app')
    except:
        files_in_app = ['Error reading directory']
    
    return jsonify({
        "working_directory": os.getcwd(),
        "python_executable": sys.executable,
        "files_in_app": files_in_app,
        "main_py_exists": os.path.exists('/app/main.py'),
        "main_py_imported": MAIN_IMPORTED,
        "environment": dict(os.environ)
    })

@app.route('/visualizations')
def visualizations():
    """List available visualization files"""
    viz_dir = '/home/merakiuser/meraki_visualizations'
    try:
        if os.path.exists(viz_dir):
            files = [f for f in os.listdir(viz_dir) if f.endswith('.html')]
            if not files:
                files_list = "<p>No visualization files found yet. Run your CLI to generate some!</p>"
            else:
                files_list = "<ul>"
                for file in sorted(files):
                    files_list += f'<li><a href="/view-viz/{file}" target="_blank">{file}</a> <small>(Click to open)</small></li>'
                files_list += "</ul>"
        else:
            files_list = "<p>Visualization directory not found. Make sure volume is mounted correctly.</p>"
    except Exception as e:
        files_list = f"<p>Error reading visualization directory: {e}</p>"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Visualizations</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .command {{ background: #343a40; color: #fff; padding: 15px; border-radius: 5px; font-family: monospace; margin: 10px 0; }}
            ul {{ line-height: 1.8; }}
            a {{ color: #1e88e5; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>🌐 Network Topology Visualizations</h1>
        
        <h2>Available Visualizations:</h2>
        {files_list}
        
        <h2>Generate New Visualization:</h2>
        <div class="command">docker exec -it cisco-meraki-cli-app python main.py</div>
        <p><small>Choose the network visualization option in your CLI</small></p>
        
        <p><a href="/">← Back to Dashboard</a></p>
    </body>
    </html>
    """

@app.route('/view-viz/<filename>')
def view_visualization(filename):
    """Serve visualization files"""
    viz_dir = '/home/merakiuser/meraki_visualizations'
    try:
        return send_from_directory(viz_dir, filename)
    except FileNotFoundError:
        abort(404, description=f"Visualization file '{filename}' not found")

if __name__ == '__main__':
    print("🚀 Starting Cisco Meraki CLI Docker Interface")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📄 Main.py exists: {os.path.exists('/app/main.py')}")
    print(f"📦 Main.py imported: {MAIN_IMPORTED}")
    print("🌐 Web interface will be available at http://localhost:5000")
    print("🔧 CLI access: docker exec -it cisco-meraki-cli-app python main.py")
    
    app.run(host='0.0.0.0', port=5000, debug=True)