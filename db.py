import sqlite3
from sqlite3 import Error
import hashlib
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def create_connection(db_file="shop_management.db"):
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        db_path = resource_path(db_file)
        conn = sqlite3.connect(db_path)
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables():
    """Create all necessary tables in the SQLite database."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()

        # Users table for login
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        """)

        # Products table for stock management
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            cost_price REAL NOT NULL DEFAULT 0.0,
            description TEXT,
            stock INTEGER NOT NULL,
            alert_threshold INTEGER NOT NULL
        );
        """)

        # Transactions table for recording sales
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
        """)
        
        # Cost price history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cost_price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            old_cost_price REAL NOT NULL,
            new_cost_price REAL NOT NULL,
            change_date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
        """)
        conn.commit()
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == "__main__":
    create_tables()

    # Insert default admin user if not exists
    conn = sqlite3.connect("shop_management.db")
    cursor = conn.cursor()
    username = "admin"
    password = "password"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
    conn.close()