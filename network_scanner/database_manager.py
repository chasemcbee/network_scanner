import os
import sqlite3

# Create a folder to hold all .db files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FOLDER = os.path.join(BASE_DIR, 'databases')
os.makedirs(DATABASE_FOLDER, exist_ok=True)

# Default active DB (can be changed by user in GUI)
_active_db_path = os.path.join(DATABASE_FOLDER, 'default.db')
if not os.path.exists(_active_db_path):
    conn = sqlite3.connect(_active_db_path)
    conn.close()

def list_databases():
    """List all .db files in the databases folder"""
    return [f for f in os.listdir(DATABASE_FOLDER) if f.endswith('.db')]

def create_database(name):
    """Create a new .db file and set it as active"""
    global _active_db_path
    db_file = os.path.join(DATABASE_FOLDER, f"{name}.db")
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        conn.close()
    _active_db_path = db_file
    return db_file

def set_active_database_path(path):
    """Set full path to a specific database file"""
    global _active_db_path
    _active_db_path = path

def set_active_database(db_name):
    """Set an existing .db file in the folder as active"""
    global _active_db_path
    db_path = os.path.join(DATABASE_FOLDER, db_name)
    if os.path.exists(db_path):
        _active_db_path = db_path
    else:
        raise FileNotFoundError(f"Database {db_name} not found in {DATABASE_FOLDER}")

def get_active_database_path():
    """Return full path to the currently selected .db file"""
    return _active_db_path
