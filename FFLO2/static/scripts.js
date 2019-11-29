let flex_positions = ["RB", "WR", "TE"];
let roster_details = ["Rostered", "Starting", "Bench", "QB", "RB", "WR", "TE", "FLEX", "DEF", "K"];

//factor out so many document.getElementById calls
getId = Id => {
    return document.getElementById(Id);
}

numberConv = elem => {
    return parseInt(elem.innerHTML);
}

let invalid_input_message = display_message => {
    document.getElementById("invalid_input").innerHTML = display_message;
    document.getElementById("invalid_input").style.visibility = "visible";
    setTimeout(function() {
        document.getElementById("invalid_input").style.visibility = "hidden";
    }, 5000);
};

let counterChange = (position, action) => {

    action === 'add' ? getId('Rostered').innerHTML = numberConv(getId('Rostered')) + 1 :
    getId('Rostered').innerHTML = numberConv(getId('Rostered')) - 1;

    addColor('Rostered');

    if (action === 'remove') {
         //bench or starting
         if (numberConv(getId("Bench")) > 0) {
             getId('Bench').innerHTML = numberConv(getId("Bench")) - 1;
             addColor('Bench');
         } else if (numberConv(getId('Bench')) === 0) {
             getId('Starting').innerHTML = numberConv(getId('Starting')) - 1;
             addColor("Starting");
         }
         // flex or normal
         if (numberConv(getId('Flex')) > 0 && flex_positions.includes(position)) {
             getId('FLEX').innerHTML = numberConv(getId("FLEX")) - 1;
             addColor("FLEX");
         } else {
             getId(position).innerHTML = numberConv(getId(position)) -1;
             addColor(position);
         }
    }
    else if (action === 'add') {
        if (numberConv(getId('Starting')) >= numberConv(getId('setStarting'))) {
            getId("Bench").innerHTML = numberConv(getId('Bench')) + 1;
            addColor('Bench');
        } else {
            getId("Starting").innerHTML = numberConv(getId('Starting')) + 1;
            addColor('Starting');
        }

        console.log(numberConv(getId('FLEX')))
        console.log(numberConv(getId(position)))

        if (numberConv(getId(position)) >= numberConv(getId("set" + position)) &&
        numberConv(getId('FLEX')) < numberConv(getId('setFLEX')) &&
        flex_positions.includes(position)) {

            getId("FLEX").innerHTML = numberConv(getId('FLEX')) + 1;
            addColor('FLEX');
        } else if (numberConv(getId(position)) < numberConv(getId('set' + position))) {
            getId(position).innerHTML = numberConv(getId(position)) + 1;
            addColor(position);
        }
    }
};