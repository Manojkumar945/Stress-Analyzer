# Brainwave Monitoring and Stress Alert System

A comprehensive real-time EEG monitoring system with stress detection, caretaker alerts, and smart therapy recommendations.

## Features

### 1. Instant Caretaker Alert System
- **Caretaker Registration**: Register caretakers with Name, Mobile Number, and Email ID
- **Multiple Caretakers**: Support for multiple registered caretakers
- **Automatic Alerts**: Email and SMS notifications sent to all active caretakers when stress or anxiety is detected
- **Alert Management**: Activate/deactivate caretakers, delete caretakers
- **Test Alert Functionality**: Send test alerts to verify notification system
- **Spam Prevention**: Time-based throttling prevents alert spam

### 2. Smart Therapy System
- **Music Therapy**: Automatically recommends calming music based on detected stress levels
  - Normal state: Calm piano, nature sounds, meditation music
  - Stress state: Deep relaxation, stress relief music
  - Anxiety state: Anxiety relief, soothing sounds
- **Relaxation Techniques**: Provides mindset relaxing techniques
  - Breathing exercises (4-7-8, box breathing)
  - Grounding techniques (5-4-3-2-1 method)
  - Mindfulness and meditation guidance
  - Progressive muscle relaxation

### 3. EEG Dashboard
- Real-time EEG value display
- Last reading timestamp
- Interactive line chart showing EEG activity over time
- Stress detection metrics display

### 4. EEG Stress Detection Dashboard
- Start/Stop monitoring controls
- Real-time status updates
- Extracted features display:
  - Mean Value
  - Standard Deviation
  - Peak Amplitude
  - Heart Rate
  - RR Variance
  - Entropy
- Latest prediction status

### 5. Real-time EEG Data Analysis
- **Real EEG Board Connection**: Automatically extracts data from connected EEG board via IoT endpoint
- **Second-by-Second Recording**: Stores every reading with precise timestamp
- **Automatic Data Extraction**: Intelligently extracts EEG values from various JSON formats
- **Continuous Monitoring**: Fetches data every 2 seconds from IoT endpoint
- **Feature Extraction**: Processes readings every 10 seconds for stress detection
- **ML Model Prediction**: Uses Random Forest model for accurate stress/anxiety detection
- **Historical Storage**: Stores all readings in SQLite database for analysis
- **Real-time Visualization**: Live charts and dashboards

### 6. Detailed History View
- **Second-by-Second Timeline**: View every EEG reading with exact timestamps
- **Interactive Chart**: Scrollable timeline visualization of all readings
- **Searchable Table**: Filter and search through historical data
- **Session Filtering**: View data by monitoring session
- **Export Functionality**: Download history as CSV for analysis
- **Statistics**: Total readings, time range, average values, reading rate
- **Pagination**: Navigate through large datasets efficiently

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup Steps

1. **Clone or download this repository**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv myenv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     myenv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source myenv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Email Settings (Optional)**
   - Set environment variables for email notifications:
     ```bash
     # Windows (PowerShell)
     $env:EMAIL_ADDRESS="your_email@gmail.com"
     $env:EMAIL_PASSWORD="your_app_password"
     
     # Linux/Mac
     export EMAIL_ADDRESS="your_email@gmail.com"
     export EMAIL_PASSWORD="your_app_password"
     ```
   - For Gmail, use an App Password (not your regular password)
   - To disable email notifications, set `EMAIL_ENABLED = False` in `main_app.py`

6. **Configure SMS Settings (Optional)**
   - Set environment variables for SMS notifications (using Twilio):
     ```bash
     # Windows (PowerShell)
     $env:TWILIO_ACCOUNT_SID="your_twilio_account_sid"
     $env:TWILIO_AUTH_TOKEN="your_twilio_auth_token"
     $env:TWILIO_PHONE_NUMBER="your_twilio_phone_number"
     
     # Linux/Mac
     export TWILIO_ACCOUNT_SID="your_twilio_account_sid"
     export TWILIO_AUTH_TOKEN="your_twilio_auth_token"
     export TWILIO_PHONE_NUMBER="your_twilio_phone_number"
     ```
   - Install Twilio: `pip install twilio`
   - Uncomment Twilio code in `send_sms_notification()` function in `main_app.py`
   - To disable SMS notifications, set `SMS_ENABLED = False` in `main_app.py`

7. **Ensure ML model file exists**
   - Make sure `stress_rf_model.pkl` is in the project root
   - If not, run `train.py` to generate the model:
     ```bash
     python train.py
     ```

## Usage

### Starting the Application

1. **Run the main application**
   ```bash
   python main_app.py
   ```

2. **Access the dashboards**
   - Main EEG Dashboard: http://localhost:5000/
   - Stress Detection Dashboard: http://localhost:5000/stress-dashboard
   - Caretaker Registration: http://localhost:5000/caretaker-registration
   - Detailed History View: http://localhost:5000/history
   - Connection Test: http://localhost:5000/connection-test

### Using the Stress Detection Dashboard

1. Click **"Start Monitoring"** to begin real-time EEG monitoring
2. The system will:
   - Fetch EEG data from the IoT endpoint every 2 seconds
   - Extract features every 10 seconds
   - Make stress predictions using the ML model
   - Display real-time metrics and predictions
3. When stress/anxiety is detected:
   - Automatic alerts are sent to all registered active caretakers (Email + SMS)
   - Therapy recommendations appear
   - Music can be played manually via the "Play Calming Music" button
4. Click **"Stop Monitoring"** to pause monitoring

### Registering Caretakers

1. Navigate to **"Caretaker Registration"** page (link in Stress Dashboard or directly: `/caretaker-registration`)
2. Fill in the registration form:
   - **Name**: Full name of the caretaker
   - **Mobile Number**: Contact number (format: +1234567890 or local format)
   - **Email Address**: Email for receiving alerts
3. Click **"Register Caretaker"** to save
4. Registered caretakers will automatically receive alerts when stress/anxiety is detected
5. Manage caretakers:
   - **Activate/Deactivate**: Toggle caretaker status
   - **Delete**: Remove a caretaker from the system

### Using the Main EEG Dashboard

- Displays real-time EEG values and trends
- Shows extracted features and stress detection results
- Click "View History" to see detailed second-by-second history

### Using the History Page

1. Navigate to **"History"** page (link from Main Dashboard or directly: `/history`)
2. **Filter by Time Range**: Select hours (1, 6, 24, 48, or 168 hours)
3. **Filter by Session**: Select specific monitoring session from dropdown
4. **View Timeline Chart**: Interactive chart showing all readings over time
5. **Browse Readings**: Paginated table showing second-by-second data with:
   - Timestamp and time
   - EEG value
   - Stress prediction (if available)
   - Heart rate and features (if available)
6. **Search**: Use search box to filter readings by value or time
7. **Export**: Click "Export CSV" to download data for analysis

### EEG Board WiFi Connection

**For WiFi-Enabled EEG Boards (ESP32/ESP8266):**

1. **Setup EEG Board**:
   - Connect your EEG board to WiFi
   - Configure board to send data to: `https://iotcloud22.in/4503_eeg/post_value1.php`
   - Data format: `value1=[eeg_value]` or JSON format
   - See `EEG_BOARD_SETUP.md` for detailed instructions

2. **Test Connection**:
   - Go to Connection Test page: http://localhost:5000/connection-test
   - Click "Test Connection" to verify EEG board is sending data
   - Check connection status in Stress Dashboard

3. **Start Monitoring**:
   - When connected, go to Stress Dashboard
   - Click "Start Monitoring"
   - Real-time data will appear every 2 seconds

**How It Works:**
- System automatically fetches data from IoT endpoint every 2 seconds
- Each reading is stored with precise timestamp
- System intelligently extracts EEG values from JSON response
- Supports multiple JSON formats: `value1`, `eeg_value`, `value`, or numeric arrays
- Falls back to simulated data only if IoT endpoint is unavailable
- Real values are automatically used for accurate stress detection

**Connection Status Indicator:**
- Green "Connected" = EEG board sending data successfully
- Red "Disconnected" = No data received from EEG board
- Check Connection Test page for detailed diagnostics

## Configuration

### IoT Endpoint Configuration

Edit `main_app.py` to configure IoT endpoints:
```python
IOT_READ_URL = "https://iotcloud22.in/4503_eeg/light.json"
IOT_POST_URL = "https://iotcloud22.in/4503_eeg/post_value1.php"
```

### Model Path

Ensure the ML model path is correct:
```python
MODEL_PATH = "stress_rf_model.pkl"
```

### Database

The application uses SQLite for data storage. The database file `eeg_monitoring.db` is created automatically.

## File Structure

```
project-root/
├── main_app.py                  # Main Flask application
├── train.py                     # ML model training script
├── predict.py                   # Prediction script
├── stress_rf_model.pkl          # Trained ML model
├── stress_ecg_dataset.csv       # Training dataset
├── eeg_monitoring.db            # SQLite database (auto-created)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── templates/
│   ├── index.html                  # Main EEG Dashboard
│   ├── stress_dashboard.html       # Stress Detection Dashboard
│   └── caretaker_registration.html # Caretaker Registration Page
└── static/
    ├── css/
    │   ├── dashboard.css           # Main dashboard styles
    │   ├── stress_dashboard.css    # Stress dashboard styles
    │   └── caretaker_registration.css # Registration page styles
    └── js/
        ├── dashboard.js            # Main dashboard JavaScript
        ├── stress_dashboard.js     # Stress dashboard JavaScript
        └── caretaker_registration.js # Registration page JavaScript
```

## API Endpoints

### Dashboards
- `GET /` - Main EEG Dashboard
- `GET /stress-dashboard` - Stress Detection Dashboard
- `GET /caretaker-registration` - Caretaker Registration Page
- `GET /history` - Detailed History View with Timeline
- `GET /connection-test` - EEG Board Connection Test Page

### Monitoring
- `POST /api/start_monitoring` - Start EEG monitoring
- `POST /api/stop_monitoring` - Stop EEG monitoring
- `GET /api/status` - Get current monitoring status
- `GET /api/eeg_data` - Get recent EEG data for visualization
- `GET /api/test_connection` - Test EEG board connection to IoT endpoint
- `GET /api/history?hours=24` - Get aggregated historical predictions
- `GET /api/detailed_history?hours=24&session_id=xxx` - Get second-by-second readings
- `GET /api/get_sessions` - Get all available monitoring sessions

### Therapy
- `GET /api/therapy/<prediction_type>` - Get therapy content
- `POST /api/trigger_therapy` - Manually trigger therapy

### Caretaker Management
- `POST /api/register_caretaker` - Register a new caretaker
- `GET /api/get_caretakers` - Get all registered caretakers
- `PUT /api/update_caretaker/<id>` - Update caretaker status (activate/deactivate)
- `DELETE /api/delete_caretaker/<id>` - Delete a caretaker

### Alerts
- `POST /api/send_alert` - Send manual alert

## Troubleshooting

### Email Notifications Not Working
- Verify email credentials are correct
- For Gmail, ensure you're using an App Password
- Check that `EMAIL_ENABLED = True` in `main_app.py`
- Check firewall/network settings for SMTP access

### Model Not Found
- Ensure `stress_rf_model.pkl` exists in the project root
- Run `python train.py` to generate the model if missing

### IoT Connection Issues
- Verify IoT endpoint URLs are accessible (check `IOT_READ_URL` in `main_app.py`)
- Check network connectivity
- Verify EEG board is sending data to the IoT endpoint
- Check JSON format matches expected format (`value1`, `eeg_value`, `value`, or numeric)
- The system will use simulated data only if the endpoint is unavailable (check console logs)
- Real EEG values are automatically extracted when board is connected

### Database Errors
- Ensure write permissions in the project directory
- Delete `eeg_monitoring.db` to recreate the database

## License

This project is for educational and research purposes.

## Support

For issues or questions, please check:
1. Configuration settings in `main_app.py`
2. Environment variables are set correctly
3. All dependencies are installed
4. IoT endpoints are accessible

---

**Note**: This system is designed for monitoring and alerting purposes. For medical applications, ensure proper validation and regulatory compliance.


