const id = Date.now();
console.log(id)
var modal_id_counter = 0

$('#user_input').on("keydown", function (e) {
    if (e.keyCode === 13) {
        postMsg(false);
    }
});

function postMsg(initial) {
    var msg;
    if (initial === false) {
        var user_marker = document.createElement("DIV");
        user_marker.innerText = "You";
        var user_node = document.createElement("DIV");
        user_node.appendChild(user_marker);
        user_node.classList.add("ui", "basic", "fitted", "segment");
        user_node.style = "text-align: left; margin: 3px;";
        document.getElementById("textdiv").appendChild(user_node);

        msg = document.getElementById("user_input").value;
        var message_node = document.createElement("DIV");
        message_node.appendChild(document.createTextNode(msg));
        message_node.classList.add("ui", "compact", "message");
        message_node.style = "background-color: white; text-color: b79a33; max-width: 80%;";
        var segment_node = document.createElement("DIV");
        segment_node.appendChild(message_node);
        segment_node.classList.add("ui", "basic", "fitted", "segment");
        segment_node.style = "text-align: left; margin: 3px;";
        document.getElementById("textdiv").appendChild(segment_node);
        document.getElementById("user_input").value = "";
    }
    else {
        msg = "initmsg";
    }

    var xhr = new XMLHttpRequest();
    xhr.open("POST", get_webhook_location(), true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {

            var json = JSON.parse(xhr.responseText);

            var bot_marker = document.createElement("DIV");
            bot_marker.innerText = "Deltabot";
            bot_marker.style = "color: #b79a33;";
            var bot_node = document.createElement("DIV");
            bot_node.appendChild(bot_marker);
            bot_node.classList.add("ui", "basic", "fitted", "segment");
            bot_node.style = "text-align: right; margin: 3px;";
            document.getElementById("textdiv").appendChild(bot_node);

            for (var i = 0; i < json.length; i++) {
                var segment_node = document.createElement("DIV");
                if (json[i]['text'] === "") {
                    segment_node.classList.add("ui", "hidden", "divider");
                }
                else if (json[i]['text'].startsWith("!img ")) {
                    const img_src = json[i]["text"].split(" ")[1]

                    var modal_node = document.createElement("DIV")
                    modal_node.classList.add("ui", "modal")
                    modal_node.setAttribute("id", "modal_" + modal_id_counter.toString())
                    var modal_image_node = document.createElement("IMG")
                    modal_image_node.src = img_src
                    modal_node.appendChild(modal_image_node)
                    segment_node.appendChild(modal_node)

                    var image_node = document.createElement("IMG");
                    image_node.src = img_src
                    image_node.style = "max-width: 80%"
                    image_node.onload = scroll_to_bottom
                    image_node.setAttribute("onclick", "open_modal("+modal_id_counter.toString()+")")
                    segment_node.appendChild(image_node);
                    segment_node.classList.add("ui", "basic", "fitted", "segment");
                    segment_node.style = "text-align: right; margin: 3px;";

                    modal_id_counter += 1
                }
                else {
                    var message_node = document.createElement("DIV");
                    message_node.appendChild(document.createTextNode(json[i]['text']));
                    message_node.classList.add("ui", "compact", "message");
                    message_node.style = "background-color: #b79a33; max-width: 80%;";
                    segment_node.appendChild(message_node);
                    segment_node.classList.add("ui", "basic", "fitted", "segment");
                    segment_node.style = "text-align: right; margin: 3px;";
                }
                document.getElementById("textdiv").appendChild(segment_node);
            }
            scroll_to_bottom()
        }
    };
    var data = JSON.stringify({"sender": id, "message": msg});
    xhr.send(data);
    scroll_to_bottom()
}

function scroll_to_bottom() {
    document.getElementById("chatbox_bottom").scrollIntoView()
}

function open_modal(modal_index) {
    $('#modal_' + modal_index).modal('show')
}

postMsg(true);
