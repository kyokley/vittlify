var tables = {};
var token;

function updateRow(item_id, checked){
    jQuery.ajax({url: "/vittlify/item/" + item_id + "/",
                 type: "PUT",
                 dataType: "json",
                 data: {done: checked,
                        csrfmiddlewaretoken: token},
                 success: function(json){
                     console.log('Set item ' + item_id + ' to ' + checked)
                 },
                 error: function(){
                     console.log("Failed");
                 }
    });
}

function addItem(list_id){
    var item_name = document.getElementById("new-item-name-" + list_id);
    var item_comments = document.getElementById("new-item-comment-" + list_id);
    jQuery.ajax({url: "/vittlify/item/",
                 type: "POST",
                 dataType: "json",
                 data: {shopping_list_id: list_id,
                        name: item_name.value,
                        comments: item_comments.value,
                        csrfmiddlewaretoken: token},
                 success: function(json){
                     var table = tables["table-shopping_list-" + list_id];
                     var checkbox = '<input type="checkbox" id="checkbox-' + list_id + '-' + json.pk + '" name="checkbox-' + json.name + '" />';
                     table.row.add([item_name.value, checkbox]).draw();
                     item_name.value = "";
                     item_comments.value = "";

                     var selectorID = "checkbox-" + list_id + "-" + json.pk;
                     jQuery('input[id=' + selectorID + ']').click(function(){
                         var checked = this.checked;
                         updateRow('{{ csrf_token }}', json.pk, checked);
                     });
                 },
                 error: function(){
                     console.log("Failed");
                 }
    });
}

function openItem(item_id, shopping_list_id){
    var shopping_list_div = document.getElementById("div-" + shopping_list_id);
    var add_item_panel = document.getElementById("add-item-panel-" + shopping_list_id);
    var edit_item_panel = document.getElementById("edit-item-panel-" + shopping_list_id);
    var edit_item_id_elem = document.getElementById("edit-item-id");

    edit_item_id_elem.value = item_id;
    shopping_list_div.style.display = "none";
    add_item_panel.style.display = "none";
    edit_item_panel.style.display = "block";

    jQuery.ajax({url: "/vittlify/item/" + item_id + "/",
                 type: "GET",
                 dataType: "json",
                 success: function(json){
                     var edit_item_name_elem = document.getElementById("edit-item-name-" + shopping_list_id);
                     var edit_item_comment_elem = document.getElementById("edit-item-comment-" + shopping_list_id);

                     edit_item_name_elem.value = json.name;
                     edit_item_comment_elem.value = json.comments;
                 },
                 error: function(){
                     alert("An error has occurred!");
                     closeEditPanel(shopping_list_id);
                 }
    });
}

function closeEditPanel(shopping_list_id){
    var shopping_list_div = document.getElementById("div-" + shopping_list_id);
    var add_item_panel = document.getElementById("add-item-panel-" + shopping_list_id);
    var edit_item_panel = document.getElementById("edit-item-panel-" + shopping_list_id);
    var edit_item_id_elem = document.getElementById("edit-item-id");

    edit_item_id_elem.value = "";
    shopping_list_div.style.display = "block";
    add_item_panel.style.display = "block";
    edit_item_panel.style.display = "none";
}

function saveItem(shopping_list_id){
     var edit_item_comment_elem = document.getElementById("edit-item-comment-" + shopping_list_id);
    var edit_item_id_elem = document.getElementById("edit-item-id");

    var item_id = edit_item_id_elem.value;

    jQuery.ajax({url: "/vittlify/item/" + item_id + "/",
                 type: "PUT",
                 dataType: "json",
                 data: {comments: edit_item_comment_elem.value,
                        csrfmiddlewaretoken: token},
                 success: function(json){
                     var link_id = document.getElementById("link-" + json.pk);
                     if(edit_item_comment_elem.value){
                         link_id.innerHTML = json.name + ' <span class="glyphicon glyphicon-plus-sign" aria-hidden="true"></span>';
                     } else {
                         link_id.innerHTML = json.name;
                     }
                     closeEditPanel(shopping_list_id);
                 },
                 error: function(){
                     alert("An error has occurred!");
                     closeEditPanel(shopping_list_id);
                 }
    });
}
