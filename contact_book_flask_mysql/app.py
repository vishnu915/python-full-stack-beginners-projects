from flask import Flask, render_template, request, redirect, url_for
from flaskext.mysql import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'       # change as needed
app.config['MYSQL_DATABASE_PASSWORD'] = 'vishnu@123'       # change as needed
app.config['MYSQL_DATABASE_DB'] = 'contact_db'

mysql = MySQL()
mysql.init_app(app)

@app.route('/')
def index():
    cur = mysql.connect().cursor()
    cur.execute("SELECT * FROM contacts")
    contacts = cur.fetchall()
    cur.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO contacts (name, phone, email) VALUES (%s, %s, %s)", (name, phone, email))
    conn.commit()
    cur.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit_contact(id):
    cur = mysql.connect().cursor()
    cur.execute("SELECT * FROM contacts WHERE id=%s", (id,))
    contact = cur.fetchone()
    cur.close()
    return render_template('edit.html', contact=contact)

@app.route('/update/<int:id>', methods=['POST'])
def update_contact(id):
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("UPDATE contacts SET name=%s, phone=%s, email=%s WHERE id=%s", (name, phone, email, id))
    conn.commit()
    cur.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_contact(id):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
