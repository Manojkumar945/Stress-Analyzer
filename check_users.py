import sqlite3

DATABASE_PATH = 'stress_monitor.db'

def check_users():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, email, full_name, is_active FROM users')
    users = cursor.fetchall()
    
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"ID: {user['id']}, Email: {user['email']}, Name: {user['full_name']}, Active: {user['is_active']}")
    
    conn.close()

if __name__ == "__main__":
    check_users()
