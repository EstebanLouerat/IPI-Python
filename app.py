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

# Close the BD connection
conn.close()


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return do_the_login()
#     else:
#         return show_the_login_form()

@app.route("/<name>")
def hello(name):
    return f"<h2>Hello, {escape(name)}!<h2>"

@app.route('/')
def index():
    return "<h1>This is a Flask app<h1>"