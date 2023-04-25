function wrap(rangeList, style) {
    let textbox = document.getElementById("contentbox");
    let text = textbox.innerHTML;

    if(rangeList.length > 0) {
        let offset = 0;


        for(i = 0; i < rangeList.length; i++) {
            let range = rangeList[i]

             text = [
                text.slice(0, range.startOffset + offset), "<" + style + ">",
                text.slice(range.startOffset + offset, range.endOffset + offset), "</" + style + ">",
                text.slice(range.endOffset + offset)
            ].join('');

            offset += ("<" + style + "></" + style + ">").length
        }

        textbox.innerHTML = text;

    } else {
//        textbox.innerHTML = text + "<" + style + "></" + style + ">";
//
//        textbox.focus();
//
//        let range = document.createRange();
//        let selection = window.getSelection();
//
//        range.setStart(textbox.childNodes[2], textbox.innerHTML.length - ("</" + style + ">").length);
//        range.collapse(true);
//
//        selection.removeAllRanges();
//        selection.addRange(range);
    }

}

function stylize(style) {
    let selection = window.getSelection();
    let textbox = document.getElementById("contentbox");

    if(selection.focusNode.parentElement === textbox) {
        let rangeList = [];

        for(i = 0; i < selection.rangeCount; i++) {
            rangeList.push(selection.getRangeAt(i));
        }

        wrap(rangeList, style);


    } else {
        return 0;
    }
}