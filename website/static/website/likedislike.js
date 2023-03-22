function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break
            }
        }
    }
    return cookieValue;
}


function like(game_id, has_liked){
//    if(!location.href.includes(poll_id)){
//        const choiceEl = document.getElementById(choice)
//        let data = null
//        if (choiceEl){
//            data = {
//                choice: choiceEl.value,
//            }
//        }
        const url = "http://" + location.hostname + ":" + location.port + "/like/game/" + game_id + "/"
        fetch(url)
        .then(res => {
            if(res.status == 200) {
                const score = document.getElementById("score" + game_id);
                if(has_liked === "True") {
                    score.textContent = Number(score.textContent) - 1;
                    score.setAttribute();
                } else {
                    score.textContent = Number(score.textContent) + 1;
                }
            }

        });
//    }
}