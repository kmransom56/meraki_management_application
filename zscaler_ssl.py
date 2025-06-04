import os

def set_zscaler_ca():
    ca_path = os.path.expanduser("~/zscaler_cacert.pem")  # or your preferred path
    if os.path.exists(ca_path):
        os.environ["REQUESTS_CA_BUNDLE"] = ca_path
        os.environ["SSL_CERT_FILE"] = ca_path
        print(f"Zscaler CA certificate set to {ca_path}")
    else:
        print(f"Zscaler CA certificate not found at {ca_path}.")    

if __name__ == "__main__":
    set_zscaler_ca()

#import zscaler_ssl
#zscaler_ssl.set_zscaler_ca()
#
import os
ca_path = "C:/path/to/meraki.pem"
if os.path.exists(ca_path):
    os.environ["REQUESTS_CA_BUNDLE"] = ca_path
    os.environ["SSL_CERT_FILE"] = ca_path
    print(f"Zscaler CA certificate set to {ca_path}")
else:
    print(f"Zscaler CA certificate not found at {ca_path}.")

#Get-Content C:\path\to\zscaler_root_ca1.crt, C:\path\to\zscaler_root_ca2.crt | Set-Content C:\Users\keith.ransom\zscaler_cacert.pem