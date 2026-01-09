from flask import Flask, jsonify, render_template
import requests
import pandas as pd
import numpy as np
import time
import random
import threading
import joblib
import webbrowser

# ==========================================
# CONFIGURATION
# ==========================================
IOT_URL = "https://iotcloud22.in/4503_eeg/light.json"
MODEL_PATH = "stress_rf_model.pkl"

model = joblib.load(MODEL_PATH)

SONGS = {
    "normal": [
        "https://www.youtube.com/watch?v=2Vv-BfVoq4g",
        "https://www.youtube.com/watch?v=wp43OdtAAkM",
        "https://www.youtube.com/watch?v=JGwWNGJdvx8",
        "https://www.youtube.com/watch?v=7NOSDKb0HlU",
        "https://www.youtube.com/watch?v=60ItHLz5WEA"
    ],
    "stress": [
        "https://www.youtube.com/watch?v=hTWKbfoikeg",
        "https://www.youtube.com/watch?v=3mbBbFH9fAg",
        "https://www.youtube.com/watch?v=5abamRO41fE",
        "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",
        "https://www.youtube.com/watch?v=l482T0yNkeo"
    ],
    "anxiety": [
        "https://www.youtube.com/watch?v=WIF4_Sm-rgQ",
        "https://www.youtube.com/watch?v=1WLWmDZ3Q6I",
        "https://www.youtube.com/watch?v=3JWTaaS7LdU",
        "https://www.youtube.com/watch?v=3AtDnEC4zak",
        "https://www.youtube.com/watch?v=3YxaaGgTQYM"
    ]
}


app = Flask(__name__)

# ==========================================
# FEATURE EXTRACTION
# ==========================================
def extract_features(ecg_values):
    ecg_array = np.array(ecg_values)
    mean_val = np.mean(ecg_array)
    std_val = np.std(ecg_array)
    peak_amp = np.max(ecg_array)
    heart_rate = np.random.uniform(60, 110)
    rr_var = np.var(np.diff(ecg_array))
    entropy = -np.sum((ecg_array/1024) * np.log2((ecg_array/1024) + 1e-9))
    return pd.DataFrame([{
        "mean_val": mean_val,
        "std_val": std_val,
        "peak_amp": peak_amp,
        "heart_rate": heart_rate,
        "rr_var": rr_var,
        "entropy": entropy
    }])

# ==========================================
# GLOBALS
# ==========================================
last_label = None
repeat_count = 0
latest_prediction = "N/A"
current_song = "None"
ecg_buffer = []

# ==========================================
# BACKGROUND THREAD
# ==========================================
def live_monitoring():
    global last_label, repeat_count, latest_prediction, ecg_buffer, current_song
    start_time = time.time()
    while True:
        try:
            response = requests.get(IOT_URL, timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f'ecg value-----> {data}')
                # ecg_value = float(data["value1"])
                ecg_value = 457
                ecg_buffer.append(ecg_value)

            if time.time() - start_time >= 10 and len(ecg_buffer) > 10:
                features = extract_features(ecg_buffer)
                label = model.predict(features)[0]
                latest_prediction = label

                if label == last_label:
                    repeat_count += 1
                else:
                    repeat_count = 1
                    last_label = label

                if repeat_count >= 2:
                    song_url = random.choice(SONGS[label])
                    current_song = song_url
                    webbrowser.open(song_url)
                    time.sleep(60)
                    repeat_count = 0

                ecg_buffer = []
                start_time = time.time()

            time.sleep(2)

        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(2)

thread = threading.Thread(target=live_monitoring, daemon=True)
thread.start()

# ==========================================
# API ENDPOINTS
# ==========================================
@app.route("/home")
def home():
    return jsonify({
        "status": "running",
        "latest_prediction": latest_prediction,
        "current_song": current_song
    })

# Dashboard route
@app.route("/")
def dashboard():
    return render_template('index1.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
