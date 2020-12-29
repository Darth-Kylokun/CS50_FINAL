$(function() {
    $(".col").sortable({
        connectWith: ".col",
        handle: ".card-body",
        cancel: ".toggle",
        placeholder: ".placeholder"
    });
});

$(document).on("click", ".col", function() {
    let icon = $(this);
    icon.closest(".card").find("card-title").toggle();
});

$(document).on("sortreceive", ".col", function(event, ui) {
    event.preventDefault();
        const word_to_int = {
            "one": "1",
            "two": "2",
            "three": "3"
        };
        $.post({
            url: "/modListPos",
            data: JSON.stringify({"list_id": ui.item.attr("id"), "new_col_id": word_to_int[ui.item.parent().attr("id")]}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
});

$(document).on("submit", "form", function(event) {
    event.preventDefault();
        
    alert("uwU");

    const form = $(this);

    if (form.attr("id") === "create_list") {
        form.find("button.btn-primary").prop("disabled", true);
        const title = form.find("input").val();

        if (title === "") {
            $(`#listCreationModal`).modal('hide');
            form.find("button.btn-primary").prop("disabled", false);
            $("nav").after("<header><div class=\"alert alert-danger border text-center alert-dismissible fade show\" role=\"alert\">Please Provide a Title<button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\" aria-label=\"Close\"></button></div></header>")
            return false;
        }

        const desc = form.find("textarea").val();

        $.post({
            url: form.attr("action"),
            data: JSON.stringify({"title": title, "description": desc}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        })
            .done(function (data) {
                $("#listCreationModal").modal('hide');

                form.find("button.btn-primary").prop("disabled", false);
                form.find("input").val("");
                form.find("textarea").val("");

                const card_to_add = ` \
                <div class="modal fade" id="list${data.list_id}" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="list${data.list_id}Title" aria-hidden="true">
                        <div class="modal-dialog">
                            <form action="/modifyList/${data.list_id}" method="POST" class="modify_list">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title" id="list${data.list_id}Title">Edit Post:</h5>
                                    </div>
                                    <div class="modal-body">
                                        <div class="mb-3">
                                            <label for="titleEdit" class="form-label">Title</label>
                                            <input type="text" class="form-control form-control-lg" id="titleEdit" name="title_edit" placeholder="Title" value="${data.list_title}" maxlength="255">
                                        </div>
                                        <div class="mb-3">
                                            <label for="descriptionEdit" class="form-label">Description</label>
                                            <textarea class="form-control form-control-lg" id="descriptionEdit" name="description_edit" placesholder="Description" maxlength="2048">${data.list_desc}</textarea>
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                        <button type="submit" class="btn btn-danger" name="list_id_to_delete" value="${data.list_id}">Delete</button>
                                        <button type="submit" class="btn btn-primary" name="list_id" value="${data.list_id}">Edit</button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                        <div class="card" id="${data.list_id}">
                        <div class="card-body">
                            <h5 class="card-title">${data.list_title}</h5><span class="toggle"></span>
                            <p class="card-text">${data.list_desc}</p>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-secondary mb-3" data-bs-toggle="modal" data-bs-target="#list${data.list_id}">Modify</button>
                        </div>
                    </div>
                `

                $("#one").append(card_to_add);
                $("form").bind("submit");
            });
    }
    else {
        const button = $("button[type=submit][clicked=true]");
        button.prop("disabled", true)
        form.find("button.btn-primary").prop("disabled", true);
        form.find("button.btn-danger").prop("disabled", true);
        const list_id = button.val();
        if (button.attr("name") === "list_id_to_delete") {
            $.post({
                url: form.attr("action"),
                data: JSON.stringify({"list_id": list_id, "to_delete": true}),
                contentType: "application/json; charset=utf-8",
                dataType: "json"
            })
                .done(function(data) {
                    $(`#list${list_id}`).modal('hide');
                    form.find("button.btn-primary").prop("disabled", false);
                    form.find("button.btn-danger").prop("disabled", false);

                    $(`#${list_id}`).remove();
                });
        }
        else {
            const title = form.find("input").val();
            const desc = form.find("textarea").val();

            alert(`${list_id} ${title} ${desc}`);

            if (title === "") {
                $(`#list${list_id}`).modal('hide');
                form.find("button.btn-primary").prop("disabled", false);
                $("nav").after("<header><div class=\"alert alert-danger border text-center alert-dismissible fade show\" role=\"alert\">Please Make Sure You Have a Title<button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\" aria-label=\"Close\"></button></div></header>");
                return false;
            }
            $.post({
                url: form.attr("action"),
                data: JSON.stringify({"list_id": list_id, "to_delete": false, "title": title, "desc": desc}),
                contentType: "application/json; charset=utf-8",
                dataType: "json"
            })
                .done(function() {
                    $(`#list${list_id}`).modal('hide');
                    form.find("button.btn-primary").prop("disabled", false);
                    form.find("button.btn-danger").prop("disabled", false);

                    let card = $(`#${list_id}`);
                    card.find("h5").text(title);
                    card.find("p").text(desc);
                });
        }
        $("button[type=submit][clicked=true]").attr("clicked", "false");
    }
});

$(document).on("click", "form button[type=submit]", function() {
    $("button[type=submit]", $(this).parents("form")).removeAttr("clicked");
    $(this).attr("clicked", "true");
});
