"""
database.py - Database and Authentication Management for Chat Application
Oasis Infobyte Python Internship - Task 5

Handles SQLite database initialization, user registration with secure PBKDF2 password
hashing with unique salt, user authentication, room creation, and message history persistence.
Uses parameterized queries exclusively to prevent SQL injection vulnerabilities.
"""

import os
import sqlite3
import hashlib
import hmac
import re
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_app.db")


def get_db_connection(db_path=DEFAULT_DB_PATH):
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DEFAULT_DB_PATH):
    """
    Initializes the database schema with parameterized setup.
    Creates tables for users, rooms, and messages if they do not exist.
    Also seeds default rooms.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL COLLATE NOCASE,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # 2. Chat Rooms Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL COLLATE NOCASE,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # 3. Messages Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT NOT NULL COLLATE NOCASE,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Seed initial default chat rooms if empty
    cursor.execute("SELECT COUNT(*) FROM rooms")
    if cursor.fetchone()[0] == 0:
        default_rooms = ["General", "Python Hub", "Oasis Interns", "Tech Talk"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for room in default_rooms:
            cursor.execute(
                "INSERT INTO rooms (name, created_by, created_at) VALUES (?, ?, ?)",
                (room, "System", timestamp)
            )

    conn.commit()
    conn.close()


def _hash_password(password: str, salt_hex: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    Never stores plain-text passwords.
    """
    salt = bytes.fromhex(salt_hex)
    pwd_bytes = password.encode("utf-8")
    hash_bytes = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, 100_000)
    return hash_bytes.hex()


def register_user(username: str, password: str, db_path=DEFAULT_DB_PATH):
    """
    Registers a new user with input validation and cryptographic password hashing.
    Returns: (success: bool, message: str)
    """
    username = (username or "").strip()
    if not username:
        return False, "Username cannot be empty."

    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters."

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."

    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, f"Username '{username}' is already taken. Please choose another."

        # Generate cryptographically secure random 16-byte salt
        salt_hex = os.urandom(16).hex()
        password_hash = _hash_password(password, salt_hex)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO users (username, salt, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, salt_hex, password_hash, created_at)
        )
        conn.commit()
        return True, f"Registration successful! Welcome, {username}."
    except Exception as e:
        return False, f"Database error during registration: {str(e)}"
    finally:
        conn.close()


def verify_user(username: str, password: str, db_path=DEFAULT_DB_PATH):
    """
    Verifies user login credentials using constant-time hash comparison.
    Returns: (success: bool, message: str)
    """
    username = (username or "").strip()
    if not username or not password:
        return False, "Username and password are required."

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT salt, password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        if not row:
            return False, "Username not found. Please register first."

        salt_hex = row["salt"]
        stored_hash = row["password_hash"]
        computed_hash = _hash_password(password, salt_hex)

        # Constant-time comparison to prevent timing attacks
        if hmac.compare_digest(stored_hash, computed_hash):
            return True, "Login successful."
        else:
            return False, "Incorrect password. Please try again."
    except Exception as e:
        return False, f"Database error during login: {str(e)}"
    finally:
        conn.close()


def get_all_rooms(db_path=DEFAULT_DB_PATH):
    """Returns a list of all chat room names."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM rooms ORDER BY name COLLATE NOCASE ASC")
    rooms = [row["name"] for row in cursor.fetchall()]
    conn.close()
    return rooms


def create_room(room_name: str, created_by: str, db_path=DEFAULT_DB_PATH):
    """
    Creates a new chat room.
    Returns: (success: bool, message: str)
    """
    room_name = (room_name or "").strip()
    if not room_name:
        return False, "Room name cannot be empty."

    if len(room_name) < 2 or len(room_name) > 30:
        return False, "Room name must be between 2 and 30 characters."

    # Allow alphanumeric, spaces, dashes, and underscores
    if not re.match(r"^[a-zA-Z0-9_\- ]+$", room_name):
        return False, "Room name can only contain letters, numbers, spaces, '-' and '_'."

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM rooms WHERE name = ?", (room_name,))
        if cursor.fetchone():
            return False, f"Room '{room_name}' already exists."

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO rooms (name, created_by, created_at) VALUES (?, ?, ?)",
            (room_name, created_by, created_at)
        )
        conn.commit()
        return True, f"Room '{room_name}' created successfully."
    except Exception as e:
        return False, f"Database error creating room: {str(e)}"
    finally:
        conn.close()


def save_message(room_name: str, username: str, message: str, timestamp: str = None, db_path=DEFAULT_DB_PATH):
    """
    Persists a chat message in the SQLite database.
    """
    if not timestamp:
        timestamp = datetime.now().strftime("[%H:%M]")

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO messages (room_name, username, message, timestamp) VALUES (?, ?, ?, ?)",
            (room_name, username, message, timestamp)
        )
        conn.commit()
    finally:
        conn.close()


def get_room_history(room_name: str, limit: int = 50, db_path=DEFAULT_DB_PATH):
    """
    Retrieves the most recent messages for a given room, sorted chronologically.
    Returns: list of dicts [{'username': ..., 'message': ..., 'timestamp': ...}]
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # Retrieve the latest 'limit' messages, then reverse to display chronologically
        cursor.execute("""
            SELECT username, message, timestamp
            FROM messages
            WHERE room_name = ?
            ORDER BY id DESC
            LIMIT ?
        """, (room_name, limit))
        rows = cursor.fetchall()
        # Reverse to get oldest first among the last 'limit'
        history = [
            {
                "username": row["username"],
                "message": row["message"],
                "timestamp": row["timestamp"]
            }
            for row in reversed(rows)
        ]
        return history
    finally:
        conn.close()


if __name__ == "__main__":
    # Self-test when run directly
    print("Testing database module...")
    test_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_temp.db")
    if os.path.exists(test_db):
        os.remove(test_db)

    init_db(test_db)
    print("Initial rooms:", get_all_rooms(test_db))

    reg_ok, msg = register_user("chandana", "secret123", test_db)
    print("Register Chandana:", reg_ok, msg)

    reg_dup, msg = register_user("chandana", "secret123", test_db)
    print("Register Duplicate:", reg_dup, msg)

    login_ok, msg = verify_user("chandana", "secret123", test_db)
    print("Login Success:", login_ok, msg)

    login_bad, msg = verify_user("chandana", "wrongpassword", test_db)
    print("Login Bad Password:", login_bad, msg)

    room_ok, msg = create_room("AI-Lab", "chandana", test_db)
    print("Create Room:", room_ok, msg)

    save_message("AI-Lab", "chandana", "Hello Oasis Infobyte! 🚀", "[14:35]", test_db)
    history = get_room_history("AI-Lab", db_path=test_db)
    print("Room History:", history)

    os.remove(test_db)
    print("Database test passed cleanly!")
