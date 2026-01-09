import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket

EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'SENDER_EMAIL': 'cybertechguard28@gmail.com',
    'SENDER_PASSWORD': 'kyucxjzrwaxaskgt', 
    'USE_TLS': True
}

def debug_email():
    print(f"DEBUG: Testing connectivity to {EMAIL_CONFIG['SMTP_SERVER']}...")
    try:
        # Check DNS resolution
        ip = socket.gethostbyname(EMAIL_CONFIG['SMTP_SERVER'])
        print(f"DEBUG: Resolved {EMAIL_CONFIG['SMTP_SERVER']} to {ip}")
    except Exception as e:
        print(f"ERROR: DNS resolution failed: {e}")
        return

    print("\n--- Test 1: Port 587 (STARTTLS) ---")
    try:
        server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], 587)
        server.set_debuglevel(1)  # Enable verbose output
        print("DEBUG: Connected to server")
        
        server.ehlo()
        if server.has_extn('STARTTLS'):
            print("DEBUG: Starting TLS")
            server.starttls()
            server.ehlo()
        
        print(f"DEBUG: Attempting login as {EMAIL_CONFIG['SENDER_EMAIL']}")
        server.login(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['SENDER_PASSWORD'])
        print("✅ SUCCESS: Login accepted!")
        
        # Try sending a test email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['SENDER_EMAIL']
        msg['To'] = EMAIL_CONFIG['SENDER_EMAIL'] # Send to self
        msg['Subject'] = "Test Email from Debug Script"
        msg.attach(MIMEText("This is a test email to verify the configuration.", 'plain'))
        
        server.send_message(msg)
        print("✅ SUCCESS: Test email sent!")
        
        server.quit()
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    debug_email()
