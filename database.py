"""Database module for Consumables & Toners Tracking
Supports both SQLite (local) and PostgreSQL (Supabase for production)
"""

import os
from datetime import datetime
import sqlite3

DATABASE = 'tracking_dashboard.db'


def get_database_url():
    """Get database URL from Streamlit secrets or environment"""
    # Try Streamlit secrets first
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass
    # Fallback to environment variable
    return os.environ.get("DATABASE_URL", None)


def get_connection():
    """Get database connection based on environment"""
    db_url = get_database_url()
    if db_url:
        import psycopg2
        # Supabase requires SSL
        conn = psycopg2.connect(db_url, sslmode='require')
        return conn, True  # True = PostgreSQL
    else:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn, False  # False = SQLite


def execute_query(query, params=None, fetch=False, fetch_one=False):
    """Execute a query with proper handling for both database types"""
    conn, is_postgres = get_connection()
    
    if is_postgres:
        from psycopg2.extras import RealDictCursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Convert SQLite-style ? placeholders to PostgreSQL %s
        query = query.replace('?', '%s')
    else:
        cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
            if is_postgres:
                return dict(result) if result else None
            else:
                return dict(result) if result else None
        elif fetch:
            results = cursor.fetchall()
            if is_postgres:
                return [dict(row) for row in results]
            else:
                return [dict(row) for row in results]
        else:
            conn.commit()
            return cursor.lastrowid if not is_postgres else None
    finally:
        cursor.close()
        conn.close()


def init_database():
    """Initialize all database tables"""
    create_users_table()
    create_consumables_table()
    create_toners_table()
    create_activities_table()
    # Add columns if they don't exist (for existing databases)
    add_missing_columns()


def create_users_table():
    """Create users table"""
    db_url = get_database_url()
    if db_url:
        query = '''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password TEXT DEFAULT '',
            department TEXT DEFAULT 'IT',
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
    else:
        query = '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password TEXT DEFAULT '',
            department TEXT DEFAULT 'IT',
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
    execute_query(query)


def create_consumables_table():
    """Create consumables table"""
    db_url = get_database_url()
    if db_url:
        query = '''CREATE TABLE IF NOT EXISTS consumables (
            id SERIAL PRIMARY KEY,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            p1_it_cage INTEGER DEFAULT 0,
            hrv_backside INTEGER DEFAULT 0,
            rf_cage INTEGER DEFAULT 0,
            p3_it_cage INTEGER DEFAULT 0,
            min_stock_level INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
    else:
        query = '''CREATE TABLE IF NOT EXISTS consumables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            p1_it_cage INTEGER DEFAULT 0,
            hrv_backside INTEGER DEFAULT 0,
            rf_cage INTEGER DEFAULT 0,
            p3_it_cage INTEGER DEFAULT 0,
            min_stock_level INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
    execute_query(query)


def create_toners_table():
    """Create toners table"""
    db_url = get_database_url()
    if db_url:
        query = '''CREATE TABLE IF NOT EXISTS toners (
            id SERIAL PRIMARY KEY,
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
        )'''
    else:
        query = '''CREATE TABLE IF NOT EXISTS toners (
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
        )'''
    execute_query(query)


def create_activities_table():
    """Create activities table"""
    db_url = get_database_url()
    if db_url:
        query = '''CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            action_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            before_count INTEGER DEFAULT 0,
            after_count INTEGER DEFAULT 0,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )'''
    else:
        query = '''CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            action_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            before_count INTEGER DEFAULT 0,
            after_count INTEGER DEFAULT 0,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )'''
    execute_query(query)


def add_missing_columns():
    """Add missing columns to existing tables (migration support)"""
    conn, is_postgres = get_connection()
    cursor = conn.cursor()
    
    if is_postgres:
        try:
            cursor.execute("ALTER TABLE consumables ADD COLUMN IF NOT EXISTS p3_it_cage INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE toners ADD COLUMN IF NOT EXISTS p3_it_cage INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE activities ADD COLUMN IF NOT EXISTS before_count INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE activities ADD COLUMN IF NOT EXISTS after_count INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE")
            conn.commit()
        except Exception as e:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        try:
            cursor.execute("PRAGMA table_info(consumables)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'p3_it_cage' not in columns:
                cursor.execute('ALTER TABLE consumables ADD COLUMN p3_it_cage INTEGER DEFAULT 0')
            
            cursor.execute("PRAGMA table_info(toners)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'p3_it_cage' not in columns:
                cursor.execute('ALTER TABLE toners ADD COLUMN p3_it_cage INTEGER DEFAULT 0')
            
            cursor.execute("PRAGMA table_info(activities)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'before_count' not in columns:
                cursor.execute('ALTER TABLE activities ADD COLUMN before_count INTEGER DEFAULT 0')
            if 'after_count' not in columns:
                cursor.execute('ALTER TABLE activities ADD COLUMN after_count INTEGER DEFAULT 0')
            
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'is_admin' not in columns:
                cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
            
            conn.commit()
        except Exception as e:
            pass
        finally:
            cursor.close()
            conn.close()


# ==================== USER FUNCTIONS ====================

def add_user(username, full_name, department='IT', password='', is_admin=False):
    """Add a new user"""
    db_url = get_database_url()
    if db_url:
        admin_val = is_admin
    else:
        admin_val = 1 if is_admin else 0
    query = 'INSERT INTO users (username, full_name, department, password, is_admin) VALUES (?, ?, ?, ?, ?)'
    execute_query(query, (username, full_name, department, password, admin_val))


def update_user_admin_status(user_id, is_admin):
    """Update user admin status"""
    db_url = get_database_url()
    if db_url:
        admin_val = is_admin
    else:
        admin_val = 1 if is_admin else 0
    query = 'UPDATE users SET is_admin = ? WHERE id = ?'
    execute_query(query, (admin_val, user_id))


def is_user_admin(user_id):
    """Check if user is admin"""
    user = get_user_by_id(user_id)
    if user:
        return bool(user.get('is_admin', False))
    return False


def update_user_password(user_id, password):
    """Update user password"""
    query = 'UPDATE users SET password = ? WHERE id = ?'
    execute_query(query, (password, user_id))


def update_user_details(user_id, full_name, username, department):
    """Update user details"""
    query = 'UPDATE users SET full_name = ?, username = ?, department = ? WHERE id = ?'
    execute_query(query, (full_name, username, department, user_id))


def delete_user(user_id):
    """Delete a user from the database"""
    query = 'DELETE FROM users WHERE id = ?'
    execute_query(query, (user_id,))


def verify_user_password(username, password):
    """Verify user password"""
    query = 'SELECT * FROM users WHERE username = ? AND password = ?'
    return execute_query(query, (username, password), fetch_one=True)


def get_all_users():
    """Get all users"""
    query = 'SELECT * FROM users ORDER BY full_name'
    return execute_query(query, fetch=True)


def get_user_by_id(user_id):
    """Get user by ID"""
    query = 'SELECT * FROM users WHERE id = ?'
    return execute_query(query, (user_id,), fetch_one=True)


# ==================== CONSUMABLES FUNCTIONS ====================

def add_consumable(item_name, category, p1_it_cage=0, hrv_backside=0, rf_cage=0, p3_it_cage=0, min_stock_level=5):
    """Add a new consumable item"""
    query = '''INSERT INTO consumables (item_name, category, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level) 
               VALUES (?, ?, ?, ?, ?, ?, ?)'''
    execute_query(query, (item_name, category, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level))


def get_all_consumables():
    """Get all consumables with total stock"""
    query = '''SELECT *, (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) as total_stock 
               FROM consumables ORDER BY category, item_name'''
    return execute_query(query, fetch=True)


def update_consumable_stock(item_id, location, quantity_change):
    """Update consumable stock at a location"""
    loc_col = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
    col = loc_col.get(location, 'p1_it_cage')
    query = f'UPDATE consumables SET {col} = {col} + ? WHERE id = ?'
    execute_query(query, (quantity_change, item_id))


def set_consumable_stock(item_id, location, new_value):
    """Set consumable stock to a specific value"""
    loc_col = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
    col = loc_col.get(location, 'p1_it_cage')
    query = f'UPDATE consumables SET {col} = ? WHERE id = ?'
    execute_query(query, (new_value, item_id))


def get_low_stock_consumables():
    """Get consumables with low stock"""
    query = '''SELECT *, (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) as total_stock 
               FROM consumables 
               WHERE (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) <= min_stock_level'''
    return execute_query(query, fetch=True)


def get_consumable_stats():
    """Get consumable statistics"""
    query = '''SELECT 
                COUNT(*) as total_items, 
                COALESCE(SUM(p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)), 0) as total_stock, 
                COALESCE(SUM(p1_it_cage), 0) as p1_it_cage, 
                COALESCE(SUM(hrv_backside), 0) as hrv_backside, 
                COALESCE(SUM(rf_cage), 0) as rf_cage, 
                COALESCE(SUM(p3_it_cage), 0) as p3_it_cage, 
                COUNT(DISTINCT category) as categories 
               FROM consumables'''
    stats = execute_query(query, fetch_one=True)
    if stats is None:
        stats = {'total_items': 0, 'total_stock': 0, 'p1_it_cage': 0, 'hrv_backside': 0, 'rf_cage': 0, 'p3_it_cage': 0, 'categories': 0, 'low_stock_count': 0}
        return stats
    
    low_query = '''SELECT COUNT(*) as low_stock FROM consumables 
                   WHERE (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) <= min_stock_level'''
    low_result = execute_query(low_query, fetch_one=True)
    stats['low_stock_count'] = low_result['low_stock'] if low_result else 0
    
    return stats


# ==================== TONER FUNCTIONS ====================

def add_toner(printer_model, printer_count, toner_model, color, p1_it_cage=0, hrv_backside=0, rf_cage=0, p3_it_cage=0, min_stock_level=2):
    """Add a new toner"""
    query = '''INSERT INTO toners (printer_model, printer_count, toner_model, color, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    execute_query(query, (printer_model, printer_count, toner_model, color, p1_it_cage, hrv_backside, rf_cage, p3_it_cage, min_stock_level))


def get_all_toners():
    """Get all toners with total stock"""
    query = '''SELECT *, (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) as total_stock 
               FROM toners ORDER BY printer_model'''
    return execute_query(query, fetch=True)


def update_toner_stock(item_id, location, quantity_change):
    """Update toner stock at a location"""
    loc_col = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
    col = loc_col.get(location, 'p1_it_cage')
    query = f'UPDATE toners SET {col} = {col} + ? WHERE id = ?'
    execute_query(query, (quantity_change, item_id))


def set_toner_stock(item_id, location, new_value):
    """Set toner stock to a specific value"""
    loc_col = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
    col = loc_col.get(location, 'p1_it_cage')
    query = f'UPDATE toners SET {col} = ? WHERE id = ?'
    execute_query(query, (new_value, item_id))


def get_low_stock_toners():
    """Get toners with low stock"""
    query = '''SELECT *, (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) as total_stock 
               FROM toners 
               WHERE (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) <= min_stock_level'''
    return execute_query(query, fetch=True)


def get_toner_stats():
    """Get toner statistics"""
    query = '''SELECT 
                COUNT(*) as total_items, 
                COALESCE(SUM(p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)), 0) as total_stock, 
                COALESCE(SUM(p1_it_cage), 0) as p1_it_cage, 
                COALESCE(SUM(hrv_backside), 0) as hrv_backside, 
                COALESCE(SUM(rf_cage), 0) as rf_cage, 
                COALESCE(SUM(p3_it_cage), 0) as p3_it_cage 
               FROM toners'''
    stats = execute_query(query, fetch_one=True)
    if stats is None:
        stats = {'total_items': 0, 'total_stock': 0, 'p1_it_cage': 0, 'hrv_backside': 0, 'rf_cage': 0, 'p3_it_cage': 0, 'low_stock_count': 0}
        return stats
    
    low_query = '''SELECT COUNT(*) as low_stock FROM toners 
                   WHERE (p1_it_cage + hrv_backside + rf_cage + COALESCE(p3_it_cage, 0)) <= min_stock_level'''
    low_result = execute_query(low_query, fetch_one=True)
    stats['low_stock_count'] = low_result['low_stock'] if low_result else 0
    
    return stats


# ==================== ACTIVITY FUNCTIONS ====================

def log_activity(user_id, item_type, item_id, item_name, action_type, quantity, notes='', before_count=0, after_count=0):
    """Log an activity"""
    query = '''INSERT INTO activities (user_id, item_type, item_id, item_name, action_type, quantity, before_count, after_count, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    execute_query(query, (user_id, item_type, item_id, item_name, action_type, quantity, before_count, after_count, notes))


def get_recent_activities(limit=50):
    """Get recent activities"""
    query = '''SELECT a.*, u.full_name as user_name 
               FROM activities a 
               LEFT JOIN users u ON a.user_id = u.id 
               ORDER BY a.timestamp DESC 
               LIMIT ?'''
    return execute_query(query, (limit,), fetch=True)


def get_activities_by_item(item_type, item_id):
    """Get activities for a specific item"""
    query = '''SELECT a.*, u.full_name as user_name 
               FROM activities a 
               LEFT JOIN users u ON a.user_id = u.id 
               WHERE a.item_type = ? AND a.item_id = ? 
               ORDER BY a.timestamp DESC'''
    return execute_query(query, (item_type, item_id), fetch=True)


def get_user_activity_summary():
    """Get user activity summary"""
    query = '''SELECT u.full_name, u.department, 
                COUNT(a.id) as total_activities, 
                SUM(CASE WHEN a.action_type = 'Pick' THEN 1 ELSE 0 END) as total_picks, 
                SUM(CASE WHEN a.action_type = 'Stow' THEN 1 ELSE 0 END) as total_stows 
               FROM users u 
               LEFT JOIN activities a ON u.id = a.user_id 
               GROUP BY u.id 
               ORDER BY total_activities DESC'''
    return execute_query(query, fetch=True)


# ==================== SAMPLE DATA ====================

def insert_sample_data():
    """Insert sample data if tables are empty"""
    # Check if users exist
    users = get_all_users()
    if not users or len(users) == 0:
        # Admin users with is_admin=True
        admin_users = [
            ('gmanisel', 'Maniselvam G', 'IT', 'MAA4@123', True),
            ('saswith', 'Aswitha S', 'IT', 'MAA4@123', True),
            ('ddink', 'Dinesh Kumar', 'IT', 'MAA4@123', True),
        ]
        # Regular users with is_admin=False
        regular_users = [
            ('raghumun', 'Munusamy R', 'IT', '', False),
            ('Gksanjay', 'Sanjay', 'IT', '', False),
            ('Sriajayk', 'Ajay', 'IT', '', False),
            ('sababuka', 'Sathish B', 'IT', '', False),
            ('ilayaram', 'Ilayabharathi P', 'IT', '', False),
            ('Karthik', 'parumk', 'IT', '', False)
        ]
        for user in admin_users + regular_users:
            try:
                add_user(user[0], user[1], user[2], user[3], user[4])
            except Exception as e:
                pass
    
    # Check if consumables exist
    consumables = get_all_consumables()
    if not consumables or len(consumables) == 0:
        consumables_data = [
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
        for item in consumables_data:
            try:
                add_consumable(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            except Exception as e:
                pass
    
    # Check if toners exist
    toners = get_all_toners()
    if not toners or len(toners) == 0:
        toners_data = [
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
        for item in toners_data:
            try:
                add_toner(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8])
            except Exception as e:
                pass