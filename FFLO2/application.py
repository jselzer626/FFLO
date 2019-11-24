import os
import json

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from collections import Counter

from helpers import create_clean_list, pos_rank, playercounter, check_player_quantities, search_list, calculate_inactives

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
positions = ["QB", "RB", "WR", "TE", "DEF", "K"]
flex_positions = ["RB", "WR", "TE"]

# load player rankings and create player and position detail lists
clean_player_list = create_clean_list()
search_list_inactives = search_list(clean_player_list, "inactives")
# update master list and search list with inactives
clean_player_list = calculate_inactives(search_list_inactives, clean_player_list)
search_list = search_list(clean_player_list, "actives")
roster_details = {}
Final_Roster = []

@app.route("/", methods=["GET", "POST"])
def start():
    if request.method =="GET":
        counter = playercounter(Final_Roster, roster_details, flex_positions)
        if roster_details and Final_Roster:
            success_banner = check_player_quantities(counter, roster_details)
            return render_template("index.html", Final_Roster=Final_Roster, roster_details=roster_details, counter=counter, success_banner=success_banner)
        elif roster_details:
            return render_template("index.html", roster_details=roster_details, counter=counter)
        else:
            return render_template("landing.html")
    else:
        roster_detail_keys = ["Type", "Rostered", "Starting", "Bench", "QB", "RB", "WR", "TE", "FLEX", "DEF", "K"]

        roster_details.clear()
        for item in roster_detail_keys:
            if item == "Type":
                roster_details.update({item: request.form["Type"]})
            else:
                roster_details.update({item: request.form.get(item)})

        counter = playercounter(Final_Roster, roster_details, flex_positions)

        return render_template("index.html", roster_details=roster_details, Final_Roster=Final_Roster, counter=counter)

# get user from landing page to roster parameters page, or back to landing page.
@app.route("/start", methods=["GET", "POST"])
def find_starting_point():
    if request.method == "GET":
        roster_details.clear()
        return redirect("/")
    else:
        return render_template("start.html")

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
            return redirect("/start")

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

        return redirect("/start")

    else:
        return render_template("login.html")

@app.route("/clear_roster_details", methods=["GET"])
def clear_roster_details():
    return render_template("start.html", roster_details=roster_details)

@app.route("/clear_lineup", methods=["GET"])
def clear_lineup():
    Final_Roster.clear()
    counter = playercounter(Final_Roster, roster_details, flex_positions)
    success_banner = check_player_quantities(counter, roster_details)
    return jsonify(counter, success_banner)

@app.route("/search")
def search():
    q = request.args.get("q")
    players_display = [player for player in search_list if player[0].casefold().startswith(q.casefold())]
    return jsonify(players_display)


@app.route("/addplayer", methods=["GET"])
def addplayer():
    player_to_add = request.args.get("q").split(" , ")
    player_match = ''
    try:
        for item in clean_player_list[roster_details["Type"]]:
            if [item["name"],item["team"],item["position"]] == player_to_add:
                player_match = item
    except (KeyError, TypeError, ValueError):
        return jsonify(False)

    if player_match:
        # for duplicate players
        if player_match in Final_Roster:
            return jsonify(False)
        # add new player
        else:
            Final_Roster.append(player_match)
            counter = playercounter(Final_Roster, roster_details, flex_positions)
            success_banner = check_player_quantities(counter, roster_details)
            return jsonify(player_to_add, counter, success_banner)
    # invalid input (i.e. blank or not selected from drop-down)
    else:
        return jsonify(False)

        '''for item in clean_player_list[roster_details["Type"]]:
            if ([item["name"],item["team"],item["position"]]) == player_to_add:
                Final_Roster.append(item)
                counter = playercounter(Final_Roster, roster_details, flex_positions)
                success_banner = check_player_quantities(counter, roster_details)
                return jsonify(player_to_add, counter, success_banner)'''

@app.route("/removeplayer", methods=["GET"])
def removeplayer():
    player_to_remove = request.args.get("q")
    for item in Final_Roster:
        if (item["name"] + item["team"] + item["position"]) == player_to_remove:
            Final_Roster.remove(item)
    counter = playercounter(Final_Roster, roster_details, flex_positions)
    success_banner = check_player_quantities(counter, roster_details)
    return jsonify(counter, success_banner)

@app.route("/createlineup", methods=["POST"])
def createlineup():
    if request.method == "POST":

        # sort final roster
        Final_Roster.sort(key=pos_rank)

        # declare necessary display lists
        starters = []
        flex = []
        bench_players = []
        req_details = ["name", "team", "position", "posrank"]
        total_projected = 0

        # ensure req_details displays either ppr or standard
        if roster_details:
            if roster_details["Type"] == "Standard":
                req_details.append("standard")
            else:
                req_details.append("ppr")

        # non flex starters
        for player in Final_Roster:
            for position in positions:
                if Counter(player['position'] for player in starters)[position] < int(roster_details[position]) and player["position"] == position:
                    starters.append(player)
                    total_projected += float(player[req_details[4]])

        # flex starters
        for player in Final_Roster:
            if player["position"] in flex_positions and len(starters) + len(flex) < int(roster_details["Starting"]) and player not in starters:
                flex.append(player)
                total_projected += float(player[req_details[4]])

        # bench players
        for player in Final_Roster:
            if player not in starters and player not in flex:
                bench_players.append(player)

        return render_template("result.html", req_details=req_details, starters=starters, flex=flex, bench_players=bench_players, total_projected=total_projected, positions=positions,
        roster_details=roster_details, Final_Roster=Final_Roster)
