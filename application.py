import os
import requests
import json

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from collections import Counter
from datetime import date

from helpers import login_required, addAndDeletePlayers

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['DEBUG'] = True

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
player_save_details = ['playersToSave', 'rosterName']

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

        currentRosters = db.execute("SELECT * FROM rosters WHERE userId = :userId", userId = session["user_id"])

        return render_template("index.html", currentRosters = currentRosters)
    #else TODO

@app.route('/createRoster', methods = ['GET', 'POST'])
@login_required
def createRoster():
    if request.method == "GET":

        return render_template("createRoster.html")

    else:
        new_roster_name = request.form.get('Name')

        roster_details = {parameter: request.form.get(parameter) for parameter in roster_parameters}

        rosterDetailsAdded = db.execute('INSERT INTO rosters (rosterName, userId, Type, Rostered, Starting, Bench, QB, RB, WR, TE, FLEX, DEF, K) VALUES (:rosterName, :userId, :Type, :Rostered, :Starting, :Bench, :QB, :RB, :WR, :TE, :FLEX, :DEF, :K)',
        rosterName = new_roster_name, userId = session["user_id"], Type=roster_details['Type'], Rostered=roster_details['Rostered'], Starting=roster_details['Starting'], Bench=roster_details['Bench'], QB=roster_details['QB'], RB=roster_details['RB'], WR=roster_details['WR'],
        TE=roster_details['TE'], FLEX=roster_details['FLEX'], DEF=roster_details['DEF'], K=roster_details['K'])

        return render_template("createLineup.html", roster_details = roster_details, roster_name = new_roster_name)

@app.route('/logout', methods=["GET"])
def logout():
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route('/save', methods=["POST"])
@login_required
def save():
    if request.method == "POST":

        saveDetails = json.loads(request.form.get('savedLineup'))

        # see helpers.py for full documentation
        addAndDeletePlayers(saveDetails)

        return redirect('/editLineup?rosterName=' + saveDetails["rosterName"])

@app.route('/loadPlayers', methods=["GET"])
def loadPlayers():
    if request.method == "GET":

        return jsonify(db.execute('SELECT playerName, playerPosition, playerTeam, playerId FROM players WHERE rosterName = :rosterName', rosterName = request.args.get('rosterName')))

@app.route('/editLineup', methods=["GET", "POST"])
@login_required
def editLineup():

    rosterName = ''
    message = ''

    if request.method == "POST":
        rosterName = request.form.get('lineupToEdit')

    else:
        rosterName = request.args.get('rosterName')
        message = f'{rosterName} saved!'

    roster_details = db.execute("SELECT * FROM rosters WHERE userId = :userId AND rosterName = :rosterName", userId = session["user_id"], rosterName = rosterName)

    return render_template("createLineup.html", roster_name = rosterName, roster_details = {detail: roster_details[0][detail] for detail in roster_details[0] if detail in roster_parameters}, message=message)

@app.route('/deleteLineup', methods=["GET"])
def delete():
    if request.method == "GET":
        rosterName = request.args.get("rosterName")

        db.execute('DELETE FROM rosters WHERE rosterName = :rosterName', rosterName = rosterName)

        return jsonify(rosterName)

@app.route('/optimize', methods=["POST"])
def optimize():
    if request.method == "POST":

        playerRankings = {}
        saveDetails = json.loads(request.form.get('playersToOptimize'))
        print(saveDetails)

        # perform normal add and delete players functions - see helpers.py for full documentation
        addAndDeletePlayers(saveDetails);

        # eventually add functionality to let user change weeks but for now use current week
        currentWeek = requests.get("https://www.fantasyfootballnerd.com/service/weather/json/8qb63ck2ibj4/").json()["Week"]

        for position in positions:
            if saveDetails["playersToOptimize"][position]:
                #call rankings API, return as ordered list where index of player is their weekly rankings
                positionRankings = requests.get(f'https://www.fantasyfootballnerd.com/service/weekly-rankings/json/8qb63ck2ibj4/{position}/{currentWeek}/{saveDetails["leagueType"]}').json()["Rankings"]

                for player in positionRankings:
                    if player["playerId"] in saveDetails["playersToOptimize"][position]:
                        playerRankings.update({player['playerId']: positionRankings.index(player)})

        return render_template("result.html", rosterName = saveDetails["rosterName"])







if __name__ == '__main__':
 app.debug = True
 port = int(os.environ.get('PORT', 5000))
 app.run(host='0.0.0.0', port=port)
