import os
import json

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from collections import Counter

from helpers import create_clean_list, pos_rank, playercounter, check_player_quantities, search_list, calculate_inactives, login_required

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = SQL("sqlite:///FFLO.db")

# global position & detail lists
roster_parameters = ["Type", "Rostered", "Starting", "Bench", "QB", "RB", "WR", "TE", "FLEX", "DEF", "K"];
positions = ["QB", "RB", "WR", "TE", "DEF", "K"]
flex_positions = ["RB", "WR", "TE"]

@app.route('/start', methods=["GET"])
def start():
    return render_template("landing.html")

@app.route('/register', methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        # input validation for username/password is going to occur entirely client side with javascript
        username = request.form.get("username")
        password_hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        register_success = db.execute("INSERT INTO users (username, passwordHash) VALUES (:username, :password_hash)", username=username, password_hash=password_hash)

        if register_success:
            # query database for user that was just registered
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

            # login in newly registered user
            session["user_id"] = rows[0]["userId"]

            # Redirect user to home page
            return redirect("/")

        else:
            # check for duplicate usernames
            return render_template("register.html", message="Username already taken")

    elif request.method == "GET":
        return render_template("register.html")

@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":

        # logout any current user
        session.clear()

        # minimum length requirements of passwords have already been verified client side
        rows = db.execute('SELECT * FROM users WHERE username = :username', username=request.form.get("username"))

        # invalid username / password
        if len(rows) != 1 or not check_password_hash(rows[0]['passwordHash'], request.form.get("password")):
            return render_template('login.html', message = "Could Not Retrieve Username/Password")
        else:
            session["user_id"] = rows[0]["userId"]

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/", methods = ['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        return render_template("index.html")
    #else TODO

@app.route('/createRoster', methods = ['GET', 'POST'])
@login_required
def createRoster():
    if request.method == "GET":
        return render_template("createRoster.html")
    else:
        roster_name = request.form.get('Name')
        roster_details = {parameter: request.form.get(parameter) for parameter in roster_parameters}
        return render_template("createLineup.html", roster_details = roster_details, roster_name = roster_name)

@app.route('/logout', methods=["GET"])
def logout():
    session.clear()

    # Redirect user to login form
    return redirect("/")