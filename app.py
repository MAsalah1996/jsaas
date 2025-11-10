import streamlit as st
import sqlite3

DB_NAME = "maintenance.db"

# =========================
# تهيئة قاعدة البيانات
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            role TEXT DEFAULT 'client',      -- client / technician / admin
            admin_type TEXT DEFAULT NULL,    -- super / viewer
            approved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # جدول الطلبات
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_type TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT DEFAULT 'جديد',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =========================
# دوال المستخدمين
# =========================
def register_user(name, phone, email, role, admin_type=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE phone=? OR email=?', (phone, email))
    if c.fetchone():
        conn.close()
        return False
    c.execute('''
        INSERT INTO users (name, phone, email, role, admin_type, approved)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, phone, email, role, admin_type, 1 if role=="client" or role=="admin" else 0))
    conn.commit()
    conn.close()
    return True

def login_user(phone_or_email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE phone=? OR email=?', (phone_or_email, phone_or_email))
    user = c.fetchone()
    conn.close()
    return user

def approve_technician(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE users SET approved=1 WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

def get_pending_technicians():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, email FROM users WHERE role='technician' AND approved=0")
    data = c.fetchall()
    conn.close()
    return data

def get_all_requests():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT r.id, u.name, r.service_type, r.description, r.location, r.status, r.created_at
        FROM requests r
        LEFT JOIN users u ON r.user_id = u.id
    ''')
    data = c.fetchall()
    conn.close()
    return data

def save_request(user_id, service, desc, location):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO requests (user_id, service_type, description, location)
        VALUES (?, ?, ?, ?)
    ''', (user_id, service, desc, location))
    conn.commit()
    conn.close()

# =========================
# واجهة التطبيق
# =========================
st.set_page_config(page_title="منصة Jsaas", layout="centered")
st.title("منصة Jsaas للخدمات الذكية")

mode = st.radio("اختر العملية", ["تسجيل دخول", "تسجيل جديد"])

if mode == "تسجيل جديد":
    name = st.text_input("الاسم الكامل")
    phone = st.text_input("رقم الجوال")
    email = st.text_input("البريد الإلكتروني")
    role_label = st.selectbox("نوع المستخدم", ["عميل", "فني", "إدارة (Super)", "إدارة (Viewer)"])

    if role_label == "عميل":
        role, admin_type = "client", None
    elif role_label == "فني":
        role, admin_type = "technician",
