import streamlit as st
import sqlite3
from db import init_db
import openai
import os
import pandas as pd
import matplotlib.pyplot as plt

# إعداد المفتاح
openai.api_key = os.getenv("OPENAI_API_KEY")

# تهيئة قاعدة البيانات
init_db()

# إدخال طلب جديد
def insert_ticket(name, phone, issue_type, description, assigned_to):
    conn = sqlite3.connect('maintenance.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO tickets (customer_name, phone, issue_type, description, status, assigned_to)
        VALUES (?, ?, ?, ?, 'جديد', ?)
    ''', (name, phone, issue_type, description, assigned_to))
    conn.commit()
    conn.close()

# جلب الطلبات
def get_tickets():
    conn = sqlite3.connect('maintenance.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tickets ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows

# رد ذكي باستخدام GPT
def ai_response(description):
    prompt = f"عميل أرسل المشكلة التالية: {description}\nاقترح رد مهني مختصر:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# إعداد الصفحة
st.set_page_config(page_title="Jsaas - نظام الصيانة الذكي", layout="wide")
st.title("🛠️ Jsaas | نظام إدارة طلبات الصيانة")

# نموذج إدخال
with st.form("new_ticket"):
    st.subheader("إدخال طلب جديد")
    name = st.text_input("اسم العميل")
    phone = st.text_input("رقم الجوال")
    issue_type = st.selectbox("نوع المشكلة", ["كهرباء", "كاميرات", "شبكة", "أخرى"])
    description = st.text_area("وصف المشكلة")
    assigned_to = st.text_input("الموظف المسؤول")
    submitted = st.form_submit_button("إرسال الطلب")
    if submitted:
        insert_ticket(name, phone, issue_type, description, assigned_to)
        st.success("✅ تم تسجيل الطلب بنجاح")

# عرض الطلبات
st.subheader("📋 الطلبات الحالية")
tickets = get_tickets()
for t in tickets:
    st.markdown(f"**#{t[0]} | {t[1]} | {t[3]} | الحالة: {t[5]}**")
    st.markdown(f"📞 {t[2]} | 👨‍🔧 {t[6]} | 🕒 {t[7]}")
    st.markdown(f"📝 {t[4]}")
    if st.button(f"رد ذكي للطلب #{t[0]}", key=f"ai_{t[0]}"):
        reply = ai_response(t[4])
        st.info(f"🤖 الرد المقترح: {reply}")
    st.markdown("---")

# تقارير مرئية
st.subheader("📈 تقارير الطلبات")
conn = sqlite3.connect('maintenance.db')
df = pd.read_sql_query("SELECT * FROM tickets", conn)

# توزيع الحالات
status_counts = df['status'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')
st.pyplot(fig1)

# نوع المشكلة
issue_counts = df['issue_type'].value_counts()
fig2, ax2 = plt.subplots()
ax2.bar(issue_counts.index, issue_counts.values, color='skyblue')
ax2.set_xlabel("نوع المشكلة")
ax2.set_ylabel("عدد الطلبات")
st.pyplot(fig2)

# جدول الطلبات
st.subheader("📊 أحدث 10 طلبات")
st.dataframe(df.head(10))