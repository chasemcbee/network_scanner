import os
import sqlite3

DATABASE_FOLDER = os.path.join(os.path.dirname(__file__), 'databases')
os.makedirs(DATABASE_FOLDER, exist_ok=True)

active_db_path = os.path.join(DATABASE_FOLDER, 'default.db')  # default

def list_databases():
    return [f for f in os.listdir(DATABASE_FOLDER) if f.endswith('.db')]

def create_database(name):
    global active_db_path
    db_file = os.path.join(DATABASE_FOLDER, f"{name}.db")
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        conn.close()
    active_db_path = db_file
    return db_file

def set_active_database(db_name):
    global active_db_path
    active_db_path = os.path.join(DATABASE_FOLDER, db_name)

def get_active_database_path():
    return active_db_path
