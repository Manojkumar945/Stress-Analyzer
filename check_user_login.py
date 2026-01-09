import sqlite3
import hashlib

DATABASE = 'stress_monitor.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(email, password):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    user = conn.execute(
        'SELECT * FROM users WHERE email = ?',
        (email,)
    ).fetchone()
    conn.close()
    
    if user:
        print(f"User found: {user['email']}")
        print(f"Stored Hash: {user['password']}")
        input_hash = hash_password(password)
        print(f"Input Hash:  {input_hash}")
        if user['password'] == input_hash:
            print("Password MATCH")
        else:
            print("Password MISMATCH")
            # Update password to match
            conn = sqlite3.connect(DATABASE)
            conn.execute('UPDATE users SET password = ? WHERE email = ?', (input_hash, email))
            conn.commit()
            conn.close()
            print("Password updated to match input.")
    else:
        print("User NOT found")

if __name__ == "__main__":
    check_login('admin@example.com', 'password123')
