function render() {
    let md = window.markdownit();

    let content = document.getElementById("content");

    for(let i = 0; i < content.childElementCount; i++) {
        let element = content.children[i];
        element.innerHTML = md.renderInline(element.innerHTML);
    }
}

window.onload = render;