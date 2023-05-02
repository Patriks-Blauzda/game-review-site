const md = require('markdown-it');

function wrapSelection(style) {
    let inputbox = document.getElementById("input");
    let output;

    let text = inputbox.value

    if(inputbox.value[inputbox.selectionEnd - 1] === " ") { inputbox.selectionEnd--; }

     output = (
         text.slice(0, inputbox.selectionStart) + style +
         text.slice(inputbox.selectionStart, inputbox.selectionEnd) + style +
         text.slice(inputbox.selectionEnd)
     );

    inputbox.value = output;
    render();

}

function stylize(style) {
    let selection = window.getSelection();
    let inputbox = document.getElementById("input");

    if(selection.focusNode == inputbox) {
        wrapSelection(style, selection);
    }
}

function render() {
    let md = window.markdownit();

    let inputbox = document.getElementById("input");
    let outputbox = document.getElementById("output");

    const render = () => {
        outputbox.innerHTML = md.renderInline(inputbox.value);
    }

    render();
}


window.onload = render;
