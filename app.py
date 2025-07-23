from flask import Flask, render_template, request, redirect, session
from datetime import time
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('cab.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cab_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            shift_start TEXT,
            shift_end TEXT,
            status TEXT DEFAULT 'pending',
            request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_by TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Simulated login (you can improve this later)
@app.before_request
def mock_login():
    session['emp_id'] = 101  # Fixed ID for demo
    session['emp_name'] = "Lakshmi"

def is_night_shift(start, end):
    return start >= time(20, 0) or end <= time(6, 0)

@app.route('/')
def home():
return "SmartCab is live! Use /request_cab or /track_requests in the URL."

@app.route('/request_cab', methods=['GET', 'POST'])
def request_cab():
    if request.method == 'POST':
        emp_id = session['emp_id']
        shift_start = request.form['shift_start']
        shift_end = request.form['shift_end']

        start = time.fromisoformat(shift_start)
        end = time.fromisoformat(shift_end)

        status = 'approved' if is_night_shift(start, end) else 'pending'
        approved_by = 'System' if status == 'approved' else None

        conn = sqlite3.connect('cab.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO cab_requests (emp_id, shift_start, shift_end, status, approved_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (emp_id, shift_start, shift_end, status, approved_by))
        conn.commit()
        conn.close()

        return redirect('/track_requests')
    return render_template('request_cab.html')

@app.route('/track_requests')
def track_requests():
    emp_id = session['emp_id']
    conn = sqlite3.connect('cab.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT * FROM cab_requests
        WHERE emp_id = ?
        ORDER BY request_time DESC
    ''', (emp_id,))
    requests = c.fetchall()
    conn.close()
    return render_template('track_requests.html', requests=requests)

if __name__ == '__main__':
    port=int(os.environ.get('PORT',10000))
    app.run(host='0.0.0.0', port=port)
