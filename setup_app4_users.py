
import sqlite3
import hashlib

DB_PATH = "stress_monitor.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_and_fix_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if users table exists (app4.py schema)
    try:
        cursor.execute("SELECT count(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"Found {count} users in 'users' table.")
        
        if count == 0:
            print("Creating default user for app4.py...")
            # Create default admin user
            email = "admin@example.com"
            password = "password123"
            full_name = "Admin User"
            
            cursor.execute(
                'INSERT INTO users (email, password, full_name, is_active) VALUES (?, ?, ?, 1)',
                (email, hash_password(password), full_name)
            )
            conn.commit()
            print(f"Created user: {email} / {password}")
            
            # Create cybertech user
            email2 = "cybertechguard28@gmail.com"
            cursor.execute(
                'INSERT INTO users (email, password, full_name, is_active) VALUES (?, ?, ?, 1)',
                (email2, hash_password(password), "CyberTech Guard")
            )
            conn.commit()
            print(f"Created user: {email2} / {password}")
            
    except sqlite3.OperationalError as e:
        print(f"Error accessing users table: {e}")
        print("It seems the table might not exist or schema is different.")
        
    conn.close()

if __name__ == "__main__":
    check_and_fix_users()
