from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'vishnu@123',  # Add your MySQL password here
    'database': 'event_registration'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    return redirect(url_for('list_events'))

@app.route('/events')
def list_events():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all events
    cursor.execute("SELECT * FROM events ORDER BY date")
    events = cursor.fetchall()
    
    # For each event, get the number of registrations
    for event in events:
        cursor.execute("SELECT COUNT(*) as count FROM registrations WHERE event_id = %s", (event['event_id'],))
        result = cursor.fetchone()
        event['registrations_count'] = result['count']
    
    cursor.close()
    conn.close()
    return render_template('events.html', events=events)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (title, description, date, location) VALUES (%s, %s, %s, %s)",
            (title, description, date, location)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Event added successfully!', 'success')
        return redirect(url_for('list_events'))
    
    return render_template('add_event.html')

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register(event_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get event details
    cursor.execute("SELECT * FROM events WHERE event_id = %s", (event_id,))
    event = cursor.fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        try:
            # Check if user exists, if not create
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
                user_id = cursor.lastrowid
            else:
                user_id = user['user_id']
            
            # Register user for event
            cursor.execute(
                "INSERT INTO registrations (user_id, event_id) VALUES (%s, %s)",
                (user_id, event_id)
            )
            conn.commit()
            flash('Registration successful!', 'success')
        except mysql.connector.IntegrityError:
            conn.rollback()
            flash('You are already registered for this event!', 'error')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('list_events'))
    
    cursor.close()
    conn.close()
    return render_template('register.html', event=event)

@app.route('/registrations')
def view_registrations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all registrations with user and event details
    cursor.execute("""
        SELECT r.registration_id, r.registration_date, 
               u.name as user_name, u.email, 
               e.title as event_title, e.date as event_date
        FROM registrations r
        JOIN users u ON r.user_id = u.user_id
        JOIN events e ON r.event_id = e.event_id
        ORDER BY r.registration_date DESC
    """)
    registrations = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('registrations.html', registrations=registrations)

if __name__ == '__main__':
    app.run(debug=True)