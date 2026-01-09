import os
import sys
import time
from pyngrok import ngrok, conf

# ==============================================================================
# INSTRUCTIONS FOR PERMANENT LINK
# ==============================================================================
# 1. Sign up for a free account at https://dashboard.ngrok.com/signup
# 2. Get your Authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
# 3. Stop this script.
# 4. Run command in terminal: ngrok config add-authtoken YOUR_TOKEN
# 5. Claim a free static domain here: https://dashboard.ngrok.com/cloud-edge/domains
# 6. Edit the line below:
#    public_url = ngrok.connect(5000, domain="your-static-domain.ngrok-free.app").public_url
# ==============================================================================

def start_public_tunnel():
    print("Initializing Public Tunnel...")
    
    # Configure ngrok to be silent
    conf.get_default().monitor_thread = False

    try:
        # Check if a tunnel is already open (in case of restart)
        tunnels = ngrok.get_tunnels()
        if not tunnels:
            # Start a tunnel to port 5000
            # If you have a static domain, create it like this:
            # url = ngrok.connect(5000, domain="your-domain.ngrok-free.app").public_url
            url = ngrok.connect(5000).public_url
        else:
            url = tunnels[0].public_url

        print("\n" + "="*60)
        print("🌍  YOUR PUBLIC ACCESS LINK  🌍")
        print("="*60)
        print(f"\n👉  {url}  👈\n")
        print("="*60)
        print("Share this link with anyone to access your project.")
        print("NOTE: Unless you configured a static domain, this link changes every time you restart.")
        print("Press Ctrl+C to stop the tunnel.")
        
        # Keep the script alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping Tunnel...")
        ngrok.kill()
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("Ensure 'server.py' is running in another terminal!")

if __name__ == "__main__":
    start_public_tunnel()
