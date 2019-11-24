invalid_input_message = display_message => {
    document.getElementById("invalid_input").innerHTML = display_message;
    document.getElementById("invalid_input").style.visibility = "visible";
    setTimeout(function() {
        document.getElementById("invalid_input").style.visibility = "hidden";
    }, 5000);
};