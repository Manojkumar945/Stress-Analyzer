import sqlite3
import hashlib

DATABASE_PATH = 'stress_monitor.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def reset_password(email, new_password):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    hashed_pw = hash_password(new_password)
    
    cursor.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_pw, email))
    
    if cursor.rowcount > 0:
        print(f"Password for {email} updated successfully.")
    else:
        print(f"User {email} not found.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset_password('admin@example.com', 'password123')
