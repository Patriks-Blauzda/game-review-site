const md = window.markdownit();

function wrapSelection(style) {
    let inputbox = document.getElementById("id_content");
    let output;

    let text = inputbox.value

    if(inputbox.value[inputbox.selectionEnd - 1] === " ") { inputbox.selectionEnd--; }

     output = (
         text.slice(0, inputbox.selectionStart) + style +
         text.slice(inputbox.selectionStart, inputbox.selectionEnd) + style +
         text.slice(inputbox.selectionEnd)
     );

    console.log(output);

    inputbox.value = output;
    render();

}

function stylize(style) {
    let selection = window.getSelection();
    let inputbox = document.getElementById("id_content");

    wrapSelection(style, selection);
}

function render() {

    let inputbox = document.getElementById("id_content");
    let outputbox = document.getElementById("output");

    const render = () => {
        outputbox.innerHTML = md.render(inputbox.value);
    }

    render();
}


window.onload = render;