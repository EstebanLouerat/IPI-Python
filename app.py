from operator import length_hint
from flask import Flask, flash, redirect, render_template, request, session, url_for
from markupsafe import escape
import sqlite3
import re
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(12)

# Connection to the DB
conn = sqlite3.connect("instance/database.db")

# Create the table
with open("schema.sql", "r") as f:
    schema = f.read()
conn.executescript(schema)

# Close the BD connection
conn.close()


def check_email_format(email: str) -> bool:
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

    if re.fullmatch(regex, email):
        return True
    else:
        return False


def check_if_connect() -> bool:
    if not session.get("logged_in"):
        return True
    return False


@app.route("/")
def index():
    if check_if_connect():
        return redirect("/login")
    else:
        return render_template("index.html")


@app.route("/additem", methods=["GET", "POST"])
def add_item():
    if check_if_connect():
        return redirect("/login")
    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]
        user_id = session["user_id"]
        db = sqlite3.connect("instance/database.db")
        db.execute(
            f'INSERT INTO shopping_list (item_name, quantity, user_id) VALUES ("{name}", "{quantity}", "{user_id}")'
        )
        db.commit()
        db.close()
        return redirect("/")
    return render_template("add_item.html")


@app.route("/list")
def list():
    if check_if_connect():
        return redirect("/login")
    db = sqlite3.connect("instance/database.db")
    cur = db.execute(f'SELECT * FROM shopping_list WHERE user_id={session["user_id"]}')
    rows = cur.fetchall()
    columns = [column[0] for column in cur.description]
    names = []
    quantities = []

    for row in rows:
        names.append(row[columns.index("item_name")])
        quantities.append(row[columns.index("quantity")])

    db.close()
    return render_template("list.html", names=names, quantities=quantities)


# Login, Sign up and Logout


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        if length_hint(password) < 4:
            flash("Password has to been 4 characters length minimum", "error")
            return render_template("signup.html")
        elif length_hint(username) < 4:
            flash("Username has to been 4 characters length minimum", "error")
            return render_template("signup.html")
        elif length_hint(email) < 4:
            flash("Email has to been 4 characters length minimum", "error")
            return render_template("signup.html")
        elif not check_email_format(email):
            flash("Email format is incorrect", "error")
            return render_template("signup.html")
        else:
            db = sqlite3.connect("instance/database.db")

            db.execute(
                f'INSERT INTO users (username, password, email) VALUES ("{username}", "{password}", "{email}")'
            )
            result = db.execute(
                f'SELECT id from users WHERE username="{username}"'
            ).fetchone()
            db.commit()
            session["user_id"] = result[0] if result else None
            session["logged_in"] = True
            db.close()
            return redirect("/")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = sqlite3.connect("instance/database.db")
        credential = db.execute(
            f'SELECT id, username, email, password from users WHERE username="{username}" OR email="{username}" AND password="{password}"'
        )
        rows = credential.fetchall()
        columns = [column[0] for column in credential.description]

        for row in rows:
            if (
                password == row[columns.index("password")]
                and username == row[columns.index("username")]
            ):
                session["logged_in"] = True
                session["user_id"] = row[columns.index("id")]
                return redirect("/")
        flash("wrong password or username!")

        db.close()
    return render_template("login.html")


@app.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect("/")
