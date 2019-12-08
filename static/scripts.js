let flex_positions = ["RB", "WR", "TE"];
let roster_details = ["Type", "Rostered", "Starting", "Bench", "QB", "RB", "WR", "TE", "FLEX", "DEF", "K"];
let player_details = ['playerName', 'playerPosition', 'playerTeam', 'playerId'];

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
         // flex or normal
         if (numberConv(getId('FLEX')) > 0 && flex_positions.includes(position)) {
             getId('FLEX').innerHTML = numberConv(getId("FLEX")) - 1;
             addColor("FLEX", loadPage);
         } else {
             getId(position).innerHTML = numberConv(getId(position)) -1;
             addColor(position, loadPage);
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
};
