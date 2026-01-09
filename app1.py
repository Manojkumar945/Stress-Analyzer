# from flask import Flask, jsonify, render_template, request
# import requests
# import pandas as pd
# import numpy as np
# import time
# import random
# import threading
# import joblib
# import webbrowser

# # ==========================================
# # CONFIGURATION
# # ==========================================
# IOT_URL = "https://iotcloud22.in/4503_eeg/light.json"
# MODEL_PATH = "stress_rf_model.pkl"

# model = joblib.load(MODEL_PATH)

# SONGS = {
#     "normal": [
#         "https://www.youtube.com/watch?v=2Vv-BfVoq4g",
#         "https://www.youtube.com/watch?v=wp43OdtAAkM",
#         "https://www.youtube.com/watch?v=JGwWNGJdvx8",
#         "https://www.youtube.com/watch?v=7NOSDKb0HlU",
#         "https://www.youtube.com/watch?v=60ItHLz5WEA"
#     ],
#     "stress": [
#         "https://www.youtube.com/watch?v=hTWKbfoikeg",
#         "https://www.youtube.com/watch?v=3mbBbFH9fAg",
#         "https://www.youtube.com/watch?v=5abamRO41fE",
#         "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",
#         "https://www.youtube.com/watch?v=l482T0yNkeo"
#     ],
#     "anxiety": [
#         "https://www.youtube.com/watch?v=WIF4_Sm-rgQ",
#         "https://www.youtube.com/watch?v=1WLWmDZ3Q6I",
#         "https://www.youtube.com/watch?v=3JWTaaS7LdU",
#         "https://www.youtube.com/watch?v=3AtDnEC4zak",
#         "https://www.youtube.com/watch?v=3YxaaGgTQYM"
#     ]
# }

# app = Flask(__name__)

# # ==========================================
# # FEATURE EXTRACTION
# # ==========================================
# def extract_features(ecg_values):
#     ecg_array = np.array(ecg_values)
#     mean_val = np.mean(ecg_array)
#     std_val = np.std(ecg_array)
#     peak_amp = np.max(ecg_array)
#     heart_rate = np.random.uniform(60, 110)
#     rr_var = np.var(np.diff(ecg_array))
#     entropy = -np.sum((ecg_array/1024) * np.log2((ecg_array/1024) + 1e-9))
    
#     return pd.DataFrame([{
#         "mean_val": mean_val,
#         "std_val": std_val,
#         "peak_amp": peak_amp,
#         "heart_rate": heart_rate,
#         "rr_var": rr_var,
#         "entropy": entropy
#     }]), {
#         "mean_val": round(mean_val, 4),
#         "std_val": round(std_val, 4),
#         "peak_amp": round(peak_amp, 4),
#         "heart_rate": round(heart_rate, 4),
#         "rr_var": round(rr_var, 4),
#         "entropy": round(entropy, 4)
#     }

# # ==========================================
# # GLOBALS
# # ==========================================
# last_label = None
# repeat_count = 0
# latest_prediction = "N/A"
# current_song = "None"
# ecg_buffer = []
# monitoring_active = False
# current_features = {
#     "mean_val": 0,
#     "std_val": 0,
#     "peak_amp": 0,
#     "heart_rate": 0,
#     "rr_var": 0,
#     "entropy": 0
# }

# # ==========================================
# # BACKGROUND THREAD
# # ==========================================
# def live_monitoring():
#     global last_label, repeat_count, latest_prediction, ecg_buffer, current_song, monitoring_active, current_features
#     start_time = time.time()
#     while True:
#         if monitoring_active:
#             try:
#                 response = requests.get(IOT_URL, timeout=3)
#                 if response.status_code == 200:
#                     data = response.json()
#                     print(f'ecg value-----> {data}')
#                     ecg_value = int(data["value1"])
#                     # ecg_value = 457 + random.uniform(-10, 10)  # Adding some variation for demo
#                     ecg_buffer.append(ecg_value)

#                 if time.time() - start_time >= 10 and len(ecg_buffer) > 10:
#                     features_df, features_dict = extract_features(ecg_buffer)
#                     current_features = features_dict
#                     label = model.predict(features_df)[0]
#                     latest_prediction = label
                    

#                     if label == last_label:
#                         repeat_count += 1
#                     else:
#                         repeat_count = 1
#                         last_label = label

#                     if repeat_count >= 2:
#                         song_url = random.choice(SONGS[label])
#                         current_song = song_url
#                         webbrowser.open(song_url)
#                         time.sleep(60)
#                         repeat_count = 0

#                     ecg_buffer = []
#                     start_time = time.time()

#                 time.sleep(2)

#             except Exception as e:
#                 print("⚠️ Error:", e)
#                 time.sleep(2)
#         else:
#             time.sleep(1)

# thread = threading.Thread(target=live_monitoring, daemon=True)
# thread.start()

# # ==========================================
# # API ENDPOINTS
# # ==========================================
# @app.route("/home")
# def home():
#     return jsonify({
#         "status": "running",
#         "latest_prediction": latest_prediction,
#         "current_song": current_song,
#         "monitoring_active": monitoring_active,
#         "features": current_features
#     })

# @app.route("/start_monitoring", methods=['POST'])
# def start_monitoring():
#     global monitoring_active, ecg_buffer, latest_prediction, current_song
#     monitoring_active = True
#     ecg_buffer = []
#     latest_prediction = "Monitoring started..."
#     current_song = "None"
#     return jsonify({"status": "Monitoring started"})

# @app.route("/stop_monitoring", methods=['POST'])
# def stop_monitoring():
#     global monitoring_active, latest_prediction
#     monitoring_active = False
#     latest_prediction = "Monitoring stopped"
#     return jsonify({"status": "Monitoring stopped"})

# @app.route("/get_status")
# def get_status():
#     return jsonify({
#         "latest_prediction": latest_prediction,
#         "current_song": current_song,
#         "monitoring_active": monitoring_active,
#         "features": current_features
#     })

# # Dashboard route
# @app.route("/")
# def dashboard():
#     return render_template('index.html')

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)



from flask import Flask, jsonify, render_template, request
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
    
    # Convert numpy types to native Python types for JSON serialization
    features_df = pd.DataFrame([{
        "mean_val": float(mean_val),
        "std_val": float(std_val),
        "peak_amp": float(peak_amp),
        "heart_rate": float(heart_rate),
        "rr_var": float(rr_var),
        "entropy": float(entropy)
    }])
    
    features_dict = {
        "mean_val": float(mean_val),
        "std_val": float(std_val),
        "peak_amp": float(peak_amp),
        "heart_rate": float(heart_rate),
        "rr_var": float(rr_var),
        "entropy": float(entropy)
    }
    
    return features_df, features_dict

# ==========================================
# GLOBALS
# ==========================================
last_label = None
repeat_count = 0
latest_prediction = "N/A"
current_song = "None"
ecg_buffer = []
monitoring_active = False
current_features = {
    "mean_val": 0.0,
    "std_val": 0.0,
    "peak_amp": 0.0,
    "heart_rate": 0.0,
    "rr_var": 0.0,
    "entropy": 0.0
}

# ==========================================
# BACKGROUND THREAD
# ==========================================
def live_monitoring():
    global last_label, repeat_count, latest_prediction, ecg_buffer, current_song, monitoring_active, current_features
    start_time = time.time()
    while True:
        if monitoring_active:
            try:
                response = requests.get(IOT_URL, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    print(f'ecg value-----> {data}')
                    # ecg_value = float(data["value1"])
                    ecg_value = 457 + random.uniform(-10, 10)  # Adding some variation for demo
                    ecg_buffer.append(ecg_value)

                if time.time() - start_time >= 10 and len(ecg_buffer) > 10:
                    features_df, features_dict = extract_features(ecg_buffer)
                    current_features = features_dict
                    label = model.predict(features_df)[0]
                    
                    # Convert numpy string/object to native Python string
                    if hasattr(label, 'item'):  # For numpy types
                        label = label.item()
                    latest_prediction = str(label)

                    if label == last_label:
                        repeat_count += 1
                    else:
                        repeat_count = 1
                        last_label = label

                    if repeat_count >= 2:
                        song_url = random.choice(SONGS.get(label, SONGS["normal"]))
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
        else:
            time.sleep(1)

thread = threading.Thread(target=live_monitoring, daemon=True)
thread.start()

# ==========================================
# HELPER FUNCTION TO CONVERT NUMPY TYPES
# ==========================================
def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.str_, np.string_)):
        return str(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

# ==========================================
# API ENDPOINTS
# ==========================================
@app.route("/home")
def home():
    return jsonify({
        "status": "running",
        "latest_prediction": latest_prediction,
        "current_song": current_song,
        "monitoring_active": monitoring_active,
        "features": convert_numpy_types(current_features)
    })

@app.route("/start_monitoring", methods=['POST'])
def start_monitoring():
    global monitoring_active, ecg_buffer, latest_prediction, current_song
    monitoring_active = True
    ecg_buffer = []
    latest_prediction = "Monitoring started..."
    current_song = "None"
    return jsonify({"status": "Monitoring started"})

@app.route("/stop_monitoring", methods=['POST'])
def stop_monitoring():
    global monitoring_active, latest_prediction
    monitoring_active = False
    latest_prediction = "Monitoring stopped"
    return jsonify({"status": "Monitoring stopped"})

@app.route("/get_status")
def get_status():
    # Convert all numpy types to native Python types before jsonify
    status_data = {
        "latest_prediction": latest_prediction,
        "current_song": current_song,
        "monitoring_active": monitoring_active,
        "features": convert_numpy_types(current_features)
    }
    return jsonify(status_data)

# Dashboard route
@app.route("/")
def dashboard():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
