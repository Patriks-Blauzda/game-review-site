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

function like_game(game_id, likes_count, has_liked){
        const url = "http://" + location.hostname + ":" + location.port + "/like/game/" + game_id + "/";
        fetch(url)
        .then(res => {
            if(res.status == 200) {
                const score = document.getElementById("score" + game_id);
                const like_button = document.getElementById("like" + game_id);
                const dislike_button = document.getElementById("dislike" + game_id);

                if(has_liked === "True") {
                    if(likes_count > Number(score.textContent)) {
                        score.textContent = Number(score.textContent) + 1;
                        like_button.style.color = "#00b300";

                        if(dislike_button.style.color != "rgb(0, 0, 0)") {
                            dislike_button.style.color = "#000000";
                            score.textContent = Number(score.textContent) + 1;
                        }

                    } else {
                        score.textContent = Number(score.textContent) - 1;
                        like_button.style.color = "#000000";
                    }

                } else {
                    if(likes_count < Number(score.textContent)) {
                        score.textContent = Number(score.textContent) - 1;
                        like_button.style.color = "#000000";
                    } else {
                        score.textContent = Number(score.textContent) + 1;
                        like_button.style.color = "#00b300";

                        if(dislike_button.style.color != "rgb(0, 0, 0)") {
                            dislike_button.style.color = "#000000";
                            score.textContent = Number(score.textContent) + 1;
                        }
                    }
                }
            }

        });
}


function dislike_game(game_id, likes_count, has_disliked){
        const url = "http://" + location.hostname + ":" + location.port + "/dislike/game/" + game_id + "/";
        fetch(url)
        .then(res => {
            if(res.status == 200) {
                const score = document.getElementById("score" + game_id);
                const dislike_button = document.getElementById("dislike" + game_id)
                const like_button = document.getElementById("like" + game_id)

                if(has_disliked === "True") {
                    if(likes_count < Number(score.textContent)) {
                        score.textContent = Number(score.textContent) - 1;
                        dislike_button.style.color = "#b30000";

                        if(like_button.style.color != "rgb(0, 0, 0)") {
                            like_button.style.color = "#000000";
                            score.textContent = Number(score.textContent) - 1;
                        }

                    } else {
                        score.textContent = Number(score.textContent) + 1;
                        dislike_button.style.color = "#000000";
                    }

                } else {
                    if(likes_count > Number(score.textContent)) {
                        score.textContent = Number(score.textContent) + 1;
                        dislike_button.style.color = "#000000";
                    } else {
                        score.textContent = Number(score.textContent) - 1;
                        dislike_button.style.color = "#b30000";

                        if(like_button.style.color != "rgb(0, 0, 0)") {
                            like_button.style.color = "#000000";
                            score.textContent = Number(score.textContent) - 1;
                        }
                    }
                }
            }

        });
}


function like_post(post_id, likes_count, has_liked){
        const url = "http://" + location.hostname + ":" + location.port + "/like/post/" + post_id + "/";
        fetch(url)
        .then(res => {
            if(res.status == 200) {
                const score = document.getElementById("score" + post_id);
                const like_button = document.getElementById("like" + post_id);
                const dislike_button = document.getElementById("dislike" + post_id);

                if(has_liked === "True") {
                    if(likes_count > Number(score.textContent)) {
                        score.textContent = Number(score.textContent) + 1;
                        like_button.style.color = "#00b300";

                        if(dislike_button.style.color != "rgb(0, 0, 0)") {
                            dislike_button.style.color = "#000000";
                            score.textContent = Number(score.textContent) + 1;
                        }

                    } else {
                        score.textContent = Number(score.textContent) - 1;
                        like_button.style.color = "#000000";
                    }

                } else {
                    if(likes_count < Number(score.textContent)) {
                        score.textContent = Number(score.textContent) - 1;
                        like_button.style.color = "#000000";
                    } else {
                        score.textContent = Number(score.textContent) + 1;
                        like_button.style.color = "#00b300";

                        if(dislike_button.style.color != "rgb(0, 0, 0)") {
                            dislike_button.style.color = "#000000";
                            score.textContent = Number(score.textContent) + 1;
                        }
                    }
                }
            }

        });
}


function dislike_post(post_id, likes_count, has_disliked){
        const url = "http://" + location.hostname + ":" + location.port + "/dislike/post/" + post_id + "/";
        fetch(url)
        .then(res => {
            if(res.status == 200) {
                const score = document.getElementById("score" + post_id);
                const dislike_button = document.getElementById("dislike" + post_id)
                const like_button = document.getElementById("like" + post_id)

                if(has_disliked === "True") {
                    if(likes_count < Number(score.textContent)) {
                        score.textContent = Number(score.textContent) - 1;
                        dislike_button.style.color = "#b30000";

                        if(like_button.style.color != "rgb(0, 0, 0)") {
                            like_button.style.color = "#000000";
                            score.textContent = Number(score.textContent) - 1;
                        }

                    } else {
                        score.textContent = Number(score.textContent) + 1;
                        dislike_button.style.color = "#000000";
                    }

                } else {
                    if(likes_count > Number(score.textContent)) {
                        score.textContent = Number(score.textContent) + 1;
                        dislike_button.style.color = "#000000";
                    } else {
                        score.textContent = Number(score.textContent) - 1;
                        dislike_button.style.color = "#b30000";

                        if(like_button.style.color != "rgb(0, 0, 0)") {
                            like_button.style.color = "#000000";
                            score.textContent = Number(score.textContent) - 1;
                        }
                    }
                }
            }

        });
}