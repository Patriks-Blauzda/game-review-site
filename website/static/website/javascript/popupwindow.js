function displayModal() {
    document.getElementById("report-popup").style.display = "block";
}

function closeModal() {
    document.getElementById("report-popup").style.display = "none";
}

window.onclick = function(event) {
    if (event.target == document.getElementById("report-popup")) {
        document.getElementById("report-popup").style.display = "none";
    }

    if (document.getElementById("opt-other").checked) {
        document.getElementById("textbox-other").disabled = false;
        document.getElementById("textbox-other").style = "background-color: #fff;";
    } else {
        document.getElementById("textbox-other").disabled = true;
        document.getElementById("textbox-other").value = "";
        document.getElementById("textbox-other").style = "background-color: #f3f3f3;";
    }
}


