from flask import Flask, request, jsonify, render_template_string
import psycopg2
import os
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)

# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Initialize database table
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# HTML Template (simple frontend)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Guestbook</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        form { background: #f4f4f4; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        input, textarea { width: 100%; padding: 10px; margin: 5px 0; }
        button { background: #3498db; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        .message { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }
        .timestamp { color: #888; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>📝 Guestbook</h1>
    
    <form action="/add" method="POST">
        <input type="text" name="name" placeholder="Your Name" required>
        <textarea name="message" placeholder="Your Message" rows="4" required></textarea>
        <button type="submit">Add Message</button>
    </form>
    
    <h2>Recent Messages</h2>
    {% for msg in messages %}
    <div class="message">
        <strong>{{ msg.name }}</strong>
        <p>{{ msg.message }}</p>
        <span class="timestamp">{{ msg.created_at }}</span>
    </div>
    {% endfor %}
</body>
</html>
'''

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT name, message, created_at FROM messages ORDER BY created_at DESC LIMIT 10')
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return render_template_string(HTML_TEMPLATE, messages=messages)

@app.route('/add', methods=['POST'])
def add_message():
    name = request.form.get('name')
    message = request.form.get('message')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO messages (name, message) VALUES (%s, %s)', (name, message))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))