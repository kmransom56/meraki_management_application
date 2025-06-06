# Cisco Meraki CLI – Quick Start Guide

## For Non-Technical Users

### 1. Unzip the Folder
- Right-click the zip file and select **Extract All...**
- Choose a location (e.g., Desktop or Documents).

### 2. Install Python (if not already installed)
- Download Python 3.12 from: https://www.python.org/downloads/
- Run the installer and check “Add Python to PATH”.
- Complete the installation.

### 3. Install Required Packages
- Open PowerShell in the unzipped folder.
- Run:
  ```pwsh
  pip install -r requirements.txt
  ```

### 4. Launch the CLI
- Double-click `start_interactive_cli.ps1` in the folder.
- If prompted, right-click and select **Run with PowerShell**.

### 5. First Time Setup
- The CLI will prompt you to create a secure database and enter your Meraki API key.

---

## For Docker Users
- Open PowerShell or Command Prompt.
- Run:
  ```pwsh
  docker exec -it cisco-meraki-cli-app python main.py
  ```

---

# Cisco Meraki API Integration Tool

A Python-based tool for interacting with the Cisco Meraki API, featuring:
- Network topology visualization
- Device management
- SSL proxy support (Zscaler compatible)
- Secure API key management
- Official Meraki Dashboard API SDK integration

## Features
- Interactive network topology visualization using D3.js
- Device status monitoring
- Network health metrics
- Proxy-aware SSL handling
- Secure API key storage
- Dual API mode: Custom implementation or Official SDK

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/keransom56/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

# Cisco Meraki CLI

## Quick Start: Launch the Interactive CLI

To make it as easy as possible for non-technical users to launch the CLI:

### Windows (Recommended)
- Double-click `start_interactive_cli.ps1` to open the CLI in a new PowerShell window.
- Or, right-click and select **Run with PowerShell**.

### Docker Users
- Open PowerShell or Command Prompt.
- Run:
  ```pwsh
  docker exec -it cisco-meraki-cli-app python main.py
  ```

### First Time Setup
- The CLI will prompt you to create a secure database and set your Meraki API key.

---

## Why this is easy
- No need to open a terminal and type commands—just double-click the script!
- Works on any Windows system with Python and PowerShell.
- For Docker, just copy-paste the command above.

## API Mode Selection
The application now supports two API modes:

1. **Custom API Implementation (Default)**
   - Uses the custom API implementation with robust error handling
   - Includes special handling for Windows proxy environments (like Zscaler)
   - Recommended for most users, especially in corporate environments with proxies

2. **Official Meraki SDK**
   - Uses the official Meraki Dashboard API Python SDK
   - Provides access to all API endpoints
   - May have limitations in some proxy environments

You can switch between modes in the main menu.

## SSL Certificate Handling
The application implements a robust SSL verification strategy:
- Primary: Attempts secure verification using system CA certificates
- Fallback: For Windows proxy environments, disables verification if primary fails
- Clear error messages for troubleshooting

## Security Features
- API keys are stored securely using Fernet encryption
- SSL certificate handling with proxy support
- Environment variable support for API keys
- Comprehensive error handling and logging

## Requirements
- Python 3.7+
- See requirements.txt for dependencies# cisco-meraki-clu
