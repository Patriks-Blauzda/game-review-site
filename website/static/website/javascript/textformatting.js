function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break
            }
        }
    }
    return cookieValue;
}

// Wraps highlighted text with specified symbols or places symbols on cursor in text otherwise
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

// Uses specified strings containing symbols to call wrapSelection(), then renders changes made
function stylize(opener, closer = null) {
    let selection = window.getSelection();
    let inputbox = document.getElementById("input");

    if(closer != null) { wrapSelection(opener, closer); }
    else { wrapSelection(opener, opener); }

    render()
}

// Toggles formatting option buttons (link, image)
function toggleVisibility(elementid) {
    let options = document.getElementById("textformatoptions").children;

    for(let i = 0; i < options.length; i++) {
        if(options[i].id != elementid) { options[i].hidden = true; }
    }



    let element = document.getElementById(elementid);
    element.hidden = !element.hidden;
}

// Input formatted link into the textbox
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

// Stores image IDs to be deleted if user leaves page without publishing
const saved_images = [];

// Adds specified image to database through specified url using formdata
// After receiving the ID from backend, adds it to the saved_images array
// Outputs the formatted link to the image just added to the website
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

// Inputs any image link formatted to display the image
function pasteImage() {
    let imagelink = document.getElementById("formatimginput").value;

    if(imagelink) {
        wrapSelection("![](" + imagelink + ")", "");

        render();
    }
}

// Converts ShowdownJS formatting into html code
// Converted code is shown in the "output" html element to show a preview of the review
// Contains additional ShowdownJS formatting options (strikethrough, underline)
// "simpleLineBreaks" is used to create a line break with only one new line instead of the standard two
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

// unused(?)
function readFile() {

  if (!this.files || !this.files[0]) return;

  const FR = new FileReader();

  FR.addEventListener("load", function(evt) {
    wrapSelection( "<img src=" + evt.target.result + ">", "");
    render();
  });

  FR.readAsDataURL(this.files[0]);

}

// Confirmation popup for leaving
window.addEventListener("beforeunload", (event) => {
    if(!submitting) {
        event.returnValue = 'Are you sure you want to leave? Information will not be saved.';
    }
});

// If form is being submitted (review is published), makes sure saved images are not deleted upon leaving the page
var submitting = false;
function submitForm() { submitting = true; };

// If leaving the page without publishing the review, sends all temp image IDs to the backend through specified url
// Images are deleted upon leaving to remove unused images from the database automatically
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
