import os
import requests
import urllib.parse
import json
import timeit

from flask import redirect, render_template, request, session
from functools import wraps
from collections import Counter

positions = ["QB", "RB", "WR", "TE", "DEF", "K"]
req_details = ["name", "team", "position", "posrank", "standard", "ppr"]
    #links_to_check = ["https://www.fantasyfootballnerd.com/service/weekly-rankings/json/8qb63ck2ibj4/" + position + "/" for position in positions]

def create_clean_list():
    league_indicator = {0:'PPR' , 1:'Standard'}
    final_list = {}

    for item in league_indicator:
        full_player_list = {}
        clean_player_list= []
        week_check = requests.get("https://www.fantasyfootballnerd.com/service/weather/json/8qb63ck2ibj4/").json()["Week"]
        # week = week_check.json()["Week"]
        for position in positions:

            link = "https://www.fantasyfootballnerd.com/service/weekly-rankings/json/8qb63ck2ibj4/" + position + "/" + week_check + "/" + str(item)

            pos_list = []

            try:
                response = requests.get(link)
                response.raise_for_status()
            except requests.RequestException:
                return None

            try:
                pos_list = response.json()['Rankings']
            except (KeyError, TypeError, ValueError):
                return None

            for n in range(len(pos_list)):
                pos_list[n].update({"posrank": n+1})
            full_player_list.update({position: pos_list})

        for position in positions:
            for player in full_player_list[position]:
                temp_add = {}
                for detail in req_details:
                    temp_add.update({detail: player[detail]})
                clean_player_list.append(temp_add)


        final_list.update({league_indicator[item]: clean_player_list})

    return(final_list)

def pos_rank(item):
    if item["posrank"] != "N/A":
        return item["posrank"]
    else:
        return 500

# item1 = Final_Roster
# item2 = roster_details
# item3 = flex_positions

def playercounter(item1, item2, item3):
    counter = {detail: 0 for detail in item2 if detail != "Type"}
    pos_counter = Counter(player['position'] for player in item1)
    if pos_counter:
        for item in pos_counter:
            if item in counter:
                counter[item] = pos_counter[item]
        rostered = int(sum(counter.values()))
        counter.update({"Rostered" : rostered})
        counter.update({"Starting" : rostered})
        #create flex and bench
        for position in item2:
            if position != "Type" and counter[position] > int(item2[position]):
                if position in item3:
                    counter["FLEX"] += counter[position] - int(item2[position])
                counter[position] = int(item2[position])
        if rostered > int(counter["Starting"]):
            counter.update({"Bench": rostered - int(counter["Starting"])})
        return counter
    else:
        return counter

def check_player_quantities(counter, roster_details):
    set_quantities = {item: int(quantity) for (item, quantity) in roster_details.items() if item != "Type"}
    success_banner = all(set_quantity == inputted_quantity for set_quantity, inputted_quantity in zip(counter.values(), set_quantities.values()))
    return success_banner

def search_list(item1, item2):
    lookup_list = []
    if item2 == "inactives":
        for player in item1["Standard"]:
            temp_add = []
            for detail in req_details[:3]:
                temp_add.append(player[detail])
            lookup_list.append(temp_add)
    else:
        for player in item1["Standard"]:
            temp_add = []
            temp_add.append(player["name"] + " ")
            temp_add.append(" " + player["team"] + " , " + player["position"])
            lookup_list.append(temp_add)
    return lookup_list

# item1 = search_list(active_player_list, "inactives")
# item2 = clean_player_list

def calculate_inactives(item1, item2):

    full_player_list = []
    for position in positions:

        link = "https://www.fantasyfootballnerd.com/service/players/json/8qb63ck2ibj4/" + position + "/"
        response = requests.get(link)
        pos_list = list(response.json()['Players'])

        for player in pos_list:
            temp_add = []
            for detail in req_details[:3]:
                if detail == 'name':
                    temp_add.append(player["displayName"])
                else:
                    temp_add.append(player[detail])
            full_player_list.append(temp_add)

    inactives = [player for player in full_player_list if player not in item1]

    inactives_clean = []

    for player in inactives:
        temp_add = {}
        for n in range(len(req_details[:3])):
            temp_add.update({req_details[n]: player[n]})
        temp_add.update({"posrank": "N/A"})
        temp_add.update({"standard": 0})
        temp_add.update({"ppr": 0})
        inactives_clean.append(temp_add)

    for item in item2:
        for player in inactives_clean:
            item2[item].append(player)

    return item2

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