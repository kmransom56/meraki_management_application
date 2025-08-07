# Environment Variable Configuration Guide

This guide explains how to configure your Cisco Meraki CLI application using environment variables for secure and flexible deployment.

## Quick Setup

### Option 1: Interactive Setup Script (Recommended)
```bash
python setup_env.py
```

This interactive script will guide you through configuring all necessary environment variables and create a `.env` file automatically.

### Option 2: Manual Configuration
1. Copy the example file: `cp .env.example .env`
2. Edit the `.env` file with your actual values
3. Ensure the `.env` file is in your project root directory

## Environment Variables Reference

### 🔑 Meraki Configuration (Required)

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `MERAKI_API_KEY` | Your Meraki Dashboard API key | `fd3b9969d25792d90f0789a7e28cc661c81e2150` | ✅ Yes |
| `MERAKI_BASE_URL` | Meraki API base URL | `https://api.meraki.com/api/v1` | No (default provided) |
| `MERAKI_API_MODE` | API mode: `custom` or `sdk` | `custom` | No (default: custom) |

### 🔥 FortiGate Configuration (Optional)

#### FortiManager Settings
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `FORTIMANAGER_HOST` | FortiManager hostname/IP | `fortimanager.company.com` | No |
| `FORTIMANAGER_USERNAME` | FortiManager username | `admin` | No |
| `FORTIMANAGER_PASSWORD` | FortiManager password | `your_password` | No |

#### Direct FortiGate Settings
| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `FORTIGATE_DEVICES` | JSON array of FortiGate devices | See example below | No |

**FortiGate Devices JSON Format:**
```json
[
  {
    "name": "FG-Main",
    "host": "192.168.1.1",
    "api_key": "your_fortigate_api_key"
  },
  {
    "name": "FG-Branch",
    "host": "192.168.2.1",
    "api_key": "your_fortigate_api_key"
  }
]
```

### 🌐 Flask Web Application Settings

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `FLASK_HOST` | Web server bind address | `0.0.0.0` | No (default: 0.0.0.0) |
| `FLASK_PORT` | Web server port | `5000` | No (default: 5000) |
| `FLASK_DEBUG` | Enable debug mode | `False` | No (default: False) |
| `FLASK_SECRET_KEY` | Flask session secret key | `your_secret_key_here` | Recommended |

### ⚙️ Application Settings

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Logging level | `INFO` | No (default: INFO) |
| `SSL_VERIFY` | Verify SSL certificates | `True` | No (default: True) |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | `30` | No (default: 30) |

### 🍔 QSR (Restaurant) Settings

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `QSR_MODE` | Enable restaurant device classification | `True` | No (default: True) |
| `QSR_LOCATION_NAME` | Restaurant/location name | `McDonald's Downtown` | No (default: Restaurant Location) |

## Sample .env File

```bash
# Environment Configuration for Cisco Meraki CLI Application

# Meraki Configuration
MERAKI_API_KEY=your_meraki_api_key_here
MERAKI_BASE_URL=https://api.meraki.com/api/v1
MERAKI_API_MODE=custom

# FortiGate Configuration (Optional)
FORTIMANAGER_HOST=
FORTIMANAGER_USERNAME=
FORTIMANAGER_PASSWORD=
FORTIGATE_DEVICES=[]

# Flask Web Application Settings
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
FLASK_SECRET_KEY=your_secret_key_here

# Application Settings
LOG_LEVEL=INFO
SSL_VERIFY=True
REQUEST_TIMEOUT=30

# QSR Settings (Restaurant-specific features)
QSR_MODE=True
QSR_LOCATION_NAME=Restaurant Location
```

## Security Best Practices

### 🔒 Protecting Sensitive Information

1. **Never commit `.env` files to version control**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use strong, unique secret keys**
   ```python
   # Generate a secure secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Restrict file permissions**
   ```bash
   chmod 600 .env
   ```

4. **Use environment-specific configurations**
   - `.env.development` for development
   - `.env.production` for production
   - `.env.testing` for testing

### 🏢 Corporate Environment Considerations

If you're in a corporate environment with SSL inspection:

1. **Set SSL_VERIFY=False** (only if necessary)
2. **Install corporate certificates**
3. **Use the SSL fixes included in the application**

## Deployment Options

### 🐳 Docker Environment Variables

```dockerfile
# In your Dockerfile or docker-compose.yml
ENV MERAKI_API_KEY=your_api_key
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
```

### ☁️ Cloud Platform Environment Variables

#### Heroku
```bash
heroku config:set MERAKI_API_KEY=your_api_key
heroku config:set FLASK_SECRET_KEY=your_secret_key
```

#### AWS Lambda/ECS
Set environment variables in your AWS console or CloudFormation template.

#### Azure App Service
Configure environment variables in the Azure portal under Configuration.

## Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Verify the API key is correct
   - Check if the key has proper permissions
   - Ensure no extra spaces or characters

2. **FortiGate Connection Issues**
   - Verify network connectivity
   - Check API key permissions
   - Ensure FortiGate API is enabled

3. **Web Application Not Starting**
   - Check port availability
   - Verify Flask configuration
   - Review log files for errors

### Debug Mode

Enable debug mode for troubleshooting:
```bash
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

### Validation

Test your configuration:
```bash
# Run the application
python comprehensive_web_app.py

# Check the startup messages for configuration status
```

## Getting API Keys

### Meraki API Key
1. Log into the Meraki Dashboard
2. Go to Organization > Settings > Dashboard API access
3. Enable API access
4. Generate your API key
5. Copy and store securely

### FortiGate API Key
1. Log into FortiGate web interface
2. Go to System > Administrators
3. Create or edit an admin user
4. Enable "REST API Access"
5. Generate API key

## Support

If you encounter issues with environment configuration:

1. Check the application logs
2. Verify all required dependencies are installed
3. Ensure proper file permissions
4. Review the troubleshooting section above

For additional help, refer to the main README.md or create an issue in the project repository.
