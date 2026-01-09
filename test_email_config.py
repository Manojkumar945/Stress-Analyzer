import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_CONFIG = {
    'SENDER_EMAIL': 'cybertechguard28@gmail.com',
    'SENDER_PASSWORD': 'kyucxjzrwaxaskgt',
}

def test_email():
    print(f"Testing credentials for {EMAIL_CONFIG['SENDER_EMAIL']}...")
    
    # Test 1: Port 587 (STARTTLS)
    print("\n--- Test 1: Port 587 (STARTTLS) ---")
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['SENDER_PASSWORD'])
        print("✅ Login SUCCESSFUL on Port 587!")
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Login FAILED on Port 587: {e}")

    # Test 2: Port 465 (SSL)
    print("\n--- Test 2: Port 465 (SSL) ---")
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['SENDER_PASSWORD'])
        print("✅ Login SUCCESSFUL on Port 465!")
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Login FAILED on Port 465: {e}")
    
    return False

if __name__ == "__main__":
    test_email()
