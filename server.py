from waitress import serve
from app4 import app
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    host_ip = get_ip()
    print("="*50)
    print(f" PRODUCTION SERVER STARTED")
    print("="*50)
    print(f" * Local Access:   http://127.0.0.1:5000")
    print(f" * Network Access: http://{host_ip}:5000")
    print("="*50)
    print("LOGS:")
    serve(app, host='0.0.0.0', port=5000, threads=6)
