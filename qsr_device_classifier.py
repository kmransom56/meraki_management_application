#!/usr/bin/env python3
"""
QSR (Quick Service Restaurant) Device Classification Module
Identifies restaurant-specific devices from Meraki and FortiGate networks
"""

import re
import logging

logger = logging.getLogger(__name__)

class QSRDeviceClassifier:
    """Classifies devices in QSR environments based on device names, MAC addresses, and network information"""
    
    def __init__(self):
        # QSR device patterns for identification
        self.device_patterns = {
            'digital_menu': {
                'names': [
                    r'menu.*board', r'digital.*menu', r'menu.*display', r'drive.*menu',
                    r'menu.*screen', r'outdoor.*menu', r'indoor.*menu', r'menu.*tv'
                ],
                'macs': [
                    r'^00:1B:21',  # Samsung displays
                    r'^00:26:5A',  # LG displays
                    r'^00:0C:E7',  # Sony displays
                ],
                'models': ['samsung', 'lg', 'sony', 'philips'],
                'icon': 'fas fa-tv',
                'color': '#FF6B35',  # Orange-red
                'category': 'Digital Signage'
            },
            'kitchen_display': {
                'names': [
                    r'kds', r'kitchen.*display', r'kitchen.*screen', r'prep.*screen',
                    r'expo.*screen', r'order.*display', r'kitchen.*monitor'
                ],
                'macs': [
                    r'^00:1B:21',  # Samsung
                    r'^00:26:5A',  # LG
                    r'^A4:C3:F0',  # Toast KDS
                ],
                'models': ['toast', 'revel', 'square', 'clover'],
                'icon': 'fas fa-utensils',
                'color': '#28A745',  # Green
                'category': 'Kitchen Systems'
            },
            'kitchen_timer': {
                'names': [
                    r'timer', r'kitchen.*timer', r'fry.*timer', r'cook.*timer',
                    r'prep.*timer', r'hold.*timer'
                ],
                'macs': [
                    r'^00:50:C2',  # Industrial timers
                    r'^00:1D:0F',  # Timer manufacturers
                ],
                'models': ['perfect', 'digi', 'taylor'],
                'icon': 'fas fa-stopwatch',
                'color': '#FFC107',  # Amber
                'category': 'Kitchen Equipment'
            },
            'drive_thru_timer': {
                'names': [
                    r'drive.*thru.*timer', r'dt.*timer', r'drive.*timer',
                    r'speed.*timer', r'service.*timer', r'lane.*timer'
                ],
                'macs': [
                    r'^00:50:C2',  # HME timers
                    r'^00:1A:79',  # Drive-thru equipment
                ],
                'models': ['hme', 'digi', 'perfect'],
                'icon': 'fas fa-car',
                'color': '#17A2B8',  # Cyan
                'category': 'Drive-Thru Systems'
            },
            'pos_register': {
                'names': [
                    r'pos', r'register', r'terminal', r'checkout', r'counter.*pos',
                    r'front.*counter', r'cashier', r'till'
                ],
                'macs': [
                    r'^00:1C:42',  # NCR
                    r'^00:50:F2',  # Microsoft Surface
                    r'^A4:C3:F0',  # Toast
                    r'^00:1B:63',  # Square
                ],
                'models': ['ncr', 'toast', 'square', 'clover', 'revel', 'micros'],
                'icon': 'fas fa-cash-register',
                'color': '#6F42C1',  # Purple
                'category': 'Point of Sale'
            },
            'pos_tablet': {
                'names': [
                    r'tablet', r'ipad', r'surface', r'mobile.*pos', r'handheld.*pos',
                    r'server.*tablet', r'order.*tablet'
                ],
                'macs': [
                    r'^00:50:F2',  # Microsoft Surface
                    r'^A4:C3:F0',  # Toast tablets
                    r'^00:1B:63',  # Square tablets
                    r'^28:CF:E9',  # Apple iPad
                    r'^3C:15:C2',  # Apple iPad
                ],
                'models': ['ipad', 'surface', 'android', 'toast', 'square'],
                'icon': 'fas fa-tablet-alt',
                'color': '#E83E8C',  # Pink
                'category': 'Mobile POS'
            },
            'wifi_access_point': {
                'names': [
                    r'ap', r'access.*point', r'wifi', r'wireless', r'mr\d+',
                    r'dining.*ap', r'kitchen.*ap', r'office.*ap'
                ],
                'macs': [
                    r'^88:15:44',  # Meraki
                    r'^00:18:0A',  # Meraki
                    r'^E0:55:3D',  # Meraki
                ],
                'models': ['mr', 'meraki'],
                'icon': 'fas fa-wifi',
                'color': '#FD7E14',  # Orange
                'category': 'Network Infrastructure'
            },
            'network_switch': {
                'names': [
                    r'switch', r'ms\d+', r'network.*switch', r'ethernet.*switch',
                    r'kitchen.*switch', r'dining.*switch', r'office.*switch'
                ],
                'macs': [
                    r'^88:15:44',  # Meraki
                    r'^00:18:0A',  # Meraki
                    r'^E0:55:3D',  # Meraki
                ],
                'models': ['ms', 'meraki'],
                'icon': 'fas fa-network-wired',
                'color': '#28A745',  # Green
                'category': 'Network Infrastructure'
            },
            'security_appliance': {
                'names': [
                    r'mx\d+', r'firewall', r'security.*appliance', r'router',
                    r'gateway', r'fortigate', r'fortinet'
                ],
                'macs': [
                    r'^88:15:44',  # Meraki
                    r'^00:18:0A',  # Meraki
                    r'^90:6C:AC',  # Fortinet
                    r'^00:09:0F',  # Fortinet
                ],
                'models': ['mx', 'meraki', 'fortigate', 'fortinet'],
                'icon': 'fas fa-shield-alt',
                'color': '#DC3545',  # Red
                'category': 'Security & Routing'
            },
            'security_camera': {
                'names': [
                    r'camera', r'cam', r'mv\d+', r'security.*cam', r'surveillance',
                    r'dining.*cam', r'kitchen.*cam', r'drive.*cam', r'parking.*cam'
                ],
                'macs': [
                    r'^88:15:44',  # Meraki
                    r'^00:18:0A',  # Meraki
                    r'^E0:55:3D',  # Meraki
                ],
                'models': ['mv', 'meraki'],
                'icon': 'fas fa-video',
                'color': '#6C757D',  # Gray
                'category': 'Security Systems'
            },
            'printer': {
                'names': [
                    r'printer', r'receipt.*printer', r'kitchen.*printer', r'label.*printer',
                    r'order.*printer', r'ticket.*printer'
                ],
                'macs': [
                    r'^00:07:61',  # Epson
                    r'^00:11:62',  # Star Micronics
                    r'^00:80:92',  # Zebra
                ],
                'models': ['epson', 'star', 'zebra', 'citizen'],
                'icon': 'fas fa-print',
                'color': '#495057',  # Dark gray
                'category': 'Peripherals'
            }
        }
    
    def classify_device(self, device_info):
        """
        Classify a device based on its information
        
        Args:
            device_info (dict): Device information containing name, mac, model, etc.
            
        Returns:
            dict: Classification result with device type, category, icon, color
        """
        device_name = (device_info.get('name') or '').lower()
        device_mac = (device_info.get('mac') or '').upper()
        device_model = (device_info.get('model') or '').lower()
        device_product = (device_info.get('productType') or '').lower()
        
        # Check each device pattern
        for device_type, patterns in self.device_patterns.items():
            score = 0
            
            # Check name patterns
            for name_pattern in patterns['names']:
                if re.search(name_pattern, device_name, re.IGNORECASE):
                    score += 3
                    break
            
            # Check MAC address patterns
            for mac_pattern in patterns['macs']:
                if re.search(mac_pattern, device_mac):
                    score += 2
                    break
            
            # Check model patterns
            for model_pattern in patterns['models']:
                if model_pattern in device_model or model_pattern in device_product:
                    score += 1
                    break
            
            # If we have a good match, return the classification
            if score >= 2:
                return {
                    'device_type': device_type,
                    'category': patterns['category'],
                    'icon': patterns['icon'],
                    'color': patterns['color'],
                    'confidence': min(score / 3.0, 1.0),
                    'display_name': self._get_display_name(device_type, device_name)
                }
        
        # Default classification for unknown devices
        return {
            'device_type': 'unknown',
            'category': 'Unknown Device',
            'icon': 'fas fa-question-circle',
            'color': '#9E9E9E',
            'confidence': 0.0,
            'display_name': device_name or 'Unknown Device'
        }
    
    def _get_display_name(self, device_type, original_name):
        """Generate a user-friendly display name for the device"""
        display_names = {
            'digital_menu': 'Digital Menu Board',
            'kitchen_display': 'Kitchen Display System',
            'kitchen_timer': 'Kitchen Timer',
            'drive_thru_timer': 'Drive-Thru Timer',
            'pos_register': 'POS Register',
            'pos_tablet': 'POS Tablet',
            'wifi_access_point': 'WiFi Access Point',
            'network_switch': 'Network Switch',
            'security_appliance': 'Security Appliance',
            'security_camera': 'Security Camera',
            'printer': 'Receipt Printer'
        }
        
        base_name = display_names.get(device_type, device_type.replace('_', ' ').title())
        
        # If original name has location info, include it
        location_patterns = [
            r'(kitchen|dining|drive|counter|office|back|front|prep|expo)',
            r'(lane\s*\d+|register\s*\d+|pos\s*\d+|station\s*\d+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, original_name, re.IGNORECASE)
            if match:
                location = match.group(1).title()
                return f"{base_name} ({location})"
        
        return base_name
    
    def get_qsr_statistics(self, classified_devices):
        """Generate QSR-specific statistics from classified devices"""
        stats = {
            'total_devices': len(classified_devices),
            'categories': {},
            'device_types': {},
            'qsr_health': {
                'pos_systems': 0,
                'kitchen_systems': 0,
                'digital_signage': 0,
                'network_infrastructure': 0
            }
        }
        
        for device in classified_devices:
            classification = device.get('classification', {})
            device_type = classification.get('device_type', 'unknown')
            category = classification.get('category', 'Unknown')
            
            # Count by device type
            stats['device_types'][device_type] = stats['device_types'].get(device_type, 0) + 1
            
            # Count by category
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # QSR health metrics
            if device_type in ['pos_register', 'pos_tablet']:
                stats['qsr_health']['pos_systems'] += 1
            elif device_type in ['kitchen_display', 'kitchen_timer']:
                stats['qsr_health']['kitchen_systems'] += 1
            elif device_type in ['digital_menu']:
                stats['qsr_health']['digital_signage'] += 1
            elif device_type in ['wifi_access_point', 'network_switch', 'security_appliance']:
                stats['qsr_health']['network_infrastructure'] += 1
        
        return stats
    
    def get_device_recommendations(self, classified_devices):
        """Provide recommendations for QSR network optimization"""
        recommendations = []
        stats = self.get_qsr_statistics(classified_devices)
        
        # Check for missing critical systems
        if stats['qsr_health']['pos_systems'] == 0:
            recommendations.append({
                'type': 'critical',
                'message': 'No POS systems detected. Ensure POS registers and tablets are connected.',
                'icon': 'fas fa-exclamation-triangle'
            })
        
        if stats['qsr_health']['kitchen_systems'] == 0:
            recommendations.append({
                'type': 'warning',
                'message': 'No kitchen display systems detected. Consider adding KDS for order management.',
                'icon': 'fas fa-utensils'
            })
        
        # Check network infrastructure
        if stats['qsr_health']['network_infrastructure'] < 2:
            recommendations.append({
                'type': 'info',
                'message': 'Limited network infrastructure detected. Ensure adequate WiFi coverage.',
                'icon': 'fas fa-wifi'
            })
        
        # Check for digital signage
        if stats['qsr_health']['digital_signage'] == 0:
            recommendations.append({
                'type': 'info',
                'message': 'No digital menu boards detected. Consider digital signage for menu updates.',
                'icon': 'fas fa-tv'
            })
        
        return recommendations
