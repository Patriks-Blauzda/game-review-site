function render() {
    let sd = new showdown.Converter();
    sd.setOption('strikethrough', true);
    sd.setOption('underline', true);
    sd.setOption('simpleLineBreaks', true);

    let content = document.getElementById("content");

    for(let i = 0; i < content.childElementCount; i++) {
        let element = content.children[i];
        element.innerHTML = sd.makeHtml(element.innerHTML);
    }
}

window.onload = render;