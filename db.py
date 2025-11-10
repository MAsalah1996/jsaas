import sqlite3

def init_db():
    conn = sqlite3.connect('maintenance.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            issue_type TEXT,
            description TEXT,
            status TEXT,
            assigned_to TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()