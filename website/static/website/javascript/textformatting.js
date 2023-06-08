function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Checking if the cookie substring matches what we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break
            }
        }
    }
    return cookieValue;
}


function wrapSelection(opener, closer) {
    let inputbox = document.getElementById("input");
    let output;

    let text = inputbox.value

    if(inputbox.value[inputbox.selectionEnd - 1] === " ") { inputbox.selectionEnd--; }

     output = (
         text.slice(0, inputbox.selectionStart) + opener +
         text.slice(inputbox.selectionStart, inputbox.selectionEnd) + closer +
         text.slice(inputbox.selectionEnd)
     );

    inputbox.value = output;

}

function stylize(opener, closer = null) {
    let selection = window.getSelection();
    let inputbox = document.getElementById("input");

    if(closer != null) { wrapSelection(opener, closer); }
    else { wrapSelection(opener, opener); }

    render()
}


function toggleVisibility(elementid) {
    let options = document.getElementById("textformatoptions").children;

    for(let i = 0; i < options.length; i++) {
        if(options[i].id != elementid) { options[i].hidden = true; }
    }



    let element = document.getElementById(elementid);
    element.hidden = !element.hidden;
}


function pasteLink() {
    let link = document.getElementById("formatlinkinput").value;
    let text = document.getElementById("formatlinktextinput").value;

    if(link) {
        if(text) {
            wrapSelection("[" + text + "](" + link + ")", "");
        } else {
            wrapSelection("<" + link + ">", "");
        }

        render();
    }
}

const saved_images = [];

function uploadImage() {
    const url = "http://" + location.hostname + ":" + location.port + "/addtempimage/";

    let img = document.getElementById("uploadedimage");

    if (!img.files[0]) return;

    const data = new FormData();
    data.append("image", img.files[0]);

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: data,
        credentials: 'same-origin',
    }).then(
        res => res.json()
    ).then(
        data => {
            wrapSelection("![](http://" + location.hostname + ":" + location.port + "/image/" + data.image_id + ")", "");
            render();
            saved_images.push(data.image_id);
        }
    );

}


function pasteImage() {
    let imagelink = document.getElementById("formatimginput").value;

    if(imagelink) {
        wrapSelection("![](" + imagelink + ")", "");

        render();
    }
}


function render() {
    let sd = new showdown.Converter();
    sd.setOption('strikethrough', true);
    sd.setOption('underline', true);
    sd.setOption('simpleLineBreaks', true);

    let inputbox = document.getElementById("input");
    let outputbox = document.getElementById("output");

    const render = () => {
        outputbox.innerHTML = sd.makeHtml(inputbox.value);
    }

    render();
}


window.onload = render;


function readFile() {

  if (!this.files || !this.files[0]) return;

  const FR = new FileReader();

  FR.addEventListener("load", function(evt) {
    wrapSelection( "<img src=" + evt.target.result + ">", "");
    render();
  });

  FR.readAsDataURL(this.files[0]);

}


window.addEventListener("beforeunload", (event) => {
    if(!submitting) {
        event.returnValue = 'Are you sure you want to leave? Information will not be saved.';
    }
});


var submitting = false;
function submitForm() { submitting = true; };

window.onunload = function () {
    if(!submitting) {
        const data = new FormData();
        data.append("images", saved_images);

        fetch("http://" + location.hostname + ":" + location.port + "/abortpostcreation/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: data,
            credentials: 'same-origin',
            keepalive: true
        });
    }
}
