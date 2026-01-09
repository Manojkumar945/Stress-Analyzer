import requests
try:
    resp = requests.get("https://iotcloud22.in/4503_eeg/light.json")
    print(f"Status: {resp.status_code}")
    print(f"Content: {resp.text}")
except Exception as e:
    print(e)
