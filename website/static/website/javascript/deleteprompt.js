function deletebuttonprompts() {
    let deletebuttons = document.querySelectorAll("#delete");

    for(let i = 0; i < deletebuttons.length; i++) {
        deletebuttons[i].onclick = prompt;
    }
}

function prompt() {
    if(confirm("Delete?") == false) { return false; }
}

window.onload = deletebuttonprompts;
