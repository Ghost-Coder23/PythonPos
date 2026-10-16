import sqlite3
import hashlib

def create_connection(db_file="shop_management.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return conn

def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print(f"User '{username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists.")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python add_user.py <username> <password>")
    else:
        add_user(sys.argv[1], sys.argv[2])
