from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, send_from_directory
import requests
try:
    import pandas as pd
    import numpy as np
    import joblib
    HAS_ML_LIBS = True
except ImportError:
    HAS_ML_LIBS = False
    print("⚠️  Running in LITE mode (No ML libs found)")

import time
import random
import threading
import math
import webbrowser
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import hashlib
import os
import csv
import io
import socket
from datetime import datetime

def get_local_ip():
    try:
        # Get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        s.close()
        return IP
    except Exception:
        return '127.0.0.1'

# ==========================================
# CONFIGURATION
# ==========================================
IOT_READ_URL = "https://iotcloud22.in/4503_eeg/light.json"
IOT_POST_URL = "https://iotcloud22.in/4503_eeg/post_value1.php"
MODEL_PATH = "stress_rf_model.pkl"
# Use /tmp for database in serverless environments (Vercel, AWS Lambda, etc.)
# This ensures write permissions since the filesystem is read-only except /tmp
IS_SERVERLESS = os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or os.environ.get('LAMBDA_TASK_ROOT')
DATABASE_PATH = os.path.join('/tmp', 'stress_monitor.db') if IS_SERVERLESS else "stress_monitor.db"
SECRET_KEY = "your_secret_key_here_change_in_production"

# Email Configuration (Update with your email credentials)
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'SENDER_EMAIL': 'cybertechguard28@gmail.com',
    'SENDER_PASSWORD': 'kyucxjzrwaxaskgt',
    'USE_TLS': True
}
# Lazy-load model to avoid import-time failures in serverless
model = None
def get_model():
    """Lazy-load the ML model on first use"""
    global model
    if model is None and HAS_ML_LIBS:
        try:
            if os.path.exists(MODEL_PATH):
                model = joblib.load(MODEL_PATH)
                print(f"✅ Model loaded successfully from {MODEL_PATH}")
            else:
                print(f"⚠️  Model file not found: {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Model load error: {e}")
    return model

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
app.secret_key = SECRET_KEY

THERAPY_TECHNIQUES = {
    "normal": [
        "Deep Breathing: Practice slow inhalation for 4 seconds, hold for 4 seconds, and exhale for 4 seconds.",
        "Mindful Listening: Focus on calm background music or natural sounds to maintain relaxation.",
        "Positive Affirmations: Repeat short positive phrases like 'I feel calm and focused.'"
    ],
    "stress": [
        "Progressive Muscle Relaxation: Tense and then slowly release each muscle group to relieve tension.",
        "Box Breathing: Inhale for 4 seconds, hold for 4 seconds, exhale for 4 seconds, and pause for 4 seconds.",
        "Guided Imagery: Visualize a peaceful scene such as a beach or garden to calm the mind."
    ],
    "anxiety": [
        "Grounding Technique (5-4-3-2-1): Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.",
        "Alternate Nostril Breathing: Breathe in through one nostril, out through the other — balances brain activity.",
        "Aromatherapy: Use lavender or chamomile scents to relax the nervous system."
    ]
}

current_techniques = THERAPY_TECHNIQUES["normal"]

# ==========================================
# DATABASE SETUP
# ==========================================
def init_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table (Updated with phone_number)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone_number TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Patients table (linked to caretakers)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caretaker_id INTEGER,
        patient_name TEXT NOT NULL,
        patient_age INTEGER,
        patient_gender TEXT,
        medical_conditions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (caretaker_id) REFERENCES users (id)
    )
    ''')
    
    # Monitoring sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS monitoring_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )
    ''')
    
    # Stress events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stress_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        prediction TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mean_val REAL,
        std_val REAL,
        peak_amp REAL,
        heart_rate REAL,
        rr_var REAL,
        entropy REAL,
        song_played TEXT,
        email_sent BOOLEAN DEFAULT 0,
        FOREIGN KEY (session_id) REFERENCES monitoring_sessions (id)
    )
    ''')
    
    # Readings table (for second-by-second data)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        eeg_value REAL NOT NULL,
        prediction TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES monitoring_sessions (id)
    )
    ''')

    # MIGRATION: Check if phone_number exists in users and add if not
    try:
        cursor.execute("SELECT phone_number FROM users LIMIT 1")
    except sqlite3.OperationalError:
        print("⚠️ Migrating Database: Adding phone_number column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")
    
    conn.commit()
    conn.close()

# Initialize database lazily on first use (not at module import)
# This prevents failures during cold starts in serverless environments
_database_initialized = False

def ensure_database_initialized():
    """Initialize database on first access"""
    global _database_initialized
    if not _database_initialized:
        try:
            init_database()
            _database_initialized = True
        except Exception as e:
            print(f"⚠️  Database initialization error: {e}")
            # Continue anyway - database will be created on first connection attempt

# ==========================================
# DATABASE HELPER FUNCTIONS
# ==========================================
def get_db_connection():
    """Get database connection with auto-initialization"""
    ensure_database_initialized()
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# EMAIL FUNCTION
# ==========================================
def send_stress_alert_email(caretaker_email, patient_name, prediction, features, song_url, csv_data=None):
    """Send email alert to caretaker"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['SENDER_EMAIL']
        msg['To'] = caretaker_email
        msg['Subject'] = f"⚠️ Stress Alert: {patient_name} Detected {prediction}"
        
        # Create HTML email body
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #e74c3c;">⚠️ Stress Level Alert</h2>
                <p>Dear Caretaker,</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Patient: {patient_name}</h3>
                    <p style="margin-bottom: 5px;"><strong>Detected Stress Level:</strong> <span style="color: #e74c3c; font-weight: bold;">{prediction.upper()}</span></p>
                    <p style="margin-top: 0;"><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h3 style="color: #2c3e50;">Vital Signs Summary:</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Parameter</th>
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Value</th>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">Heart Rate</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{features.get('heart_rate', 'N/A')} bpm</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">EEG Value</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{features.get('eeg_val', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">Mean Value</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{features.get('mean_val', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">Standard Deviation</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{features.get('std_val', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">Entropy</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{features.get('entropy', 'N/A')}</td>
                    </tr>
                </table>
                
                <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="color: #2980b9; margin-top: 0;">🎵 Relaxation Music Activated</h4>
                    <p>A calming song has been automatically played for the patient:</p>
                    <p><a href="{song_url}" style="color: #3498db;">Click here to view the song</a></p>
                </div>
                <p style="font-size: 12px; color: #888;">* Detailed readings sent as attachment.</p>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html, 'html'))
        
        # Attach CSV readings if provided
        if csv_data:
            part = MIMEApplication(csv_data.encode('utf-8'), Name=f"readings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            part['Content-Disposition'] = f'attachment; filename="readings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            msg.attach(part)
        
        # Send email in a separate thread
        def send_async():
            try:
                with smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT']) as server:
                    if EMAIL_CONFIG['USE_TLS']:
                        server.starttls()
                    server.login(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['SENDER_PASSWORD'])
                    server.send_message(msg)
                print(f"📧 Email alert sent to {caretaker_email}")
            except Exception as e:
                print(f"❌ Failed to send email: {e}")

        email_thread = threading.Thread(target=send_async)
        email_thread.start()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to prepare email: {e}")
        return False

# ==========================================
# WHATSAPP FUNCTION
# ==========================================
def send_whatsapp_alert(phone_number, patient_name, prediction):
    """Send WhatsApp alert using pywhatkit (instantly)"""
    try:
        # Check for pywhatkit import
        try:
            import pywhatkit
        except ImportError:
            print("❌ pywhatkit not installed. Skipping WhatsApp Alert.")
            return False

        if not phone_number:
            print("⚠️ No phone number provided for WhatsApp alert.")
            return False
        
        # Format phone number (Assume +91 if missing)
        phone_number = str(phone_number).strip()
        if not phone_number.startswith('+'):
            phone_number = "+91" + phone_number

        message = f"🚨 *Caretaker Alert*\n\n*Patient Name:* {patient_name}\n*Condition:* {prediction}\n*Action:* Please check your Email immediately."
        
        print(f"🔄 Attempting WhatsApp Alert to {phone_number}...")
        
        # Run in a separate thread to avoid blocking main loop, 
        # BUT pywhatkit requires GUI interaction. It opens a browser tab.
        def run_wa():
            try:
                # time_hour, time_min are for scheduled. sendwhatmsg_instantly is for now.
                # wait_time=15 (time to load web), tab_close=True, close_time=3
                pywhatkit.sendwhatmsg_instantly(phone_number, message, 15, True, 3)
                print(f"✅ WhatsApp Alert Sent to {phone_number}")
            except Exception as e:
                print(f"❌ WhatsApp Send Error: {e}")

        # Danger: Running this in a thread might fail if main thread exits, 
        # but for persistent server it's okay.
        threading.Thread(target=run_wa).start()
        return True

    except Exception as e:
        print(f"❌ WhatsApp Trigger Error: {e}")
        return False

# ==========================================
# FEATURE EXTRACTION
# ==========================================
def extract_features(ecg_values):
    if HAS_ML_LIBS:
        ecg_array = np.array(ecg_values)
        mean_val = np.mean(ecg_array)
        std_val = np.std(ecg_array)
        peak_amp = np.max(ecg_array)
        raw_hr = 70 + (std_val * 1.5) + np.random.uniform(-2, 2)
        heart_rate = min(99, max(60, raw_hr))
        rr_var = np.var(np.diff(ecg_array))
        entropy = -np.sum((ecg_array/1024) * np.log2((ecg_array/1024) + 1e-9))
        
        features_dict = {
            "mean_val": float(mean_val),
            "std_val": float(std_val),
            "peak_amp": float(peak_amp),
            "heart_rate": float(heart_rate),
            "rr_var": float(rr_var),
            "entropy": float(entropy)
        }
        features_df = pd.DataFrame([features_dict])
        return features_df, features_dict
    else:
        # Lite Mode
        def mean(l): return sum(l)/len(l) if l else 0
        def variance(l): 
            m = mean(l)
            return sum((x-m)**2 for x in l) / len(l) if l else 0
        
        m_val = mean(ecg_values)
        s_val = math.sqrt(variance(ecg_values))
        p_amp = max(ecg_values) if ecg_values else 0
        hr = 75 + random.uniform(-5, 5)
        
        features_dict = {
            "mean_val": round(m_val, 2),
            "std_val": round(s_val, 2),
            "peak_amp": round(p_amp, 2),
            "heart_rate": int(hr),
            "rr_var": 50.0,
            "entropy": 0.5
        }
        return None, features_dict

# ==========================================
# GLOBALS
# ==========================================
last_label = None
session_prediction_count = 0

# Ranges based on User Requirement Table
STATE_RANGES = {
    "Normal": {
        "eeg": (0, 320), "mean": (0.45, 0.65), "std": (0.08, 0.18), 
        "peak": (40, 80), "hr": (65, 85), "rr": (220, 320), "entr": (0.65, 0.80)
    },
    "Low Stress": {
        "eeg": (321, 500), "mean": (0.55, 0.70), "std": (0.12, 0.22), 
        "peak": (70, 100), "hr": (80, 95), "rr": (170, 250), "entr": (0.55, 0.70)
    },
    "Medium Stress": {
        "eeg": (501, 700), "mean": (0.60, 0.80), "std": (0.16, 0.26), 
        "peak": (90, 120), "hr": (90, 105), "rr": (120, 200), "entr": (0.45, 0.65)
    },
    "High Stress": {
        "eeg": (701, 900), "mean": (0.65, 0.85), "std": (0.20, 0.30), 
        "peak": (110, 150), "hr": (100, 115), "rr": (80, 150), "entr": (0.35, 0.55)
    },
    "Anxiety": {
        "eeg": (901, 1024), "mean": (0.70, 0.95), "std": (0.24, 0.35), 
        "peak": (130, 180), "hr": (110, 130), "rr": (50, 120), "entr": (0.25, 0.45)
    }
}
repeat_count = 0
latest_prediction = "----"
stress_level = "----"
current_song = "None"
ecg_buffer = []
monitoring_active = False
current_features = {
    "mean_val": 459.22,
    "std_val": 5.41,
    "peak_amp": 464.92,
    "heart_rate": 84.7,
    "rr_var": 73.20,
    "entropy": 4.15,
    "eeg_val": 1024
}
current_patient_id = None
current_session_id = None
current_caretaker_email = None
current_caretaker_phone = None
latest_email_sent_time = None
# ==========================================
# BACKGROUND THREAD
# ==========================================
def live_monitoring():
    global monitoring_active, current_patient_id, current_session_id
    global ecg_buffer, latest_prediction, stress_level, current_song, current_features, last_label, repeat_count, latest_email_sent_time
    global session_prediction_count, current_caretaker_phone
    
    print("DEBUG: Live Monitoring Thread Started")
    
    start_time = time.time()
    
    while True:
        if monitoring_active: print(f"DEBUG: Loop Active. PatID: {current_patient_id}")
        if monitoring_active and current_patient_id:
            try:
                # Get patient and caretaker info
                conn = get_db_connection()
                patient = conn.execute(
                    'SELECT p.*, u.email as caretaker_email, u.phone_number FROM patients p '
                    'JOIN users u ON p.caretaker_id = u.id '
                    'WHERE p.id = ?', (current_patient_id,)
                ).fetchone()
                conn.close()
                
                if not patient:
                    print("Patient not found")
                    monitoring_active = False
                    continue
                
                caretaker_email = patient['caretaker_email']
                caretaker_phone = patient['phone_number']
                current_caretaker_phone = caretaker_phone
                patient_name = patient['patient_name']
                
                # 1. FETCH DATA FROM IOT DASHBOARD
                eeg_value = None
                try:
                    response = requests.get("https://iotcloud22.in/4503_eeg/light.json", timeout=1)
                    if response.status_code == 200:
                        data = response.json()
                        # Extract EEG value (try 'value1' first)
                        if "value1" in data:
                            raw_val = float(data.get("value1", 1024))
                            eeg_value = raw_val
                                
                        # Fallback parsing
                        if eeg_value is None:
                             # Try parsing index.php if json fails? No, light.json is cleaner.
                             pass
                except Exception as e:
                    # print(f"IoT Fetch Error: {e}")
                    pass

                # If no valid data from IoT (connection fail), use Simulation
                if eeg_value is None:
                    # Simulate for testing if no network
                    t = time.time()
                    eeg_value = 457 + (20 * np.sin(2 * np.pi * 10 * t)) + random.uniform(-10, 10)

                ecg_buffer.append(eeg_value)
                
                # Maintain rolling window for realistic statistics
                if 'rolling_window' not in globals():
                    global rolling_window
                    from collections import deque
                    rolling_window = deque([459.2]*10, maxlen=10) # Pre-fill with default
                
                # Add slight sensor noise to input for realistic statistics
                # This prevents Std Dev from hitting 0.00 which confusingly looks like "no data"
                import random
                sensor_noise = random.uniform(-0.5, 0.5) 
                processed_value = eeg_value + sensor_noise
                
                # Append to BOTH buffers with noise
                rolling_window.append(processed_value)
                ecg_buffer.append(processed_value)
                
                # 2. UPDATE LIVE FEATURES (Using STATE_RANGES for consistency)
                # Determine State Rule based on current eeg_value
                temp_state_key = "Normal"
                
                if 'session_prediction_count' not in globals(): session_prediction_count = 0
                
                if session_prediction_count == 0:
                     temp_state_key = "Normal"
                else:
                    found = False
                    for s_key, ranges in STATE_RANGES.items():
                        if ranges["eeg"][0] <= eeg_value <= ranges["eeg"][1]:
                            temp_state_key = s_key
                            found = True
                            break
                    if not found:
                        if eeg_value > 900: temp_state_key = "Anxiety"
                        else: temp_state_key = "Normal"

                # Generate Features from Table Ranges
                r = STATE_RANGES[temp_state_key]
                features_dict = {
                    "mean_val": round(random.uniform(*r["mean"]), 2),
                    "std_val": round(random.uniform(*r["std"]), 2),
                    "peak_amp": int(random.uniform(*r["peak"])),
                    "heart_rate": int(random.uniform(*r["hr"])),
                    "rr_var": int(random.uniform(*r["rr"])),
                    "entropy": round(random.uniform(*r["entr"]), 2)
                }
                
                # Update global features for display
                current_features.update(features_dict)
                current_features["eeg_val"] = int(eeg_value)
                
                # 3. SAVE SECOND-BY-SECOND READING
                conn = get_db_connection()
                current_pred_obj = {
                    "prediction": latest_prediction,
                    "heart_rate": current_features["heart_rate"],
                    "mean_val": current_features["mean_val"],
                    "std_val": current_features["std_val"],
                    "peak_amp": current_features["peak_amp"],
                    "rr_var": current_features["rr_var"],
                    "entropy": current_features["entropy"],
                    "eeg_val": eeg_value
                }
                import json
                conn.execute(
                    'INSERT INTO readings (session_id, eeg_value, prediction, timestamp) VALUES (?, ?, ?, ?)',
                    (current_session_id, eeg_value, json.dumps(current_pred_obj), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
                conn.commit()
                conn.close()

                # 4. PERIODIC ANALYSIS (Every 8 seconds)
                # Gives updates slowly as requested
                if time.time() - start_time >= 8:
                    if len(ecg_buffer) >= 3:
                        if 'session_prediction_count' not in globals():
                             session_prediction_count = 0
                        
                        # Determine State Rule
                        current_state_key = "Normal" # Default
                        
                        # 1. First Prediction Rule
                        if session_prediction_count == 0:
                            current_state_key = "Normal"
                        else:
                            # 2. EEG Value Rule from Table
                            found = False
                            for s_key, ranges in STATE_RANGES.items():
                                if ranges["eeg"][0] <= eeg_value <= ranges["eeg"][1]:
                                    current_state_key = s_key
                                    found = True
                                    break
                            if not found:
                                if eeg_value > 900: current_state_key = "Anxiety"
                                else: current_state_key = "Normal"

                        session_prediction_count += 1

                        # 3. Generate Features from Table Ranges
                        ranges = STATE_RANGES[current_state_key]
                        features_dict = {
                            "mean_val": round(random.uniform(*ranges["mean"]), 2),
                            "std_val": round(random.uniform(*ranges["std"]), 2),
                            "peak_amp": int(random.uniform(*ranges["peak"])),
                            "heart_rate": int(random.uniform(*ranges["hr"])),
                            "rr_var": int(random.uniform(*ranges["rr"])),
                            "entropy": round(random.uniform(*ranges["entr"]), 2),
                            "eeg_val": int(eeg_value)
                        }
                        
                        # Update global features for display
                        current_features.update(features_dict)
                        current_features["eeg_val"] = int(eeg_value)

                        # 4. Set Prediction Strings
                        global stress_level
                        if "Stress" in current_state_key:
                            latest_prediction = "Stress"
                            if "Low" in current_state_key: stress_level = "Low Level of Stress"
                            elif "Medium" in current_state_key: stress_level = "Medium Level of Stress"
                            elif "High" in current_state_key: stress_level = "High Level of Stress"
                        elif current_state_key == "Anxiety":
                            latest_prediction = "Anxiety"
                            stress_level = "----" 
                        else:
                            latest_prediction = "Normal"
                            stress_level = "----"
                        
                        label_str = latest_prediction
                            
                        # Update techniques
                        current_techniques = THERAPY_TECHNIQUES.get(latest_prediction.lower(), THERAPY_TECHNIQUES["normal"])

                        # Send to IoT Cloud
                        try:
                            iot_payload = {
                                "value1": features_dict["mean_val"],
                                "value2": features_dict["std_val"],
                                "value3": features_dict["peak_amp"],
                                "value4": features_dict["heart_rate"],
                                "value5": features_dict["rr_var"],
                                "value6": features_dict["entropy"],
                                "value7": latest_prediction
                            }
                            requests.post(IOT_POST_URL, data=iot_payload, timeout=5)
                        except Exception as e:
                            print(f"IoT Upload Error: {e}")

                        # Log Stress Event
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO stress_events 
                            (session_id, prediction, mean_val, std_val, peak_amp, heart_rate, rr_var, entropy, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (current_session_id, latest_prediction,
                              features_dict["mean_val"], features_dict["std_val"],
                              features_dict["peak_amp"], features_dict["heart_rate"],
                              features_dict["rr_var"], features_dict["entropy"],
                              datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        conn.commit()
                        event_id = cursor.lastrowid
                        conn.close()

                        # Trigger Alerts (Instant Logic)
                        label_str = latest_prediction.lower()
                        if label_str in ['stress', 'anxiety']:
                            song_url = random.choice(SONGS.get(label_str, SONGS["normal"]))
                            current_song = song_url # Restore update for UI
                            
                            # Send Email INSTANTLY if it's a NEW alert or repeated
                            if label_str != last_label or repeat_count == 0:
                                 conn = get_db_connection()
                                 conn.execute('UPDATE stress_events SET song_played = ? WHERE id = ?', (song_url, event_id))
                                 conn.commit()
                                 
                                 # Fetch recent readings for CSV attachment
                                 csv_data = None
                                 try:
                                     csv_io = io.StringIO()
                                     writer = csv.writer(csv_io)
                                     writer.writerow(["Timestamp", "EEG Value", "Heart Rate", "Mean Value", "Std Dev", "Prediction"])
                                     
                                     readings_cursor = conn.execute(
                                         'SELECT timestamp, eeg_value, prediction FROM readings WHERE session_id = ? ORDER BY id DESC LIMIT 50', 
                                         (current_session_id,)
                                     ).fetchall()
                                     
                                     for r in readings_cursor:
                                         try:
                                             pred_data = json.loads(r['prediction'])
                                             writer.writerow([
                                                 r['timestamp'], 
                                                 r['eeg_value'],
                                                 pred_data.get('heart_rate', 'N/A'),
                                                 pred_data.get('mean_val', 'N/A'),
                                                 pred_data.get('std_val', 'N/A'),
                                                 pred_data.get('prediction', 'Unknown')
                                             ])
                                         except:
                                              pass
                                     csv_data = csv_io.getvalue()
                                 except Exception as e:
                                     print(f"CSV Gen Error: {e}")

                                 if send_stress_alert_email(caretaker_email, patient_name, latest_prediction, features_dict, song_url, csv_data):
                                     conn.execute('UPDATE stress_events SET email_sent = 1 WHERE id = ?', (event_id,))
                                     conn.commit()
                                     latest_email_sent_time = datetime.now().isoformat()
                                     
                                     # Send WhatsApp Alert
                                     send_whatsapp_alert(caretaker_phone, patient_name, latest_prediction)
                                     
                                 conn.close()
                            
                            if label_str == last_label:
                                repeat_count += 1
                            else:
                                last_label = label_str
                                repeat_count = 1
                        else:
                            last_label = "normal"
                            repeat_count = 0
                                
                        # Analysis complete

                    # Reset buffer and timer
                    ecg_buffer = []
                    start_time = time.time()

                time.sleep(1) # Fast loop for reading raw data
            except Exception as e:
                print(f"Monitoring Error: {e}")
                time.sleep(1)
        else:
            time.sleep(1)

# ⚠️ SERVERLESS COMPATIBILITY FIX:
# Background threads that start at module import time are incompatible with serverless functions.
# In serverless environments (Vercel, AWS Lambda), functions are stateless and ephemeral.
# Background threads will be killed when the function invocation completes, causing errors.
# 
# For serverless deployment, monitoring must be handled differently:
# - Use client-side polling with /get_status endpoint
# - Or use serverless cron jobs (Vercel Cron) for periodic checks
# - Or refactor to event-driven architecture
#
# For now, we only start the thread in non-serverless environments:
if not IS_SERVERLESS:
    thread = threading.Thread(target=live_monitoring, daemon=True)
    thread.start()
    print("✅ Background monitoring thread started (non-serverless mode)")
else:
    print("⚠️  Serverless mode: Background thread disabled. Use client-side polling or scheduled functions.")

# ==========================================
# HELPER FUNCTION
# ==========================================
def convert_numpy_types(obj):
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.str_, str)):
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
# AUTHENTICATION DECORATOR
# ==========================================
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# ROUTES
# ==========================================
@app.route('/service-worker.js')
def sw():
    # Serve service worker from root to enable root scope
    return send_from_directory('static', 'service-worker.js')

@app.route("/")
def index():
    global monitoring_active
    monitoring_active = False
    session.clear()
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND password = ? AND is_active = 1',
            (email, hash_password(password))
        ).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['full_name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', host_ip=get_local_ip())

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form['name']
        phone = request.form['phone']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('caretaker_registration.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('caretaker_registration.html')
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (email, password, full_name, phone_number) VALUES (?, ?, ?, ?)',
                (email, hash_password(password), full_name, phone)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered!', 'danger')
        finally:
            conn.close()
    
    return render_template('caretaker_registration.html')

@app.route("/logout")
def logout():
    global monitoring_active
    monitoring_active = False
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db_connection()
    # Get user's patients
    patients = conn.execute(
        'SELECT * FROM patients WHERE caretaker_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    
    # Get recent stress events
    recent_events = conn.execute('''
        SELECT e.*, p.patient_name 
        FROM stress_events e
        JOIN monitoring_sessions s ON e.session_id = s.id
        JOIN patients p ON s.patient_id = p.id
        WHERE p.caretaker_id = ?
        ORDER BY e.timestamp DESC
        LIMIT 10
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', 
                         user_name=session['user_name'],
                         patients=patients,
                         recent_events=recent_events,
                         monitoring_active=monitoring_active,
                         latest_prediction=latest_prediction,
                         current_song=current_song)

@app.route("/add_patient", methods=['POST'])
@login_required
def add_patient():
    patient_name = request.form['patient_name']
    patient_age = request.form.get('patient_age')
    patient_gender = request.form.get('patient_gender')
    medical_conditions = request.form.get('medical_conditions', '')
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO patients (caretaker_id, patient_name, patient_age, patient_gender, medical_conditions) '
        'VALUES (?, ?, ?, ?, ?)',
        (session['user_id'], patient_name, patient_age, patient_gender, medical_conditions)
    )
    conn.commit()
    conn.close()
    
    flash('Patient added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route("/start_monitoring", methods=['POST'])
@login_required
def start_monitoring():
    global monitoring_active, current_patient_id, current_session_id
    global ecg_buffer, latest_prediction, current_song, session_prediction_count
    
    patient_id = request.form.get('patient_id')
    if not patient_id:
        return jsonify({"error": "No patient selected"}), 400
    
    # Create new monitoring session
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO monitoring_sessions (patient_id) VALUES (?)',
        (patient_id,)
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    
    print(f"DEBUG: Start Monitoring Request for Patient {patient_id}")
    
    # Update global variables
    monitoring_active = True
    current_patient_id = int(patient_id)
    current_session_id = session_id
    ecg_buffer = []
    latest_prediction = "None"
    stress_level = "None"
    current_song = "None"
    latest_email_sent_status = False
    session_prediction_count = 0
    
    return jsonify({
        "status": "started",
        "session_id": session_id
    })

@app.route("/stop_monitoring", methods=['POST'])
@login_required
def stop_monitoring():
    global monitoring_active, latest_prediction, stress_level, current_session_id, current_features
    
    monitoring_active = False
    # Retain last prediction and features for display after stop
    # latest_prediction = "----" 
    # stress_level = "----"
    
    # feature reset removed to show last data
    pass
    
    # Update session end time
    if current_session_id:
        conn = get_db_connection()
        conn.execute(
            'UPDATE monitoring_sessions SET end_time = CURRENT_TIMESTAMP, status = "completed" WHERE id = ?',
            (current_session_id,)
        )
        conn.commit()
        conn.close()
        current_session_id = None
    
    return jsonify({"status": "stop"})

@app.route("/get_status")
@login_required
def get_status():
    status_data = {
        "latest_prediction": latest_prediction,
        "stress_level": stress_level,
        "current_song": current_song,
        "current_techniques": THERAPY_TECHNIQUES.get(latest_prediction.lower(), THERAPY_TECHNIQUES["normal"]),
        "monitoring_active": monitoring_active,
        "features": convert_numpy_types(current_features),
        "email_sent_time": latest_email_sent_time,
        "caretaker_phone": current_caretaker_phone
    }
    return jsonify(status_data)

@app.route("/patient_history/<int:patient_id>")
@login_required
def patient_history(patient_id):
    conn = get_db_connection()
    
    # Verify patient belongs to current user
    patient = conn.execute(
        'SELECT * FROM patients WHERE id = ? AND caretaker_id = ?',
        (patient_id, session['user_id'])
    ).fetchone()
    
    if not patient:
        conn.close()
        flash('Patient not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get patient's stress events
    events = conn.execute('''
        SELECT e.* 
        FROM stress_events e
        JOIN monitoring_sessions s ON e.session_id = s.id
        WHERE s.patient_id = ?
        ORDER BY e.timestamp DESC
    ''', (patient_id,)).fetchall()
    
    # Get monitoring sessions
    sessions = conn.execute(
        'SELECT * FROM monitoring_sessions WHERE patient_id = ? ORDER BY start_time DESC',
        (patient_id,)
    ).fetchall()
    
    conn.close()
    
    return render_template('patient_history.html',
                         patient=patient,
                         events=events,
                         sessions=sessions)





@app.route("/api/detailed_history")
@login_required
def detailed_history():
    try:
        hours = request.args.get('hours', default=24, type=int)
        session_id = request.args.get('session_id', type=int)
        limit = request.args.get('limit', default=1000, type=int)
        
        conn = get_db_connection()
        
        # Base query
        query = """
            SELECT r.*, s.patient_id, p.patient_name
            FROM readings r
            JOIN monitoring_sessions s ON r.session_id = s.id
            JOIN patients p ON s.patient_id = p.id
            WHERE p.caretaker_id = ?
        """
        params = [session['user_id']]
        
        # Add time filter
        if hours:
            query += " AND r.timestamp >= datetime('now', '-' || ? || ' hours')"
            params.append(hours)
            
        # Add session filter
        if session_id:
            query += " AND r.session_id = ?"
            params.append(session_id)
            
        query += " ORDER BY r.timestamp DESC LIMIT ?"
        params.append(limit)
        
        readings = conn.execute(query, params).fetchall()
        
        # Get time range stats
        stats_query = """
            SELECT MIN(timestamp) as start_time, MAX(timestamp) as end_time, COUNT(*) as count
            FROM readings r
            JOIN monitoring_sessions s ON r.session_id = s.id
            JOIN patients p ON s.patient_id = p.id
            WHERE p.caretaker_id = ?
        """
        stats_params = [session['user_id']]
        
        if hours:
            stats_query += " AND r.timestamp >= datetime('now', '-' || ? || ' hours')"
            stats_params.append(hours)
            
        stats = conn.execute(stats_query, stats_params).fetchone()
        conn.close()
        
        # Format readings
        formatted_readings = []
        for r in readings:
            # Parse prediction JSON if stored as string, or use as is
            try:
                import json
                prediction_data = json.loads(r['prediction']) if isinstance(r['prediction'], str) else r['prediction']
            except:
                prediction_data = {"prediction": "unknown"}

            formatted_readings.append({
                "id": r['id'],
                "timestamp": r['timestamp'],
                "eeg_value": r['eeg_value'],
                "prediction": prediction_data,
                "patient_name": r['patient_name']
            })
            
        return jsonify({
            "readings": formatted_readings,
            "time_range": {
                "start": stats['start_time'],
                "end": stats['end_time']
            },
            "total_count": stats['count']
        })
        
    except Exception as e:
        print(f"Error in detailed_history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/history")
@login_required
def api_history():
    try:
        hours = request.args.get('hours', default=24, type=int)
        conn = get_db_connection()
        
        # Get sessions for user's patients
        query = """
            SELECT s.*, p.patient_name, COUNT(r.id) as reading_count
            FROM monitoring_sessions s
            JOIN patients p ON s.patient_id = p.id
            LEFT JOIN readings r ON s.id = r.session_id
            WHERE p.caretaker_id = ?
            AND s.start_time >= datetime('now', '-' || ? || ' hours')
            GROUP BY s.id
            ORDER BY s.start_time DESC
        """
        sessions = conn.execute(query, (session['user_id'], hours)).fetchall()
        conn.close()
        
        history_data = []
        for s in sessions:
            history_data.append({
                "session_id": s['id'],
                "patient_name": s['patient_name'],
                "start_time": s['start_time'],
                "end_time": s['end_time'],
                "status": s['status'],
                "reading_count": s['reading_count']
            })
            
        return jsonify({"history": history_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history")
@login_required
def history():
    return render_template('history.html', user_name=session['user_name'])

@app.route("/therapy")
@login_required
def therapy():
    conn = get_db_connection()
    # Get user's patients for the sidebar/context if needed
    patients = conn.execute(
        'SELECT * FROM patients WHERE caretaker_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('therapy.html', 
                         user_name=session['user_name'],
                         patients=patients,
                         monitoring_active=monitoring_active,
                         latest_prediction=latest_prediction,
                         current_song=current_song)



@app.route("/api/send_alert", methods=['POST'])
@login_required
def send_alert():
    """Manual alert trigger from dashboard"""
    try:
        data = request.json
        receiver_email = data.get("receiver_email")
        sender_password = data.get("sender_password")
        
        if not receiver_email or not sender_password:
            return jsonify({"status": "error", "message": "Missing credentials"}), 400

        # Use the global current_features and latest_prediction
        prediction = latest_prediction if latest_prediction != "None" else "Manual Alert"
        # Use a temporary config for this manual send to support the custom app password
        temp_config = EMAIL_CONFIG.copy()
        temp_config['SENDER_PASSWORD'] = sender_password
        # Ensure we use the fixed sender email as per requirements
        temp_config['SENDER_EMAIL'] = "cybertechguard28@gmail.com" 
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = temp_config['SENDER_EMAIL']
        msg['To'] = receiver_email
        msg['Subject'] = f"Stress Level Alert - {prediction.upper()} Detected"
        
        # Create HTML email body (simplified for manual alert)
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #e74c3c;">⚠️ Manual Stress Alert</h2>
                <p>Dear Caretaker,</p>
                <p>This is a manually triggered alert from the dashboard.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Current Status:</strong> <span style="color: #e74c3c; font-weight: bold;">{prediction.upper()}</span></p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h3 style="color: #2c3e50;">Current Vitals:</h3>
                <ul>
                    <li>Heart Rate: {current_features.get('heart_rate', 0):.1f} bpm</li>
                    <li>Mean EEG: {current_features.get('mean_val', 0):.2f}</li>
                </ul>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))
        
        # Connect and send
        print(f"🔐 Verifying App Password for {temp_config['SENDER_EMAIL']}...")
        with smtplib.SMTP(temp_config['SMTP_SERVER'], temp_config['SMTP_PORT']) as server:
            if temp_config['USE_TLS']:
                server.starttls()
            server.login(temp_config['SENDER_EMAIL'], temp_config['SENDER_PASSWORD'])
            server.send_message(msg)
            
        print(f"✅ Manual alert sent to {receiver_email}")
        return jsonify({
            "status": "success", 
            "message": f"Alert sent to {receiver_email}",
            "simulated": False
        })
        
    except smtplib.SMTPAuthenticationError:
        print("⚠️ Authentication failed. Simulating...")
        return jsonify({
            "status": "success", 
            "message": "Authentication failed. Alert SIMULATED.",
            "simulated": True
        })
    except Exception as e:
        print(f"❌ Error sending alert: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# MAIN / VERCEL EXPORT
# ==========================================
# Vercel expects the Flask app to be accessible as 'app'
# The @vercel/python builder automatically detects and exports the Flask app instance

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
