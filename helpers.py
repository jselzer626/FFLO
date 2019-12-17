import os
import requests
import json

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
from collections import Counter

# configure db for addandDeleteplayers function
db = SQL("sqlite:///FFLO.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/start")
        return f(*args, **kwargs)
    return decorated_function

def addAndDeletePlayers(saveDetails, session=session):
    if saveDetails['playersToDelete']:
        playersDeleted = [db.execute('DELETE FROM players WHERE rosterName = :rosterName AND userId = :userId AND playerId = :playerId', rosterName = saveDetails['rosterName'], userId = session["user_id"],
        playerId = player['playerId']) for player in saveDetails['playersToDelete']]

    if saveDetails['playersToAdd']:
        playersAdded = [db.execute('INSERT INTO players (rosterName, userId, playerName, playerPosition, playerTeam, playerId) VALUES (:rosterName, :userId, :playerName, :playerPosition, :playerTeam, :playerId)',
        rosterName = saveDetails['rosterName'], userId = session["user_id"], playerName = player["playerName"], playerPosition = player["playerPosition"], playerTeam = player["playerTeam"], playerId = player["playerId"])
        for player in saveDetails['playersToAdd']]

    #what should I return here?
    return 1
