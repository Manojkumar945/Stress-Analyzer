# =============================================
# Real-Time Stress Detection using IoT ECG Data
# =============================================

import requests
import numpy as np
import pandas as pd
import time
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1️⃣ Load your trained Random Forest model
# (Assuming you already trained and saved it as 'stress_rf_model.pkl')
model = joblib.load("stress_rf_model.pkl")

# 2️⃣ Helper function to extract features from raw ECG values
def extract_features(ecg_values):
    """Compute statistical and signal-based features from ECG values."""
    ecg_array = np.array(ecg_values)
    
    mean_val = np.mean(ecg_array)
    std_val = np.std(ecg_array)
    peak_amp = np.max(ecg_array)
    
    # Simulated heart rate estimation (based on simple peaks)
    heart_rate = np.random.uniform(60, 110)  # Placeholder approximation
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

# 3️⃣ Real-time data collection and prediction loop
IOT_URL = "https://iotcloud22.in/4503_eeg/light.json"

print("🔄 Starting real-time ECG monitoring... Press Ctrl+C to stop.\n")

try:
    ecg_buffer = []
    start_time = time.time()

    while True:
        # Fetch ECG value from IoT endpoint
        response = requests.get(IOT_URL)
        if response.status_code == 200:
            data = response.json()
            # ecg_value = float(data["value1"])  # adjust key if needed
            ecg_value = 9
            ecg_buffer.append(ecg_value)

        # Every 10 seconds, analyze the last chunk
        if time.time() - start_time >= 10:
            if len(ecg_buffer) > 10:
                features = extract_features(ecg_buffer)
                prediction = model.predict(features)[0]
                print(f"🫀 Predicted Stress Level: {prediction}")
            else:
                print("⚠️ Not enough ECG samples yet.")
            
            # Reset buffer and timer
            ecg_buffer = []
            start_time = time.time()

        time.sleep(5)  # adjust sampling frequency as needed

except KeyboardInterrupt:
    print("\n🛑 Monitoring stopped by user.")
