import requests

try:
    response = requests.get("https://iotcloud22.in/4503_eeg/index.php")
    with open("source.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved to source.html")
except Exception as e:
    print(e)
