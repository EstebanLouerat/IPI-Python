from operator import length_hint
from flask import Flask, flash, redirect, render_template, request, session, url_for
from markupsafe import escape
import sqlite3
import hashlib
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
    """
    Check the format of a email type string
    """
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

    if re.fullmatch(regex, email):
        return True
    else:
        return False


def check_if_connect() -> bool:
    """
    Check if the logging session is in and return a boolean
    """
    if not session.get("logged_in"):
        return True
    return False


def password_hash(password: str) -> str:
    """
    Get a password and return a hashed one
    """
    password_bytes = password.encode("utf-8")

    hash_object = hashlib.sha256(password_bytes)

    # Get the hashed password as a hex string
    hashed_password = hash_object.hexdigest()

    return hashed_password


@app.route("/")
def index():
    if check_if_connect():
        return redirect("/login")
    else:
        return render_template("index.html")


@app.route("/item", methods=["GET", "POST"])
def add_item():
    if check_if_connect():
        return redirect("/login")
    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]
        user_id = session["user_id"]

        # Insert the new item into the DB
        db = sqlite3.connect("instance/database.db")
        db.execute(
            "INSERT INTO shopping_list (item_name, quantity, user_id) VALUES (?, ?, ?)",
            (name, quantity, user_id),
        )
        db.commit()
        db.close()
        return redirect("/")
    return render_template("add_item.html")


@app.route("/item/<id>", methods=["POST"])
def delete_item(id):
    """
    Perform the delete operation on the resource with the given id
    """
    if check_if_connect():
        return redirect("/login")

    db = sqlite3.connect("instance/database.db")
    db.execute("DELETE FROM shopping_list WHERE id = ?", (id))
    db.commit()
    db.close()

    print(f"Remove {escape(id)}")
    return redirect("/list")


@app.route("/list")
def list():
    if check_if_connect():
        return redirect("/login")

    # Print only the item that the user added
    db = sqlite3.connect("instance/database.db")
    cur = db.execute(f'SELECT * FROM shopping_list WHERE user_id={session["user_id"]}')
    rows = cur.fetchall()
    columns = [column[0] for column in cur.description]
    ids = []
    names = []
    quantities = []

    for row in rows:
        ids.append(row[columns.index("id")])
        names.append(row[columns.index("item_name")])
        quantities.append(row[columns.index("quantity")])

    db.close()
    return render_template("list.html", names=names, quantities=quantities, id=ids)


# Login, Sign up and Logout
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Handle the register possible error
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
            # Insert into the DB the new user
            db = sqlite3.connect("instance/database.db")

            db.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password_hash(password), email),
            )
            db.commit()

            # And add the user id into the session storage
            result = db.execute(
                "SELECT id from users WHERE username=?", (username)
            ).fetchone()
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
            f"SELECT id, username, email, password from users WHERE username=? OR email=?",
            (username, username),
        )
        rows = credential.fetchall()
        columns = [column[0] for column in credential.description]

        for row in rows:
            if (
                password_hash(password) == row[columns.index("password")]
                and username == row[columns.index("username")]
            ):
                session["logged_in"] = True

                # And add the user id into the session storage
                session["user_id"] = row[columns.index("id")]
                return redirect("/")
        flash("wrong password or username!")

        db.close()
    return render_template("login.html")


@app.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect("/")
