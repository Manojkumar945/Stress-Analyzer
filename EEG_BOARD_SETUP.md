# EEG Board WiFi Connection Setup Guide

## Quick Setup for WiFi-Connected EEG Board

### Step 1: Configure Your EEG Board

Your EEG board needs to send data to this endpoint:
- **IoT Endpoint URL**: `https://iotcloud22.in/4503_eeg/light.json`
- **Update Endpoint**: `https://iotcloud22.in/4503_eeg/post_value1.php`

### Step 2: EEG Board Code Configuration

Your EEG board (ESP32/Arduino) should send data in this format:

#### Option 1: Using value1 field (Recommended)
```cpp
// For ESP32/Arduino with WiFi
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
String serverUrl = "https://iotcloud22.in/4503_eeg/post_value1.php";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi Connected!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    // Read EEG value from your sensor
    int eegValue = analogRead(A0); // Or your EEG sensor pin
    
    // Send data to IoT endpoint
    String postData = "value1=" + String(eegValue);
    int httpResponseCode = http.POST(postData);
    
    if (httpResponseCode > 0) {
      Serial.print("✅ Data sent: ");
      Serial.println(eegValue);
    } else {
      Serial.print("❌ Error: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
    delay(2000); // Send every 2 seconds
  }
}
```

#### Option 2: Using JSON format
```cpp
// Send JSON data
String jsonData = "{\"value1\":" + String(eegValue) + "}";
http.addHeader("Content-Type", "application/json");
http.POST(jsonData);
```

### Step 3: Verify EEG Board Connection

1. **Check WiFi Connection**:
   - Ensure your EEG board is connected to the same WiFi network
   - Verify the board can access the internet

2. **Test Endpoint Access**:
   - Open browser and go to: `https://iotcloud22.in/4503_eeg/light.json`
   - You should see JSON data with EEG values

3. **Monitor Serial Output**:
   - Check your board's serial monitor
   - Should show "WiFi Connected!" and data transmission confirmations

### Step 4: Start the Flask Application

1. **Run the application**:
   ```bash
   python main_app.py
   ```

2. **Check Console Output**:
   - Look for: `📡 EEG Data from IoT: {...}`
   - Look for: `✅ EEG Value extracted: [number]`
   - If you see errors, check the troubleshooting section

### Step 5: Start Monitoring

1. **Open Stress Dashboard**: `http://localhost:5000/stress-dashboard`
2. **Click "Start Monitoring"**
3. **Watch for real-time data**:
   - EEG values should appear in the Stress Detection section
   - Values update every 2 seconds
   - Features calculated every 10 seconds

### Step 6: Verify Real-Time Data

Check the Stress Detection panel for:
- ✅ Mean Value (Blue) - updating in real-time
- ✅ Standard Deviation (Green)
- ✅ Peak Amplitude (Orange)
- ✅ Heart Rate (Red)
- ✅ RR Variance (Green)
- ✅ Entropy (Purple)
- ✅ Result - showing "normal", "stress", or "anxiety"

---

## Troubleshooting

### Problem: No data appearing

**Check 1: IoT Endpoint**
```bash
# Test in browser
https://iotcloud22.in/4503_eeg/light.json
```
- Should return JSON like: `{"value1": 457}` or similar

**Check 2: EEG Board WiFi**
- Verify board is connected to WiFi
- Check serial monitor for connection status
- Test if board can reach the internet

**Check 3: Flask Application**
- Check console for errors
- Look for `⚠️ Error fetching EEG data from IoT`
- If errors, check network connectivity

### Problem: Wrong data format

The system supports multiple JSON formats:
- `{"value1": 457}` ✅
- `{"eeg_value": 457}` ✅
- `{"value": 457}` ✅
- `457` (direct number) ✅
- `[457]` (array) ✅

If your format is different, update `main_app.py` line 346-366 to handle your format.

### Problem: Connection timeout

- Increase timeout: Change `timeout=3` to `timeout=10` in `main_app.py` line 340
- Check firewall settings
- Verify IoT endpoint is accessible

### Problem: Data not updating

- Check if monitoring is started (green "Monitoring Active" status)
- Refresh the Stress Dashboard page
- Check browser console for JavaScript errors

---

## Connection Status Indicator

The application will show in console:
- `📡 EEG Data from IoT: {...}` - Data received successfully
- `✅ EEG Value extracted: [value]` - Value extracted correctly
- `⚠️ Error fetching EEG data from IoT: ...` - Connection error
- `📡 Falling back to simulated data` - Using fallback data

---

## Supported EEG Board Types

- ✅ ESP32 with WiFi
- ✅ ESP8266 with WiFi
- ✅ Arduino with WiFi Shield
- ✅ Raspberry Pi with WiFi
- ✅ Any device that can send HTTP POST to IoT endpoint

---

## Data Flow Diagram

```
EEG Board (WiFi) 
    ↓
IoT Endpoint (https://iotcloud22.in/4503_eeg/light.json)
    ↓
Flask App (main_app.py) - Fetches every 2 seconds
    ↓
Feature Extraction (every 10 seconds)
    ↓
ML Model Prediction
    ↓
Stress Detection Dashboard (Updates every 2 seconds)
```

---

## Next Steps

1. ✅ Connect EEG board to WiFi
2. ✅ Configure board to send data to IoT endpoint
3. ✅ Start Flask application
4. ✅ Start monitoring in Stress Dashboard
5. ✅ Verify real-time data appears
6. ✅ Monitor stress detection results

Your system is now ready to monitor real-time EEG data! 🚀

