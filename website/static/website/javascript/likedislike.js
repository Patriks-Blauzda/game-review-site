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

function like_game(game_id){
        const url = "http://" + location.hostname + ":" + location.port + "/like/game/" + game_id + "/";
        fetch(url)
        .then(res => {
            if(res.status == 201) {
                res.json().then(
                    val => {
                        const score = document.getElementById("score" + game_id);
                        const like_button = document.getElementById("like" + game_id);
                        const dislike_button = document.getElementById("dislike" + game_id);

                        score.textContent = val.like;

                        if(val.has_liked) {
                            like_button.style.color = "#00b300";

                            if(dislike_button.style.color != "rgb(0, 0, 0)") {
                                dislike_button.style.color = "#000000";
                            }

                        } else {
                            like_button.style.color = "#000000";

                            if(dislike_button.style.color != "rgb(0, 0, 0)") {
                                dislike_button.style.color = "#000000";
                            }
                        }
                    }
                )
            }

        });
}

function dislike_game(game_id){
        const url = "http://" + location.hostname + ":" + location.port + "/dislike/game/" + game_id + "/";
        fetch(url)
        .then(res => {
            if(res.status == 201) {
                res.json().then(
                    val => {
                        const score = document.getElementById("score" + game_id);
                        const like_button = document.getElementById("like" + game_id);
                        const dislike_button = document.getElementById("dislike" + game_id);

                        score.textContent = val.like;

                        if(val.has_disliked) {
                            dislike_button.style.color = "#b30000";

                            if(like_button.style.color != "rgb(0, 0, 0)") {
                                like_button.style.color = "#000000";
                            }

                        } else {
                            dislike_button.style.color = "#000000";

                            if(like_button.style.color != "rgb(0, 0, 0)") {
                                like_button.style.color = "#000000";
                            }
                        }
                    }
                )
            }

        });
}


function like_post(post_id){
        const url = "http://" + location.hostname + ":" + location.port + "/like/post/" + post_id + "/";
        fetch(url)
        .then(res => {
            if(res.status == 201) {
                res.json().then(
                    val => {
                        const score = document.getElementById("score" + post_id);
                        const like_button = document.getElementById("like" + post_id);
                        const dislike_button = document.getElementById("dislike" + post_id);

                        score.textContent = val.like;

                        if(val.has_liked) {
                            like_button.style.color = "#00b300";

                            if(dislike_button.style.color != "rgb(0, 0, 0)") {
                                dislike_button.style.color = "#000000";
                            }

                        } else {
                            like_button.style.color = "#000000";

                            if(dislike_button.style.color != "rgb(0, 0, 0)") {
                                dislike_button.style.color = "#000000";
                            }
                        }
                    }
                )
            }

        });
}


function dislike_post(post_id){
        const url = "http://" + location.hostname + ":" + location.port + "/dislike/post/" + post_id + "/";
        fetch(url)
        .then(res => {
            if(res.status == 201) {
                res.json().then(
                    val => {
                        const score = document.getElementById("score" + post_id);
                        const like_button = document.getElementById("like" + post_id);
                        const dislike_button = document.getElementById("dislike" + post_id);

                        score.textContent = val.like;

                        if(val.has_disliked) {
                            dislike_button.style.color = "#b30000";

                            if(like_button.style.color != "rgb(0, 0, 0)") {
                                like_button.style.color = "#000000";
                            }

                        } else {
                            dislike_button.style.color = "#000000";

                            if(like_button.style.color != "rgb(0, 0, 0)") {
                                like_button.style.color = "#000000";
                            }
                        }
                    }
                )
            }

        });
}