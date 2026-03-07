"""Database module for Consumables & Toners Tracking"""

import sqlite3
from datetime import datetime

DATABASE = 'tracking_dashboard.db'


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    create_users_table()
    create_consumables_table()
    create_toners_table()
    create_activities_table()
    # Add p3_it_cage column if it doesn't exist
    add_p3_it_cage_column()


def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        password TEXT DEFAULT '',
        department TEXT DEFAULT 'IT',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()


def create_consumables_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS consumables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        category TEXT NOT NULL,
        p1_it_cage INTEGER DEFAULT 0,
        hrv_backside INTEGER DEFAULT 0,
        rf_cage INTEGER DEFAULT 0,
        p3_it_cage INTEGER DEFAULT 0,
        min_stock_level INTEGER DEFAULT 5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()


def create_toners_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS toners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        printer_model TEXT NOT NULL,
        printer_count INTEGER DEFAULT 0,
        toner_model TEXT NOT NULL,
        color TEXT DEFAULT 'Black',
        p1_it_cage INTEGER DEFAULT 0,
        hrv_backside INTEGER DEFAULT 0,
        rf_cage INTEGER DEFAULT 0,
        p3_it_cage INTEGER DEFAULT 0,
        min_stock_level INTEGER DEFAULT 2,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()


def add_p3_it_cage_column():
    """Add p3_it_cage column to existing tables if not exists"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if p3_it_cage exists in consumables
    cursor.execute("PRAGMA table_info(consumables)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'p3_it_cage' not in columns:
        cursor.execute('ALTER TABLE consumables ADD COLUMN p3_it_cage INTEGER DEFAULT 0')
    
    # Check if p3_it_cage exists in toners
    cursor.execute("PRAGMA table_info(toners)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'p3_it_cage' not in columns:
        cursor.execute('ALTER TABLE toners ADD COLUMN p3_it_cage INTEGER DEFAULT 0')
    
    conn.commit()
    conn.close()


def create_activities_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item_type TEXT NOT NULL,
        item_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        action_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        notes TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()


def add_user(username, full_name, department='IT', password=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, full_name, department, password) VALUES (?, ?, ?, ?)',
                   (username, full_name, department, password))
    conn.commit()
    conn.close()


def update_user_password(user_id, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE id = ?', (password, user_id))
    conn.commit()
    conn.close()


def update_user_details(user_id, full_name, username, department):
    """Update user details"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET full_name = ?, username = ?, department = ? WHERE id = ?', 
                   (full_name, username, department, user_id))
    conn.commit()
    conn.close()


def delete_user(user_id):
    """Delete a user from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


def verify_user_password(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def set_consumable_stock(item_id, location, new_value):
    conn = get_connection()
    cursor = conn.cursor()
    loc_col = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
    col = loc_col.get(location, 'p1_it_cage')
    cursor.execute(f'UPDATE consumables SET {col} = ? WHERE id = ?', (new_value, item_id))
    conn.commit()
    conn.close()


def set_toner_stock(item_id, location, new_value):
    conn = get_connection()
    cursor = conn.cursor()
    loc_col = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
    col = loc_col.get(location, 'p1_it_cage')
    cursor.execute(f'UPDATE toners SET {col} = ? WHERE id = ?', (new_value, item_id))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY full_name')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def add_consumable(item_name, category, p1_it_cage=0, hrv_backside=0, rf_cage=0, p3_it_cage=0, min_stock_level=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO consumables (item_name, category, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (item_name, category, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level))
    conn.commit()
    conn.close()


def get_all_consumables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT *, (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) as total_stock FROM consumables ORDER BY category, item_name')
    consumables = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return consumables


def update_consumable_stock(item_id, location, quantity_change):
    conn = get_connection()
    cursor = conn.cursor()
    loc_col = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
    col = loc_col.get(location, 'p1_it_cage')
    cursor.execute(f'UPDATE consumables SET {col} = {col} + ? WHERE id = ?', (quantity_change, item_id))
    conn.commit()
    conn.close()


def get_low_stock_consumables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT *, (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) as total_stock FROM consumables WHERE (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) <= min_stock_level')
    consumables = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return consumables


def get_consumable_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total_items, COALESCE(SUM(p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)), 0) as total_stock, COALESCE(SUM(p1_it_cage), 0) as p1_it_cage, COALESCE(SUM(hrv_backside), 0) as hrv_backside, COALESCE(SUM(rf_cage), 0) as rf_cage, COALESCE(SUM(p3_it_cage), 0) as p3_it_cage, COUNT(DISTINCT category) as categories FROM consumables')
    stats = dict(cursor.fetchone())
    cursor.execute('SELECT COUNT(*) as low_stock FROM consumables WHERE (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) <= min_stock_level')
    stats['low_stock_count'] = cursor.fetchone()['low_stock']
    conn.close()
    return stats


def add_toner(printer_model, printer_count, toner_model, color, p1_it_cage=0, hrv_backside=0, rf_cage=0, p3_it_cage=0, min_stock_level=2):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO toners (printer_model, printer_count, toner_model, color, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (printer_model, printer_count, toner_model, color, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level))
    conn.commit()
    conn.close()


def get_all_toners():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT *, (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) as total_stock FROM toners ORDER BY printer_model')
    toners = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return toners


def update_toner_stock(item_id, location, quantity_change):
    conn = get_connection()
    cursor = conn.cursor()
    loc_col = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
    col = loc_col.get(location, 'p1_it_cage')
    cursor.execute(f'UPDATE toners SET {col} = {col} + ? WHERE id = ?', (quantity_change, item_id))
    conn.commit()
    conn.close()


def get_low_stock_toners():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT *, (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) as total_stock FROM toners WHERE (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) <= min_stock_level')
    toners = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return toners


def get_toner_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total_items, COALESCE(SUM(p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)), 0) as total_stock, COALESCE(SUM(p1_it_cage), 0) as p1_it_cage, COALESCE(SUM(hrv_backside), 0) as hrv_backside, COALESCE(SUM(rf_cage), 0) as rf_cage, COALESCE(SUM(p3_it_cage), 0) as p3_it_cage FROM toners')
    stats = dict(cursor.fetchone())
    cursor.execute('SELECT COUNT(*) as low_stock FROM toners WHERE (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) <= min_stock_level')
    stats['low_stock_count'] = cursor.fetchone()['low_stock']
    conn.close()
    return stats


def log_activity(user_id, item_type, item_id, item_name, action_type, quantity, notes=''):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO activities (user_id, item_type, item_id, item_name, action_type, quantity, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (user_id, item_type, item_id, item_name, action_type, quantity, notes))
    conn.commit()
    conn.close()


def get_recent_activities(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT a.*, u.full_name as user_name FROM activities a LEFT JOIN users u ON a.user_id = u.id ORDER BY a.timestamp DESC LIMIT ?', (limit,))
    activities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return activities


def get_activities_by_item(item_type, item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT a.*, u.full_name as user_name FROM activities a LEFT JOIN users u ON a.user_id = u.id WHERE a.item_type = ? AND a.item_id = ? ORDER BY a.timestamp DESC', (item_type, item_id))
    activities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return activities


def get_user_activity_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT u.full_name, u.department, COUNT(a.id) as total_activities, SUM(CASE WHEN a.action_type = "Pick" THEN 1 ELSE 0 END) as total_picks, SUM(CASE WHEN a.action_type = "Stow" THEN 1 ELSE 0 END) as total_stows FROM users u LEFT JOIN activities a ON u.id = a.user_id GROUP BY u.id ORDER BY total_activities DESC')
    summary = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return summary


def insert_sample_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM users')
    if cursor.fetchone()['count'] == 0:
        admin_users = [
            ('gmanisel', 'Maniselvam G', 'IT', 'MAA4@123'),
            ('saswith', 'Aswitha S', 'IT', 'MAA4@123'),
            ('ddink', 'Dinesh Kumar', 'IT', 'MAA4@123'),
        ]
        regular_users = [
            ('raghumun', 'Munusamy R', 'IT', ''),
            ('Gksanjay', 'Sanjay', 'IT', ''),
            ('Sriajayk', 'Ajay', 'IT', ''),
            ('sababuka', 'Sathish B', 'IT', ''),
            ('ilayaram', 'Ilayabharathi P', 'IT', ''),
            ('Karthik', 'parumk', 'IT', '')
        ]
        for user in admin_users + regular_users:
            cursor.execute('INSERT INTO users (username, full_name, department, password) VALUES (?, ?, ?, ?)', user)
    
    cursor.execute('SELECT COUNT(*) as count FROM consumables')
    if cursor.fetchone()['count'] == 0:
        consumables = [
            ('Walkie Talkie Adaptor', 'Adapters', 5, 0, 0, 0, 2),
            ('Bluetooth Scanner', 'Scanners', 6, 0, 0, 0, 3),
            ('DP Cable', 'Cables', 166, 0, 0, 0, 20),
            ('Thin Client Power Adaptor', 'Adapters', 77, 0, 0, 0, 10),
            ('VGA Cable', 'Cables', 31, 0, 0, 0, 5),
            ('Keyboard', 'Peripherals', 28, 0, 0, 0, 5),
            ('LAN Cable', 'Cables', 117, 0, 0, 0, 15),
            ('Mouse', 'Peripherals', 13, 0, 0, 0, 5),
            ('HDMI Cable', 'Cables', 140, 0, 0, 0, 20),
            ('Symbol Scanner USB Cable', 'Cables', 6, 0, 0, 0, 3),
            ('Printer Power Cable', 'Cables', 42, 0, 0, 0, 5),
            ('Thin Client Power Cable', 'Cables', 113, 0, 0, 0, 15),
            ('Laptop Charger', 'Power', 18, 0, 0, 0, 5),
            ('ZT620 & GX430 Power Adaptor', 'Adapters', 36, 0, 0, 0, 5),
            ('Printer USB Cable', 'Cables', 39, 0, 0, 0, 5),
            ('IO', 'Accessories', 44, 0, 0, 0, 5),
            ('Fiber Cable', 'Cables', 74, 0, 0, 0, 10),
            ('Console Cable', 'Cables', 27, 0, 0, 0, 5),
            ('Desk Phone', 'Peripherals', 1, 0, 0, 0, 1),
            ('Bluetooth Scanner Cable', 'Cables', 31, 0, 0, 0, 5),
            ('Switch 3 Pin Power Cable', 'Cables', 20, 0, 0, 0, 5),
            ('Bluetooth Scanner Cradle', 'Scanners', 19, 0, 0, 0, 5),
            ('External AP', 'Network', 2, 0, 0, 0, 2),
            ('Internal AP', 'Network', 6, 0, 0, 0, 3),
            ('Lan Adaptor', 'Adapters', 6, 0, 0, 0, 3),
            ('USB HUB', 'Accessories', 150, 0, 0, 0, 20),
            ('HDMI to DP', 'Adapters', 16, 0, 0, 0, 5),
            ('HDMI to VGA', 'Adapters', 3, 0, 0, 0, 2),
            ('DP to VGA', 'Adapters', 6, 0, 0, 0, 3)
        ]
        for item in consumables:
            cursor.execute('INSERT INTO consumables (item_name, category, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level) VALUES (?, ?, ?, ?, ?, ?, ?)', item)
    
    cursor.execute('SELECT COUNT(*) as count FROM toners')
    if cursor.fetchone()['count'] == 0:
        toners = [
            ('LaserJet Pro MFP M521dn', 5, 'CE255XC', 'Black', 3, 0, 4, 0, 2),
            ('LaserJet M608', 6, 'CF237YC', 'Black', 0, 13, 0, 0, 3),
            ('LaserJet flow MFP M830', 2, 'CF325XC', 'Black', 5, 12, 0, 0, 3),
            ('LaserJet M605', 5, 'CF281XC', 'Black', 6, 4, 0, 0, 2),
            ('LaserJet MFP E82560', 1, 'W9037MC', 'Black', 7, 0, 0, 0, 2),
            ('LaserJet MFP M427fdw', 3, 'CF228XC', 'Black', 1, 8, 4, 0, 2),
            ('LaserJet 700 color MFP M775', 2, 'CE340AC - K', 'Black', 4, 4, 3, 0, 2),
            ('LaserJet 700 color MFP M775', 2, 'CE341AC - C', 'Cyan', 8, 7, 0, 0, 2),
            ('LaserJet 700 color MFP M775', 2, 'CE342AC - Y', 'Yellow', 0, 6, 3, 0, 2),
            ('LaserJet 700 color MFP M775', 2, 'CE343AC - M', 'Magenta', 6, 5, 4, 0, 2),
            ('LaserJet Enterprise M611dn', 3, 'W1470YC', 'Black', 2, 4, 4, 0, 2)
        ]
        for item in toners:
            cursor.execute('INSERT INTO toners (printer_model, printer_count, toner_model, color, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', item)
    
    conn.commit()
    conn.close()