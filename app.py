from flask import Flask
from flask import request
from markupsafe import escape
import sqlite3

app = Flask(__name__)

# Connection to the DB
conn = sqlite3.connect('database.db')

# Create the table
with open('schema.sql', 'r') as f:
    schema = f.read()
conn.executescript(schema)

conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", ("John", "1234", "john@email.fr"))
conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", ("Jane", "6547", "jane@email.com"))

conn.commit()
# Close the BD connection
conn.close()


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return do_the_login()
#     else:
#         return show_the_login_form()

@app.route("/profile")
def profile():
    cur = conn.execute('SELECT * FROM users')
    rows = cur.fetchall()
    
    html = "<ul>"
    for row in rows:
        html += "<li>" + row['username'] + ", " + row['email'] + "</li>"
    html += "</ul>"
    return html

@app.route('/')
def index():
    conn2 = sqlite3.connect('database.db')
    cur = conn2.execute('SELECT username FROM users')
    conn2.close()
    return f'<h1>This is a Flask app of {cur}<h1>'