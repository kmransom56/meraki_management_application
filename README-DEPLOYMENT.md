# 🌐 Cisco Meraki Web Management - One-Click Deployment

## 🚀 Quick Start (For Team Members)

**No technical knowledge required - just Docker!**

### Step 1: Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Start Docker Desktop (make sure it's running)
- Have your Cisco Meraki API key ready

### Step 2: Deploy (One Click!)
1. **Double-click `DEPLOY.bat`**
2. Wait for deployment to complete (2-5 minutes)
3. Browser will automatically open to http://localhost:5000

### Step 3: Use the Application
1. Enter your Meraki API key in the web interface
2. Select your organization and network
3. Enjoy all the CLI features in a modern web interface!

---

## 🎯 What You Get

### **Complete CLI Functionality in Web Interface:**
- ✅ **Network Status** - Real-time monitoring
- ✅ **Device Management** - Switches, APs, Appliances  
- ✅ **Network Topology** - Interactive visualizations
- ✅ **Environmental Monitoring** - Temperature, power sensors
- ✅ **Swiss Army Knife Tools** - Password gen, subnet calc, IP tools
- ✅ **Settings & Configuration** - API management, SSL testing

### **Modern Web Features:**
- 📱 **Responsive Design** - Works on desktop, tablet, mobile
- 🔄 **Real-time Updates** - Live device and client statistics
- 🎨 **Modern UI** - Beautiful, intuitive interface
- 🔍 **Search & Filter** - Easy navigation and management
- 🔒 **Secure** - Same security as CLI version

---

## 📋 Management Commands

### Basic Operations:
```bash
# View application logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Update and restart
docker-compose down
docker-compose up --build -d
```

### Troubleshooting:
```bash
# Check if container is running
docker ps

# View container status
docker-compose ps

# Rebuild from scratch
docker-compose down
docker-compose up --build -d
```

---

## 🌐 Access Information

- **Web Interface:** http://localhost:5000
- **Container Name:** cisco-meraki-web-app
- **Ports Used:** 5000 (main), 5001-5010 (additional services)

---

## 🔧 Configuration

### Data Persistence:
- **Config:** `./config/` - User settings and database
- **Logs:** `./logs/` - Application logs
- **Data:** `./data/` - Persistent data storage

### Environment Variables:
- `FLASK_ENV=production` - Production mode
- `PYTHONUNBUFFERED=1` - Real-time logs
- `WEB_MODE=true` - Web application mode

---

## 🆘 Troubleshooting

### Common Issues:

**❌ "Docker is not running"**
- Start Docker Desktop
- Wait for Docker to fully initialize
- Try again

**❌ "Port 5000 already in use"**
- Stop other applications using port 5000
- Or change port in `compose.yml`

**❌ "Application not responding"**
- Wait 2-3 minutes for full startup
- Check logs: `docker-compose logs -f`
- Restart: `docker-compose restart`

**❌ "API key validation failed"**
- Verify your Meraki API key is correct
- Check network connectivity
- Ensure corporate firewall allows Meraki API access

### Getting Help:
1. Check the logs: `docker-compose logs -f`
2. Restart the application: `docker-compose restart`
3. If issues persist, rebuild: `docker-compose down && docker-compose up --build -d`

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ Modern web interface replacing all CLI functionality
- ✅ No more terminal commands needed
- ✅ Team-friendly deployment process
- ✅ All enhanced network visualization features
- ✅ Secure, production-ready application

**Access your Cisco Meraki Web Management at: http://localhost:5000**

---

## 📞 Support

For technical support or questions:
1. Check this README first
2. Review application logs
3. Contact your system administrator

**Happy networking! 🌐**
