// Responsible for displaying formatting used in reviews
function render() {
    let sd = new showdown.Converter();
    sd.setOption('strikethrough', true);
    sd.setOption('underline', true);
    sd.setOption('simpleLineBreaks', true);

    let content = document.getElementById("content");
    content.innerHTML = sd.makeHtml(content.innerHTML);
}

window.onload = render;