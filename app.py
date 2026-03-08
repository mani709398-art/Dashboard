"""
Consumables & Toners Tracking Dashboard
HYBRID APPROACH: Local session for speed, periodic cloud sync
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import database as db

st.set_page_config(page_title="🖥️ IT Inventory Dashboard", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
<style>
    .stApp { background: #1a1a2e !important; }
    .main .block-container { background: #1a1a2e !important; padding: 1rem 2rem; max-width: 1200px; }
    .main-header { color: #ffffff !important; font-size: 2rem; font-weight: 700; }
    .sub-header { color: #00b894 !important; font-size: 1rem; margin-bottom: 0.8rem; }
    [data-testid="stSidebar"] { background: #1a2744; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p { color: #ffffff !important; }
    [data-testid="stSidebar"] .stMarkdown h3 { color: #f39c12 !important; }
    .metric-card { background: linear-gradient(135deg, #1a2744 0%, #2d3a4a 100%); border-radius: 12px; padding: 15px 20px; margin-bottom: 10px; }
    .metric-label { color: #ffffff; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; margin-bottom: 8px; }
    .metric-value { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .metric-value-green { color: #00b894; } .metric-value-blue { color: #0984e3; } .metric-value-orange { color: #f39c12; }
    .metric-value-red { color: #e74c3c; } .metric-value-purple { color: #9b59b6; } .metric-value-dark { color: #ffffff; }
    .live-badge { background: #00b894; color: white; padding: 8px 20px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }
    .content-card { background: #16213e !important; border-radius: 12px; padding: 18px; margin-bottom: 12px; }
    .low-stock-alert { background: #3d2a2a; border-left: 4px solid #e74c3c; padding: 12px 18px; margin: 8px 0; border-radius: 0 8px 8px 0; color: #ffffff; }
    .stButton > button { background: #f39c12; color: white; border: none; padding: 10px 25px; border-radius: 8px; font-weight: 600; }
    .stButton > button:hover { background: #e67e22; }
    .stTabs [data-baseweb="tab"] { background: #2d3a4a; border-radius: 8px; padding: 12px 24px; font-weight: 600; color: #ffffff; }
    .stTabs [aria-selected="true"] { background: #0984e3; }
    .styled-table { width: 100%; border-collapse: collapse; background: #2d3a4a; border-radius: 8px; }
    .styled-table thead tr { background: #1a2744; color: white; }
    .styled-table th { padding: 15px; font-weight: 600; text-align: center; font-size: 0.85rem; text-transform: uppercase; }
    .styled-table td { padding: 12px 15px; text-align: center; border-bottom: 1px solid #3d4a5a; color: #ffffff; }
    h4, h3, h2, h1 { color: #ffffff !important; }
    .section-title-alert { color: #ff6b6b !important; }
    .last-updated { color: #aaa !important; font-size: 0.85rem; }
    header[data-testid="stHeader"] { background: #1a1a2e !important; }
    .main label, .main [data-testid="stWidgetLabel"] p { color: #ffffff !important; }
    .main [data-baseweb="select"] > div, .stSelectbox > div > div { background: #2d3a4a !important; border: 2px solid #f39c12 !important; border-radius: 8px !important; }
    .main [data-baseweb="select"] span, .stSelectbox span { color: #ffffff !important; font-weight: 700 !important; }
    .stNumberInput > div > div > input { background: #2d3a4a !important; color: #ffffff !important; border: 2px solid #f39c12 !important; }
    [data-baseweb="popover"] li { background: white !important; color: #1a2744 !important; }
    .stDeployButton, #MainMenu { display: none !important; }
    .sync-status { background: #2d3a4a; padding: 5px 10px; border-radius: 5px; font-size: 0.75rem; color: #00b894; }
</style>
""", unsafe_allow_html=True)

# Session state
if 'logged_in_user' not in st.session_state: st.session_state.logged_in_user = None
if 'success_msg' not in st.session_state: st.session_state.success_msg = None
if 'data_loaded' not in st.session_state: st.session_state.data_loaded = False
if 'pending_changes' not in st.session_state: st.session_state.pending_changes = []
if 'last_sync' not in st.session_state: st.session_state.last_sync = None

# Load cloud data once
@st.cache_data(ttl=600, show_spinner="Loading data...")
def load_cloud_data():
    db.init_database()
    db.insert_sample_data()
    return {'users': db.get_all_users(), 'consumables': db.get_all_consumables(), 'toners': db.get_all_toners(), 'activities': db.get_recent_activities(100)}

def init_local_data():
    if not st.session_state.data_loaded:
        data = load_cloud_data()
        st.session_state.local_users = list(data['users'])
        st.session_state.local_consumables = list(data['consumables'])
        st.session_state.local_toners = list(data['toners'])
        st.session_state.local_activities = list(data['activities'])
        st.session_state.last_sync = datetime.now()
        st.session_state.data_loaded = True

init_local_data()

# Local data access
def get_users(): return st.session_state.local_users
def get_consumables(): return st.session_state.local_consumables
def get_toners(): return st.session_state.local_toners
def get_activities(): return st.session_state.local_activities
def get_user_by_id(uid): return next((u for u in st.session_state.local_users if u['id'] == uid), None)
def is_user_admin(uid): u = get_user_by_id(uid); return bool(u.get('is_admin', False)) if u else False

# Local operations (instant)
def local_update_stock(item_type, item_id, location, qty_change):
    loc_map = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
    col = loc_map.get(location, 'p1_it_cage')
    items = st.session_state.local_consumables if item_type == 'consumable' else st.session_state.local_toners
    for item in items:
        if item['id'] == item_id:
            item[col] = item.get(col, 0) + qty_change
            item['total_stock'] = item['p1_it_cage'] + item['hrv_backside'] + item['rf_cage'] + item.get('p3_it_cage', 0)
            break
    st.session_state.pending_changes.append({'type': f'{item_type}_stock', 'item_id': item_id, 'location': location, 'qty': qty_change})

def local_log_activity(user_id, item_type, item_id, item_name, action, qty, before, after):
    user = get_user_by_id(user_id)
    st.session_state.local_activities.insert(0, {'id': 1000+len(st.session_state.local_activities), 'user_id': user_id, 'user_name': user['full_name'] if user else '', 'item_type': item_type, 'item_id': item_id, 'item_name': item_name, 'action_type': action, 'quantity': qty, 'before_count': before, 'after_count': after, 'notes': '', 'timestamp': datetime.now()})
    st.session_state.pending_changes.append({'type': 'activity', 'data': {'user_id': user_id, 'item_type': item_type, 'item_id': item_id, 'item_name': item_name, 'action_type': action, 'quantity': qty, 'before_count': before, 'after_count': after, 'notes': ''}})

def local_update_password(user_id, pwd):
    for u in st.session_state.local_users:
        if u['id'] == user_id: u['password'] = pwd; break
    st.session_state.pending_changes.append({'type': 'password', 'user_id': user_id, 'password': pwd})

# Cloud sync
def sync_to_cloud():
    synced = 0
    for c in st.session_state.pending_changes[:]:
        try:
            if c['type'] == 'consumable_stock': db.update_consumable_stock(c['item_id'], c['location'], c['qty']); synced += 1
            elif c['type'] == 'toner_stock': db.update_toner_stock(c['item_id'], c['location'], c['qty']); synced += 1
            elif c['type'] == 'activity': d = c['data']; db.log_activity(d['user_id'], d['item_type'], d['item_id'], d['item_name'], d['action_type'], d['quantity'], d['notes'], d['before_count'], d['after_count']); synced += 1
            elif c['type'] == 'password': db.update_user_password(c['user_id'], c['password']); synced += 1
            st.session_state.pending_changes.remove(c)
        except: pass
    if synced > 0: st.session_state.last_sync = datetime.now()
    return synced

# Auto-sync every 60 seconds
if st.session_state.last_sync and (datetime.now() - st.session_state.last_sync).total_seconds() > 60 and st.session_state.pending_changes:
    sync_to_cloud()

# Stats
def get_consumable_stats():
    c = get_consumables()
    return {'total_items': len(c), 'total_stock': sum(x.get('total_stock', 0) for x in c), 'p1_it_cage': sum(x.get('p1_it_cage', 0) for x in c), 'hrv_backside': sum(x.get('hrv_backside', 0) for x in c), 'rf_cage': sum(x.get('rf_cage', 0) for x in c), 'p3_it_cage': sum(x.get('p3_it_cage', 0) for x in c), 'categories': len(set(x.get('category', '') for x in c)), 'low_stock_count': sum(1 for x in c if x.get('total_stock', 0) <= x.get('min_stock_level', 5))}

def get_toner_stats():
    t = get_toners()
    return {'total_items': len(t), 'total_stock': sum(x.get('total_stock', 0) for x in t), 'p1_it_cage': sum(x.get('p1_it_cage', 0) for x in t), 'hrv_backside': sum(x.get('hrv_backside', 0) for x in t), 'rf_cage': sum(x.get('rf_cage', 0) for x in t), 'p3_it_cage': sum(x.get('p3_it_cage', 0) for x in t), 'low_stock_count': sum(1 for x in t if x.get('total_stock', 0) <= x.get('min_stock_level', 2))}

# Toast
if st.session_state.success_msg: st.toast(st.session_state.success_msg, icon="✅"); st.session_state.success_msg = None

def create_metric_card(label, value, color="metric-value-dark"):
    return f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value {color}">{value}</div></div>'

# Login
def login_section():
    users = get_users()
    if st.session_state.logged_in_user:
        user = get_user_by_id(st.session_state.logged_in_user)
        is_admin = is_user_admin(st.session_state.logged_in_user)
        color = "#f39c12" if is_admin else "#00b894"
        st.sidebar.markdown(f'<div style="background: {color}; border-radius: 10px; padding: 12px; color: white; margin-bottom: 10px;"><div style="font-weight: 700;">👤 {user["full_name"]}</div><div style="font-size: 0.85rem;">@{user["username"]} | {"Admin" if is_admin else "User"}</div></div>', unsafe_allow_html=True)
        
        pending = len(st.session_state.pending_changes)
        st.sidebar.markdown(f'<div class="sync-status">{"⏳ "+str(pending)+" pending" if pending else "✅ Synced"}</div>', unsafe_allow_html=True)
        if pending and st.sidebar.button("🔄 Sync Now"): sync_to_cloud(); st.toast("✅ Synced!")
        
        with st.sidebar.expander("🔑 Change Password"):
            pwd1, pwd2 = st.text_input("New Password", type="password", key="p1"), st.text_input("Confirm", type="password", key="p2")
            if st.button("Update", key="upd_pwd") and pwd1 == pwd2 and pwd1: local_update_password(st.session_state.logged_in_user, pwd1); st.success("✅ Updated!")
        
        if st.sidebar.button("🚪 Logout"): sync_to_cloud(); st.session_state.logged_in_user = None; st.rerun()
        
        if is_admin:
            with st.sidebar.expander("🔧 Admin"):
                action = st.radio("", ["Set Password", "Sync", "Reload"], label_visibility="collapsed")
                if action == "Set Password":
                    sel = st.selectbox("User", [u['full_name'] for u in users])
                    pwd = st.text_input("Password", type="password", key="apwd")
                    if st.button("Set") and pwd: u = next((x for x in users if x['full_name'] == sel), None); u and local_update_password(u['id'], pwd); st.success("✅")
                elif action == "Sync" and st.button("🔄 Sync"): st.success(f"✅ {sync_to_cloud()} synced")
                elif action == "Reload" and st.button("🔄 Reload"): st.cache_data.clear(); st.session_state.data_loaded = False; st.rerun()
    else:
        st.sidebar.markdown("### 👤 Login")
        admins, regulars = [u for u in users if u.get('is_admin')], [u for u in users if not u.get('is_admin')]
        login_type = st.sidebar.radio("", ["Admin", "User"], horizontal=True, label_visibility="collapsed")
        if login_type == "Admin" and admins:
            sel = st.sidebar.selectbox("", [u['full_name'] for u in admins], label_visibility="collapsed")
            pwd = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("🔐 Login", type="primary"):
                u = next((x for x in admins if x['full_name'] == sel), None)
                if u and u['password'] == pwd: st.session_state.logged_in_user = u['id']; st.rerun()
                else: st.sidebar.error("❌ Invalid!")
        elif login_type == "User" and regulars:
            sel = st.sidebar.selectbox("", [u['full_name'] for u in regulars], label_visibility="collapsed")
            u = next((x for x in regulars if x['full_name'] == sel), None)
            if u and u.get('password'):
                pwd = st.sidebar.text_input("Password", type="password")
                if st.sidebar.button("🔐 Login", type="primary"): 
                    if u['password'] == pwd: st.session_state.logged_in_user = u['id']; st.rerun()
                    else: st.sidebar.error("❌ Invalid!")
            elif st.sidebar.button("🔐 Login", type="primary"): st.session_state.logged_in_user = u['id']; st.rerun()

def consumables_dashboard():
    st.markdown('<div class="main-header">🏭 Consumables Inventory</div>', unsafe_allow_html=True)
    stats, consumables = get_consumable_stats(), get_consumables()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(create_metric_card("ITEMS", stats['total_items'], "metric-value-blue"), unsafe_allow_html=True)
    c2.markdown(create_metric_card("STOCK", stats['total_stock'], "metric-value-dark"), unsafe_allow_html=True)
    c3.markdown(create_metric_card("LOW", stats['low_stock_count'], "metric-value-red"), unsafe_allow_html=True)
    c4.markdown(create_metric_card("CATEGORIES", stats['categories'], "metric-value-purple"), unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Inventory", "🔄 Pick/Stow", "📜 History"])
    with tab1:
        df = pd.DataFrame(consumables)
        if not df.empty:
            df['S.No'] = range(1, len(df) + 1)
            if 'p3_it_cage' not in df.columns: df['p3_it_cage'] = 0
            disp = df[['S.No', 'item_name', 'category', 'p1_it_cage', 'hrv_backside', 'rf_cage', 'p3_it_cage', 'total_stock']].copy()
            disp.columns = ['S.No', 'Item', 'Category', 'P1', 'HRV', 'RF', 'P3', 'Total']
            for c in ['P1', 'HRV', 'RF', 'P3']: disp[c] = disp[c].apply(lambda x: '-' if x == 0 else x)
            st.markdown(disp.to_html(index=False, classes='styled-table'), unsafe_allow_html=True)
    
    with tab2:
        if not st.session_state.logged_in_user: st.warning("⚠️ Please login")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 📤 Pick")
                item = st.selectbox("Item", [c['item_name'] for c in consumables], key="pc_item")
                loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage", "P3 IT Cage"], key="pc_loc")
                qty = st.number_input("Qty", min_value=1, value=1, key="pc_qty")
                if st.button("📤 Pick", key="pc_btn"):
                    i = next((c for c in consumables if c['item_name'] == item), None)
                    if i:
                        loc_map = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
                        before = i.get(loc_map[loc], 0)
                        if before >= qty:
                            local_update_stock('consumable', i['id'], loc, -qty)
                            local_log_activity(st.session_state.logged_in_user, "Consumable", i['id'], f"{i['item_name']} ({loc})", "Pick", qty, before, before-qty)
                            st.session_state.success_msg = f"✅ Picked {qty} x {item}"
                            st.rerun()
                        else: st.error("❌ Insufficient stock!")
            with c2:
                st.markdown("#### 📥 Stow")
                item = st.selectbox("Item", [c['item_name'] for c in consumables], key="sc_item")
                loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage", "P3 IT Cage"], key="sc_loc")
                qty = st.number_input("Qty", min_value=1, value=1, key="sc_qty")
                if st.button("📥 Stow", key="sc_btn"):
                    i = next((c for c in consumables if c['item_name'] == item), None)
                    if i:
                        loc_map = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
                        before = i.get(loc_map[loc], 0)
                        local_update_stock('consumable', i['id'], loc, qty)
                        local_log_activity(st.session_state.logged_in_user, "Consumable", i['id'], f"{i['item_name']} ({loc})", "Stow", qty, before, before+qty)
                        st.session_state.success_msg = f"✅ Stowed {qty} x {item}"
                        st.rerun()
    
    with tab3:
        acts = [a for a in get_activities() if a['item_type'] == 'Consumable']
        if acts:
            df = pd.DataFrame(acts)
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df[['timestamp', 'user_name', 'item_name', 'action_type', 'quantity', 'before_count', 'after_count']], use_container_width=True, hide_index=True)
        else: st.info("No history yet")

def toner_dashboard():
    st.markdown('<div class="main-header">🖨️ Toner Inventory</div>', unsafe_allow_html=True)
    stats, toners = get_toner_stats(), get_toners()
    c1, c2, c3 = st.columns(3)
    c1.markdown(create_metric_card("TYPES", stats['total_items'], "metric-value-blue"), unsafe_allow_html=True)
    c2.markdown(create_metric_card("STOCK", stats['total_stock'], "metric-value-dark"), unsafe_allow_html=True)
    c3.markdown(create_metric_card("LOW", stats['low_stock_count'], "metric-value-red"), unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Inventory", "🔄 Pick/Stow", "📜 History"])
    with tab1:
        df = pd.DataFrame(toners)
        if not df.empty:
            df['S.No'] = range(1, len(df) + 1)
            if 'p3_it_cage' not in df.columns: df['p3_it_cage'] = 0
            disp = df[['S.No', 'printer_model', 'toner_model', 'color', 'p1_it_cage', 'hrv_backside', 'rf_cage', 'p3_it_cage', 'total_stock']].copy()
            disp.columns = ['S.No', 'Printer', 'Toner', 'Color', 'P1', 'HRV', 'RF', 'P3', 'Total']
            for c in ['P1', 'HRV', 'RF', 'P3']: disp[c] = disp[c].apply(lambda x: '-' if x == 0 else x)
            st.markdown(disp.to_html(index=False, classes='styled-table'), unsafe_allow_html=True)
    
    with tab2:
        if not st.session_state.logged_in_user: st.warning("⚠️ Please login")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 📤 Pick")
                item = st.selectbox("Toner", [f"{t['toner_model']} - {t['printer_model']}" for t in toners], key="pt_item")
                loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage", "P3 IT Cage"], key="pt_loc")
                qty = st.number_input("Qty", min_value=1, value=1, key="pt_qty")
                if st.button("📤 Pick", key="pt_btn"):
                    toner_model = item.split(" - ")[0]
                    i = next((t for t in toners if t['toner_model'] == toner_model), None)
                    if i:
                        loc_map = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
                        before = i.get(loc_map[loc], 0)
                        if before >= qty:
                            local_update_stock('toner', i['id'], loc, -qty)
                            local_log_activity(st.session_state.logged_in_user, "Toner", i['id'], f"{i['toner_model']} ({loc})", "Pick", qty, before, before-qty)
                            st.session_state.success_msg = f"✅ Picked {qty} x {toner_model}"
                            st.rerun()
                        else: st.error("❌ Insufficient stock!")
            with c2:
                st.markdown("#### 📥 Stow")
                item = st.selectbox("Toner", [f"{t['toner_model']} - {t['printer_model']}" for t in toners], key="st_item")
                loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage", "P3 IT Cage"], key="st_loc")
                qty = st.number_input("Qty", min_value=1, value=1, key="st_qty")
                if st.button("📥 Stow", key="st_btn"):
                    toner_model = item.split(" - ")[0]
                    i = next((t for t in toners if t['toner_model'] == toner_model), None)
                    if i:
                        loc_map = {'P1 IT Cage': 'p1_it_cage', 'HRV Backside': 'hrv_backside', 'RF Cage': 'rf_cage', 'P3 IT Cage': 'p3_it_cage'}
                        before = i.get(loc_map[loc], 0)
                        local_update_stock('toner', i['id'], loc, qty)
                        local_log_activity(st.session_state.logged_in_user, "Toner", i['id'], f"{i['toner_model']} ({loc})", "Stow", qty, before, before+qty)
                        st.session_state.success_msg = f"✅ Stowed {qty} x {toner_model}"
                        st.rerun()
    
    with tab3:
        acts = [a for a in get_activities() if a['item_type'] == 'Toner']
        if acts:
            df = pd.DataFrame(acts)
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df[['timestamp', 'user_name', 'item_name', 'action_type', 'quantity', 'before_count', 'after_count']], use_container_width=True, hide_index=True)
        else: st.info("No history yet")

def activity_dashboard():
    st.markdown('<div class="main-header">📋 Activity Log</div>', unsafe_allow_html=True)
    acts = get_activities()
    c1, c2, c3 = st.columns(3)
    c1.markdown(create_metric_card("TOTAL", len(acts), "metric-value-blue"), unsafe_allow_html=True)
    c2.markdown(create_metric_card("PICKS", sum(1 for a in acts if a['action_type'] == 'Pick'), "metric-value-red"), unsafe_allow_html=True)
    c3.markdown(create_metric_card("STOWS", sum(1 for a in acts if a['action_type'] == 'Stow'), "metric-value-green"), unsafe_allow_html=True)
    
    if acts:
        df = pd.DataFrame(acts)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df[['timestamp', 'user_name', 'item_type', 'item_name', 'action_type', 'quantity', 'before_count', 'after_count']], use_container_width=True, hide_index=True)
    else:
        st.info("No activity history yet")

def main():
    login_section()
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📑 Navigation")
    page = st.sidebar.radio("", ["📦 Consumables", "🖨️ Toners", "📋 Activity Log"], label_visibility="collapsed")
    
    if page == "📦 Consumables":
        consumables_dashboard()
    elif page == "🖨️ Toners":
        toner_dashboard()
    else:
        activity_dashboard()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div style="text-align: center; color: #888; font-size: 0.8rem;">IT Inventory v2.0</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
