
import os

# Read the file
with open('app4.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The code to insert
insert_code = '''
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

'''

# Split at the main block
parts = content.split('# ==========================================\n# MAIN')

if len(parts) == 2:
    new_content = parts[0] + insert_code + '# ==========================================\n# MAIN' + parts[1]
    
    with open('app4.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully added send_alert endpoint.")
else:
    print("Could not find the insertion point.")
