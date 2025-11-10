# app.py

import streamlit as st
import sqlite3
import os
import openai
from streamlit_arabic_support_wrapper import support_arabic_text

openai.api_key = os.getenv("OPENAI_API_KEY")

# إنشاء قاعدة البيانات
def init_db():
    conn = sqlite3.connect('maintenance.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            issue_type TEXT NOT NULL,
            description TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            location TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# إدخال تذكرة
def insert_ticket(name, phone, issue_type, description, assigned_to, location):
    conn = sqlite3.connect('maintenance.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO tickets (name, phone, issue_type, description, assigned_to, location)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, phone, issue_type, description, assigned_to, location))
    conn.commit()
    conn.close()

# عرض التذاكر
def view_tickets():
    conn = sqlite3.connect('maintenance.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tickets ORDER BY created_at DESC')
    tickets = c.fetchall()
    conn.close()
    return tickets

# تشغيل قاعدة البيانات
init_db()

# واجهة Streamlit
support_arabic_text()  # تفعيل دعم العربية

st.title("طلب جديد من العميل")

name = st.text_input("الاسم الكامل")
phone = st.text_input("رقم الجوال")
issue_type = st.selectbox("نوع المشكلة", ["اختر نوع المشكلة", "كهرباء", "سباكة", "نظام", "أخرى"])
description = st.text_area("وصف المشكلة")
assigned_to = st.text_input("تعيين إلى (اسم الفني أو القسم)")
location = st.text_input("الموقع الجغرافي (رابط أو عنوان)")

if st.button("إرسال الطلب"):
    if not name.strip():
        st.error("❌ يرجى إدخال الاسم الكامل")
    elif not phone.strip():
        st.error("❌ يرجى إدخال رقم الجوال")
    elif issue_type == "اختر نوع المشكلة":
        st.error("❌ يرجى اختيار نوع المشكلة")
    elif not description.strip():
        st.error("❌ يرجى إدخال وصف المشكلة")
    elif not assigned_to.strip():
        st.error("❌ يرجى إدخال اسم الفني أو القسم")
    elif not location.strip():
        st.error("❌ يرجى إدخال الموقع الجغرافي")
    else:
        insert_ticket(name, phone, issue_type, description, assigned_to, location)
        st.success("✅ تم إرسال الطلب بنجاح")

st.subheader("📋 الطلبات السابقة")
tickets = view_tickets()
for ticket in tickets:
    st.write(f"🔹 {ticket[1]} | {ticket[2]} | {ticket[3]} | {ticket[4]} | {ticket[5]} | {ticket[6]} | {ticket[7]}")