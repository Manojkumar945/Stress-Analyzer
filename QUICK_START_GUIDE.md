# Quick Start Guide - WiFi EEG Board Setup

## ✅ Everything is Ready!

Your Brainwave Monitoring and Stress Alert System is complete and ready to use with your WiFi-enabled EEG board.

## 🚀 Quick Steps to Get Started

### Step 1: Configure Your EEG Board

Your EEG board needs to send data to this endpoint:
```
https://iotcloud22.in/4503_eeg/post_value1.php
```

**Data Format:**
```
value1=[eeg_value]
```

**Example Code for ESP32:**
```cpp
// Send data every 2 seconds
String postData = "value1=" + String(eegValue);
http.POST(postData);
```

See `EEG_BOARD_SETUP.md` for complete code examples.

### Step 2: Test Connection

1. **Open Connection Test Page**: http://localhost:5000/connection-test
2. **Click "Test Connection"**
3. **Verify Status**: Should show "Connected" with EEG value

### Step 3: Start Monitoring

1. **Go to Stress Dashboard**: http://localhost:5000/stress-dashboard
2. **Check Connection Status**: Should show "EEG Board: Connected" (green)
3. **Click "Start Monitoring"**
4. **Watch Real-Time Data**: Stress Detection panel will update every 2 seconds

### Step 4: View Real-Time Data

In the Stress Detection section, you'll see:
- ✅ **Mean Value** (Blue) - updating in real-time
- ✅ **Standard Deviation** (Green)
- ✅ **Peak Amplitude** (Orange)
- ✅ **Heart Rate** (Red)
- ✅ **RR Variance** (Green)
- ✅ **Entropy** (Purple)
- ✅ **Result** - "normal", "stress", or "anxiety"

All values update automatically every 2 seconds from your EEG board!

## 📊 Available Pages

- **Main Dashboard**: http://localhost:5000/ - Real-time EEG chart
- **Stress Dashboard**: http://localhost:5000/stress-dashboard - Start monitoring here
- **Connection Test**: http://localhost:5000/connection-test - Test EEG board connection
- **History View**: http://localhost:5000/history - View all historical data
- **Caretaker Registration**: http://localhost:5000/caretaker-registration - Register caretakers

## 🔧 Troubleshooting

**No data appearing?**
1. Check Connection Test page
2. Verify EEG board is connected to WiFi
3. Check if IoT endpoint is accessible
4. Look at Flask console for error messages

**Connection timeout?**
- Check internet connection
- Verify IoT endpoint URL is correct
- Check firewall settings

**Wrong data format?**
- System supports: `value1`, `eeg_value`, `value`, or numeric arrays
- Check `main_app.py` for supported formats

## ✅ System Features Ready

1. ✅ **Real-time EEG Data** - Fetches from WiFi board every 2 seconds
2. ✅ **Stress Detection** - Automatic ML-based predictions every 10 seconds
3. ✅ **Caretaker Alerts** - Email/SMS when stress/anxiety detected
4. ✅ **Smart Therapy** - Music and relaxation techniques
5. ✅ **History Tracking** - Second-by-second data with timeline
6. ✅ **Connection Monitoring** - Real-time connection status

## 🎯 You're All Set!

Your system is ready to monitor brainwave data in real-time. Just:
1. Connect your EEG board to WiFi
2. Configure board to send data to IoT endpoint
3. Start monitoring in Stress Dashboard
4. Watch real-time stress detection!

Need help? Check `EEG_BOARD_SETUP.md` for detailed setup instructions.

