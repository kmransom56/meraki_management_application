#!/usr/bin/env python3
"""
Persistent API Key Storage Utility
Securely stores and retrieves Meraki API keys to avoid repeated entry
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class APIKeyStorage:
    """Secure persistent storage for API keys"""
    
    def __init__(self, storage_file='api_keys.enc'):
        self.storage_file = storage_file
        self.key_file = '.key_salt'
        
    def _get_encryption_key(self):
        """Generate or retrieve encryption key"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(self.key_file, 'wb') as f:
                f.write(salt)
        
        # Use machine-specific info as password
        password = f"{os.environ.get('COMPUTERNAME', 'default')}{os.environ.get('USERNAME', 'user')}".encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    def save_api_key(self, api_key, key_name='meraki_default'):
        """Save API key securely"""
        try:
            fernet = self._get_encryption_key()
            
            # Load existing keys or create new storage
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'rb') as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted_data = fernet.decrypt(encrypted_data)
                        keys = json.loads(decrypted_data.decode())
                    else:
                        keys = {}
            else:
                keys = {}
            
            # Add/update the API key
            keys[key_name] = api_key
            
            # Encrypt and save
            encrypted_data = fernet.encrypt(json.dumps(keys).encode())
            with open(self.storage_file, 'wb') as f:
                f.write(encrypted_data)
            
            print(f"[SUCCESS] API key saved securely as '{key_name}'")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save API key: {e}")
            return False
    
    def load_api_key(self, key_name='meraki_default'):
        """Load API key securely"""
        try:
            if not os.path.exists(self.storage_file):
                return None
            
            fernet = self._get_encryption_key()
            
            with open(self.storage_file, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    return None
            
            decrypted_data = fernet.decrypt(encrypted_data)
            keys = json.loads(decrypted_data.decode())
            
            return keys.get(key_name)
            
        except Exception as e:
            print(f"[ERROR] Failed to load API key: {e}")
            return None
    
    def list_saved_keys(self):
        """List all saved API key names"""
        try:
            if not os.path.exists(self.storage_file):
                return []
            
            fernet = self._get_encryption_key()
            
            with open(self.storage_file, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    return []
            
            decrypted_data = fernet.decrypt(encrypted_data)
            keys = json.loads(decrypted_data.decode())
            
            return list(keys.keys())
            
        except Exception as e:
            print(f"[ERROR] Failed to list keys: {e}")
            return []
    
    def delete_api_key(self, key_name='meraki_default'):
        """Delete a saved API key"""
        try:
            if not os.path.exists(self.storage_file):
                return False
            
            fernet = self._get_encryption_key()
            
            with open(self.storage_file, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    return False
            
            decrypted_data = fernet.decrypt(encrypted_data)
            keys = json.loads(decrypted_data.decode())
            
            if key_name in keys:
                del keys[key_name]
                
                # Save updated keys
                encrypted_data = fernet.encrypt(json.dumps(keys).encode())
                with open(self.storage_file, 'wb') as f:
                    f.write(encrypted_data)
                
                print(f"[SUCCESS] API key '{key_name}' deleted")
                return True
            else:
                print(f"[INFO] API key '{key_name}' not found")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to delete API key: {e}")
            return False

# Convenience functions
def save_meraki_api_key(api_key):
    """Save Meraki API key with simple function call"""
    storage = APIKeyStorage()
    return storage.save_api_key(api_key, 'meraki_default')

def load_meraki_api_key():
    """Load Meraki API key with simple function call"""
    storage = APIKeyStorage()
    return storage.load_api_key('meraki_default')

def clear_saved_keys():
    """Clear all saved API keys"""
    storage = APIKeyStorage()
    keys = storage.list_saved_keys()
    for key in keys:
        storage.delete_api_key(key)
    print("[SUCCESS] All saved API keys cleared")

if __name__ == "__main__":
    # Command line interface for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python api_key_storage.py save <api_key>")
        print("  python api_key_storage.py load")
        print("  python api_key_storage.py list")
        print("  python api_key_storage.py clear")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    storage = APIKeyStorage()
    
    if command == 'save' and len(sys.argv) == 3:
        api_key = sys.argv[2]
        if storage.save_api_key(api_key):
            print("API key saved successfully!")
        else:
            print("Failed to save API key!")
    
    elif command == 'load':
        api_key = storage.load_api_key()
        if api_key:
            print(f"Loaded API key: {api_key[:10]}...{api_key[-4:]}")
        else:
            print("No API key found")
    
    elif command == 'list':
        keys = storage.list_saved_keys()
        if keys:
            print("Saved API keys:")
            for key in keys:
                print(f"  - {key}")
        else:
            print("No saved API keys found")
    
    elif command == 'clear':
        clear_saved_keys()
    
    else:
        print("Invalid command")
