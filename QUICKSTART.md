# Quick Start Guide

## Fast Setup (5 minutes)

### Step 1: Install Dependencies
```bash
# Activate virtual environment (if using one)
# Windows:
myenv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure (Optional)
If you want email alerts, set these environment variables:
```bash
# Windows PowerShell
$env:EMAIL_ADDRESS="your_email@gmail.com"
$env:EMAIL_PASSWORD="your_app_password"
$env:CARETAKER_EMAIL="caretaker@example.com"

# Or edit main_app.py and set EMAIL_ENABLED = False to disable
```

### Step 3: Run
```bash
python main_app.py
```

### Step 4: Open Browser
- Main Dashboard: http://localhost:5000/
- Stress Dashboard: http://localhost:5000/stress-dashboard

## Basic Usage

1. **Start Monitoring**:
   - Go to Stress Dashboard
   - Click "Start Monitoring"

2. **View Data**:
   - Main Dashboard shows real-time EEG values and charts
   - Stress Dashboard shows features and predictions

3. **Therapy**:
   - When stress/anxiety detected, click "Play Calming Music"
   - View relaxation techniques below

4. **Alerts**:
   - Automatic alerts sent when stress/anxiety detected
   - Test alert button available for verification

## Troubleshooting

**Model not found?**
```bash
python train.py
```

**Email not working?**
- Check environment variables are set
- For Gmail, use App Password (not regular password)
- Or set `EMAIL_ENABLED = False` in main_app.py

**IoT connection issues?**
- System uses simulated data if IoT endpoint unavailable
- Check IOT_READ_URL in main_app.py

That's it! The system is ready to use.


