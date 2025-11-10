import streamlit as st
import sqlite3

# إعداد الصفحة والشعار
st.set_page_config(page_title="منصة Jsaas", layout="centered")
try:
    st.image("logo.png", width=120)
except:
    st.warning("⚠️ لم يتم العثور على ملف الشعار logo.png")

st.title("منصة Jsaas للخدمات الذكية")

DB_NAME = "maintenance.db"

# تهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            role TEXT DEFAULT 'client',
            approved INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
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

# دوال المستخدمين
def register_user(name, phone, email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE phone=? OR email=?', (phone, email))
    if c.fetchone():
        conn.close()
        return False
    # فقط Mohamed Atef Salah يكون Super Admin
    if name.strip() == "Mohamed Atef Salah" and email.strip() == "masalah199685@gmail.com":
        role = "admin"
    else:
        role = "client"
    c.execute('INSERT INTO users (name, phone, email, role) VALUES (?, ?, ?, ?)', (name, phone, email, role))
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

def save_request(user_id, service, desc, location):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO requests (user_id, service_type, description, location)
        VALUES (?, ?, ?, ?)
    ''', (user_id, service, desc, location))
    conn.commit()
    conn.close()

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

# واجهة التسجيل والدخول
st.subheader("المصادقة")

mode = st.radio("اختر العملية", ["تسجيل دخول", "تسجيل جديد"])

if mode == "تسجيل جديد":
    name = st.text_input("الاسم الكامل")
    phone = st.text_input("رقم الجوال")
    email = st.text_input("البريد الإلكتروني")
    if st.button("تسجيل"):
        if not name or not (phone or email):
            st.error("يرجى إدخال الاسم ورقم الجوال أو البريد الإلكتروني")
        else:
            success = register_user(name, phone, email)
            if success:
                st.success("✅ تم إنشاء الحساب بنجاح")
            else:
                st.warning("⚠️ هذا المستخدم مسجل مسبقًا")

else:
    phone_or_email =
