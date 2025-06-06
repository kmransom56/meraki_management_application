# Centralizing Zscaler (or Custom CA) SSL Certificate Handling for Python Projects

When working behind a Zscaler proxy or with any custom CA, you may encounter SSL errors in Python applications that make HTTPS requests. The best, most reusable way to handle this is to centralize your CA bundle configuration. This guide explains how to do this for both Windows and WSL environments, and how to make your Python code portable and robust.

---

## 1. Create a Central CA Bundle

If you have multiple certificate files (e.g., `zscaler_root_ca1.crt`, `zscaler_root_ca2.crt`), concatenate them into a single `.pem` file:

**PowerShell Example:**
```powershell
Get-Content C:\path\to\zscaler_root_ca1.crt, C:\path\to\zscaler_root_ca2.crt | Set-Content C:\Users\<your-username>\zscaler_cacert.pem
```

Or, append certificates:
```powershell
Get-Content C:\path\to\zscaler_root_ca1.crt | Add-Content C:\Users\<your-username>\zscaler_cacert.pem
Get-Content C:\path\to\zscaler_root_ca2.crt | Add-Content C:\Users\<your-username>\zscaler_cacert.pem
```

---

## 2. Install the Certificate System-Wide

### Windows
- Double-click the `.pem` or `.crt` file.
- Click **Install Certificate...**
- Choose **Local Machine** (admin rights required).
- Select **Place all certificates in the following store** → **Trusted Root Certification Authorities**.
- Complete the wizard.

**Or, use PowerShell:**
```powershell
Import-Certificate -FilePath "C:\Users\<your-username>\zscaler_cacert.pem" -CertStoreLocation Cert:\LocalMachine\Root
```

### WSL (Ubuntu/Debian)
```bash
sudo cp /mnt/c/Users/<your-username>/zscaler_cacert.pem /usr/local/share/ca-certificates/zscaler_cacert.crt
sudo update-ca-certificates
```

---

## 3. Centralize CA Bundle Usage in Python

### Option A: Set Environment Variable Globally
Set `REQUESTS_CA_BUNDLE` and/or `SSL_CERT_FILE` in your user or system environment variables:
- Variable: `REQUESTS_CA_BUNDLE`
- Value: `C:\Users\<your-username>\zscaler_cacert.pem`

This will make all Python code using `requests` (and many other libraries) use your Zscaler CA, with no code changes needed.

### Option B: Use a Python Utility Module
Create a module (e.g., `zscaler_ssl.py`):
```python
import os

def set_zscaler_ca():
    ca_path = os.path.expanduser("~/zscaler_cacert.pem")
    if os.path.exists(ca_path):
        os.environ["REQUESTS_CA_BUNDLE"] = ca_path
        os.environ["SSL_CERT_FILE"] = ca_path
        print(f"Zscaler CA certificate set to {ca_path}")
    else:
        print(f"Zscaler CA certificate not found at {ca_path}.")
```
Then, in your main script:
```python
import zscaler_ssl
zscaler_ssl.set_zscaler_ca()
```

### Option C: Patch at the Start of Your Main Script
```python
import os
ca_path = "C:/Users/<your-username>/zscaler_cacert.pem"
if os.path.exists(ca_path):
    os.environ["REQUESTS_CA_BUNDLE"] = ca_path
    os.environ["SSL_CERT_FILE"] = ca_path
```

### Option D: Use a Virtual Environment Activation Script
Add the environment variable export to your `activate` script or a `.env` file (if using tools like `python-dotenv`).

---

## 4. Verification

- **Windows:**
  - Open `certmgr.msc`, expand "Trusted Root Certification Authorities" → "Certificates", and look for your cert.
- **WSL:**
  - Run `openssl s_client -connect example.com:443 -CAfile /etc/ssl/certs/ca-certificates.crt` and check for verification success.

---

## 5. Summary
- Import the cert into Windows "Trusted Root Certification Authorities".
- Copy and update CA certs in WSL using `update-ca-certificates`.
- Set the environment variable globally, or use a utility module for per-project configuration.

This approach will eliminate SSL errors with Zscaler or other custom CAs in all your Python API projects.
