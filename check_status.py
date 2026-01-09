import requests
import time
import json

BASE_URL = 'http://localhost:5000'
LOGIN_URL = f'{BASE_URL}/login'
STATUS_URL = f'{BASE_URL}/get_status'

def check_status():
    session = requests.Session()
    
    # Login
    print("Logging in...")
    resp = session.post(LOGIN_URL, data={'email': 'admin@example.com', 'password': 'password123'})
    if resp.url != f'{BASE_URL}/dashboard':
        print("Login failed or redirected unexpectedly.")
        return

    print("Checking status...")
    for i in range(5):
        try:
            resp = session.get(STATUS_URL)
            data = resp.json()
            print(f"Status: Active={data.get('monitoring_active')}, Pred={data.get('latest_prediction')}, Features={data.get('features', {}).get('mean_val')}")
        except Exception as e:
            print(f"Error: {e}")
            print(f"Response content: {resp.text[:200]}")
        time.sleep(1)

if __name__ == "__main__":
    check_status()
