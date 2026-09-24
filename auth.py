import hashlib
from database import connect

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_users_table():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Admin'
        )
    """)
    
    # Create default admin user if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_pass = hash_password("admin123")
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       ("admin", default_pass, "Admin"))
        conn.commit()
        
    conn.close()

def authenticate_user(username, password):
    conn = connect()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", 
                   (username, hashed))
    user = cursor.fetchone()
    conn.close()
    return user  # Returns (id, username, role) if valid, else None