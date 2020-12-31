$(document).on("submit", "form.form-modal", function(event) {
    event.preventDefault();
    const form = $(this);
    const button = $("button[type=submit][clicked=true]");
    const board_id = button.val();
    if (button.attr("name") === "board_to_close") {
        button.prop("")
        $.post({
            url: "/deleteBoard", 
            data: JSON.stringify({"board_id": board_id}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        })
            .done(function(data) {
                $(`#board${board_id}`).prev().remove();
                $(`#board${board_id}`).modal('hide');
            });
    }
    else if(button.attr("name") === "board_to_edit") {
        const title = form.find("input").val();
        const desc = form.find("textarea").val();
        if (title === "") {
            $(`#boardEdit${board_id}`).modal('hide');
            // form.find("button.btn-primary").prop("disabled", false);
            $("nav").after("<header><div class=\"alert alert-danger border text-center alert-dismissible fade show\" role=\"alert\">Please Make Sure You Have a Title<button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\" aria-label=\"Close\"></button></div></header>");
            return false;
        }

        $.post({
            url: "/editBoard",
            data: JSON.stringify({"board_id": board_id, "title": title, "desc": desc}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        })
            .done(function(data) {
                $(`#boardEdit${board_id}`).modal('hide');
                $("button.btn-success").html(data.title);
                form.find("input").val(data.title);
                form.find("textarea").val(data.desc);
                let first_board = $(`#board${board_id}`);
                first_board.find("h5").html(data.title);
                first_board.find("p").html(data.desc);
            });
    }
    else {
        window.location.href = `/boards/${board_id}`;
    };
    $("button[type=submit][clicked=true]").attr("clicked", "false");
});

$(document).on("click", "form button[type=submit]", function() {
    $("button[type=submit]", $(this).parents("form")).removeAttr("clicked");
    $(this).attr("clicked", "true");
});

$(document).on("click", "button.btn-warning", function(event) {
    $(`#boardEdit${$(this).val()}`).modal("show");
})