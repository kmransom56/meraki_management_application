# Cisco Meraki CLI Tool - Enhanced Edition

A comprehensive Python CLI tool for managing Cisco Meraki networks with enhanced visualization capabilities and corporate SSL support.

## ✅ Recent Updates - SSL Issues Resolved!

### 🔒 Corporate SSL Environment Support
- **SSL certificate verification issues FIXED**
- Full support for Zscaler, Blue Coat, and corporate SSL inspection
- Automatic SSL fixes applied on startup
- No more SSL warnings or connection failures

## 🚀 Key Features

### Network Management
- Complete network device management
- Real-time monitoring and statistics
- Network topology visualization
- Client and device information

### Corporate Environment Ready
- ✅ SSL inspection compatibility (Zscaler, Blue Coat, etc.)
- ✅ Automatic SSL error suppression
- ✅ Corporate proxy support
- ✅ Enhanced error handling and logging

## Issues Previously Addressed

### 1. SSL Certificate Verification Errors ✅ FIXED
- ✅ SSL verification failures resolved
- ✅ API requests now work seamlessly in corporate environments
- ✅ Proper certificate handling implemented

### 2. API Request Issues ✅ IMPROVED
- ✅ Enhanced error handling for 404 errors
- ✅ Better rate limiting and timeout handling  
- ✅ Robust error recovery mechanisms

### 3. Web Visualization Problems ✅ ENHANCED
- ✅ Devices display properly in web interface
- ✅ Network topology rendering improved
- ✅ Complete device information in statistics

## Project Structure

```
├── src/
│   ├── api/
│   │   ├── meraki_client.py      # Improved Meraki API client with SSL handling
│   │   └── error_handler.py      # Centralized error handling
│   ├── web/
│   │   ├── app.py                # Flask application
│   │   ├── templates/            # HTML templates
│   │   └── static/               # CSS, JS, images
│   ├── utils/
│   │   ├── logger.py             # Enhanced logging setup
│   │   └── ssl_helper.py         # SSL certificate utilities
│   └── main.py                   # Main CLI application
├── tests/                        # Unit tests
├── logs/                         # Log files
├── config/                       # Configuration files
└── docs/                         # Documentation
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Meraki API key
   ```

3. **Run the Application**
   ```bash
   python src/main.py
   ```

4. **Access Web Interface**
   ```
   http://localhost:5001
   ```

## Features

- ✅ Robust SSL certificate handling
- ✅ Comprehensive API error handling
- ✅ Enhanced logging and debugging
- ✅ Improved web visualization
- ✅ Device topology display
- ✅ Network statistics dashboard

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Debugging
```bash
python src/main.py --debug --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
