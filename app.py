from operator import length_hint
from flask import Flask, flash, redirect, render_template, request, session, url_for
from markupsafe import escape
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12)

# Connection to the DB
conn = sqlite3.connect('database.db')

# Create the table
with open('schema.sql', 'r') as f:
    schema = f.read()
conn.executescript(schema)

# conn.execute()

# Close the BD connection
conn.close()

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect("/login")
    else:
        return render_template("index.html")

@app.route("/list")
def list():
    db = sqlite3.connect('database.db')
    cur = db.execute('SELECT * FROM users')
    rows = cur.fetchall()
    columns = [column[0] for column in cur.description]
    
    html = "<ul>"
    for row in rows:
        html += "<li>" + row[columns.index('username')] + ", " + row[columns.index('email')] + "</li>"
    html += "</ul>"
    
    db.close()
    return render_template("list.html", list=html)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if length_hint(password) < 4:
            flash("Password has to been 4 characters length minimum", 'error')
            return render_template("signup.html")
        elif username.length() < 4:
            flash("Username has to been 4 characters length minimum", 'error')
            return render_template("signup.html")
        elif email.length() < 4:
            flash("Email has to been 4 characters length minimum", 'error')
            return render_template("signup.html")
        else:
            session['logged_in'] = True
            flash('You were successfully Sign up')
            return redirect("/")
    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == 'password' and username == 'admin':
            session['logged_in'] = True
            return redirect("/")
        else:
            flash('wrong password!')
    return render_template("login.html")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect("/")