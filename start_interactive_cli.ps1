# PowerShell script to launch the Cisco Meraki CLI interactive CLI in a new terminal window
$scriptPath = Join-Path $PSScriptRoot 'main.py'
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "python `"$scriptPath`""
