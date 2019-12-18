let flex_positions = ["RB", "WR", "TE"];
//figure out which actions are using roster_details and see if we can consolidate
let quantityCheck = ["Rostered", "Starting", "Bench", "QB", "RB", "WR", "TE", "FLEX", "DEF", "K"];
let roster_details = ["Type", "Rostered", "Starting", "Bench", "QB", "RB", "WR", "TE", "FLEX", "DEF", "K"];
let player_details = ['playerName', 'playerPosition', 'playerTeam', 'playerId'];
let justPositions = ["QB", "RB", "WR", "TE", "FLEX", "DEF", "K"];

//factor out so many document.getElementById calls
getId = Id => {
    return document.getElementById(Id);
}

//quickly retrieve numeric value of html in <td>'s for counter
numberConv = elem => {
    return parseInt(elem.innerHTML);
}

let invalid_input_message = display_message => {
    getId("invalid_input").innerHTML = display_message;
    getId("invalid_input").style.visibility = "visible";
    setTimeout(function() {
        getId("invalid_input").style.visibility = "hidden";
    }, 5000);
};

//eliminate redundancies in sorting function on results.html
rosterCounterChange = (position, rosterCounter) => {
  rosterCounter[position] += 1;
  rosterCounter["Starting"] += 1;
}

buildList = (player, button=true) => {
  return button === true ? `<tr><td>${player.playerName}</td><td class="playerPosition">${player.playerPosition}</td><td>${player.playerTeam}</td>
  <td class="playerId">${player.playerId}</td><td><button class="remove" class="btn btn-primary">Remove</button></td></tr>` :
  `<tr><td>${player.playerName}</td><td class="playerPosition">${player.playerPosition}</td><td>${player.playerTeam}</td>
  <td class="playerId">${player.playerRanking}</td><td>${player.projected}</td></tr>`;
}

//change <td> color to green if <td> value equals required roster quantity
//for counter that loads when page is loaded, operation will be set to load_page
//for counter used during normal add or remove functions operation is set to normal
addColor = (detail, loadPage=false) => {
    //check if final color needed
    if (numberConv(getId(detail)) === numberConv(getId('set' + detail))) {
        getId(detail).style.backgroundColor = "#d4edda";

    } else if (loadPage === false) {
        //flash gray if added / removed any time other than during page loading
        getId(detail).style.backgroundColor = "#d3d3d3";
            setTimeout( function() {
                getId(detail).style.backgroundColor = "";
            }, 500);
        }
    };

let counterChange = (position, action, loadPage=false) => {

    action === 'add' ? getId('Rostered').innerHTML = numberConv(getId('Rostered')) + 1 :
    getId('Rostered').innerHTML = numberConv(getId('Rostered')) - 1;

    addColor('Rostered', loadPage);

    if (action === 'remove') {
         //bench or starting
         if (numberConv(getId("Bench")) > 0) {
             getId('Bench').innerHTML = numberConv(getId("Bench")) - 1;
             addColor('Bench', loadPage);
         } else if (numberConv(getId('Bench')) === 0) {
             getId('Starting').innerHTML = numberConv(getId('Starting')) - 1;
             addColor("Starting", loadPage);
         }

         if (numberConv(getId(`set${position}`)) > 0) {
         // flex or normal
            if (numberConv(getId('FLEX')) > 0 && flex_positions.includes(position)) {
                getId('FLEX').innerHTML = numberConv(getId("FLEX")) - 1;
                addColor("FLEX", loadPage);
            } else {
                getId(position).innerHTML = numberConv(getId(position)) -1;
                addColor(position, loadPage);
            }
        }
    }
    else if (action === 'add') {
        if (numberConv(getId('Starting')) >= numberConv(getId('setStarting'))) {
            getId("Bench").innerHTML = numberConv(getId('Bench')) + 1;
            addColor('Bench', loadPage);
        } else {
            getId("Starting").innerHTML = numberConv(getId('Starting')) + 1;
            addColor('Starting', loadPage);
        }

        if (numberConv(getId(position)) >= numberConv(getId("set" + position)) &&
        numberConv(getId('FLEX')) < numberConv(getId('setFLEX')) &&
        flex_positions.includes(position)) {

            getId("FLEX").innerHTML = numberConv(getId('FLEX')) + 1;
            addColor('FLEX', loadPage);

        } else if (numberConv(getId(position)) < numberConv(getId('set' + position))) {
            getId(position).innerHTML = numberConv(getId(position)) + 1;
            addColor(position, loadPage);
        }
    }

    // check to see if success banner with optimize lineup button should be displayed
    quantityCheck.every(detail => numberConv(getId(detail)) === numberConv(getId(`set${detail}`))) ?
    getId("successAlert").style.visibility = "visible" : getId("successAlert").style.visibility = "hidden";
};

//save lineup filtering used for both /save and /optimize routes. Action parameters denotes if either being saved or optimized.
let saveLineup = () => {
  lineupToSave = {};
  lineupToSave["rosterName"] = rosterName;
  lineupToSave["playersToAdd"] = playerList.filter(player => !currentPlayers.includes(player))
  lineupToSave["playersToDelete"] = currentPlayers.filter(player => !playerList.includes(player))
  return lineupToSave;
}
