import streamlit as st
import sqlite3

# 1️⃣ إنشاء قاعدة بيانات وجدول المستخدمين والطلبات
def init_db():
    conn = sqlite3.connect("maintenance.db")
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            role TEXT DEFAULT 'client',  -- client / technician / admin
            approved INTEGER DEFAULT 0,  -- 0 = غير مفعل، 1 = مفعل
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

# دوال المستخدمين
def register_user(name, phone, email, role):
    conn = sqlite3.connect("maintenance.db")
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE phone = ? OR email = ?', (phone, email))
    if c.fetchone():
        conn.close()
        return False
    c.execute('INSERT INTO users (name, phone, email, role) VALUES (?, ?, ?, ?)', (name, phone, email, role))
    conn.commit()
    conn.close()
    return True

def login_user(phone_or_email):
    conn = sqlite3.connect("maintenance.db")
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE phone = ? OR email = ?', (phone_or_email, phone_or_email))
    user = c.fetchone()
    conn.close()
    return user

# دالة حفظ الطلب
def save_request(user_id, service, desc, location):
    conn = sqlite3.connect("maintenance.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO requests (user_id, service_type, description, location)
        VALUES (?, ?, ?, ?)
    ''', (user_id, service, desc, location))
    conn.commit()
    conn.close()

# تشغيل قاعدة البيانات
init_db()

# 2️⃣ واجهة التطبيق
st.set_page_config(page_title="منصة Jsaas", layout="centered")
st.image("logo.png", width=120)
st.title("منصة Jsaas للخدمات الذكية")

# اختيار تسجيل دخول أو تسجيل جديد
mode = st.radio("اختر العملية", ["تسجيل دخول", "تسجيل جديد"])

if mode == "تسجيل جديد":
    name = st.text_input("الاسم الكامل")
    phone = st.text_input("رقم الجوال")
    email = st.text_input("البريد الإلكتروني")
    role = st.selectbox("نوع المستخدم", ["عميل", "فني"])
    role_value = "client" if role == "عميل" else "technician"

    if st.button("تسجيل"):
        if not name or (not phone and not email):
            st.warning("يرجى إدخال الاسم ورقم الجوال أو البريد الإلكتروني")
        else:
            success = register_user(name, phone, email, role_value)
            if success:
                if role_value == "technician":
                    st.info("✅ تم إرسال طلب التسجيل كفني، بانتظار موافقة الإدارة")
                else:
                    st.success("✅ تم إنشاء الحساب بنجاح")
            else:
                st.error("⚠️ هذا المستخدم مسجل مسبقًا")

else:  # تسجيل دخول
    phone_or_email = st.text_input("رقم الجوال أو البريد الإلكتروني")
    if st.button("دخول"):
        user = login_user(phone_or_email)
        if user:
            if user[5] == 0 and user[4] == "technician":
                st.warning("🛑 لم يتم تفعيل حسابك كفني بعد، يرجى انتظار موافقة الإدارة")
            else:
                st.success(f"مرحبًا {user[1]} 👋")
                st.session_state["user"] = user
        else:
            st.error("❌ لم يتم العثور على مستخدم بهذا الرقم أو البريد")

# 3️⃣ واجهة العميل بعد تسجيل الدخول
if "user" in st.session_state:
    user = st.session_state["user"]
    st.subheader("📌 طلب خدمة جديدة")
    service = st.selectbox("نوع الخدمة", ["كهرباء", "سباكة", "تكييف", "تنظيف", "أخرى"])
    desc = st.text_area("وصف المشكلة")
    location = st.text_input("الموقع الجغرافي")

    if st.button("إرسال الطلب"):
        if not desc.strip() or not location.strip():
            st.error("❌ يرجى تعبئة جميع الحقول المطلوبة")
        else:
            save_request(user[0], service, desc, location)
            st.success("✅ تم إرسال الطلب بنجاح")
            st.balloons()
