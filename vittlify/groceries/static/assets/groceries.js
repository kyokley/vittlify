/*jslint browser:true */
var tables = {};
var token;
var deletedTable;

function updateRow(item_id, list_id, checked, row_elem){
    jQuery.ajax({url: "/vittlify/item/" + item_id + "/",
                 type: "PUT",
                 dataType: "json",
                 data: {done: checked,
                        csrfmiddlewaretoken: token},
                 success: function(json){
                     console.log('Set item ' + item_id + ' to ' + checked);
                     var table = tables["table-shopping_list-" + list_id];
                     var hiddenInput = document.getElementById('done-checked-' + item_id);
                     var button = document.getElementById('done-btn-' + list_id + '-' + item_id);
                     var link_btn = document.getElementById('link-' + item_id);
                     var row, rowNode;

                     if(checked === "true"){
                         row = table.row(row_elem);
                         rowNode = row.node();

                         row.remove();
                         deletedTable.row.add(rowNode).draw();
                         button.innerHTML = "Undone";
                         hiddenInput.value = "false";
                         link_btn.disabled = true;
                     } else {
                         row = deletedTable.row(row_elem);
                         rowNode = row.node();

                         row.remove();
                         table.row.add(rowNode).draw();
                         button.innerHTML = "Done";
                         hiddenInput.value = "true";
                         link_btn.disabled = false;
                     }
                 },
                 error: function(){
                     alert("An error has occurred");
                 }
    });
}

function addItem(list_id){
    var item_name = document.getElementById("new-item-name-" + list_id);
    var item_comments = document.getElementById("new-item-comment-" + list_id);
    if(!item_name.value){
        alert('Name is a required field for new items');
    } else {
        jQuery.ajax({url: "/vittlify/item/",
                     type: "POST",
                     dataType: "json",
                     data: {shopping_list_id: list_id,
                            name: item_name.value,
                            comments: item_comments.value,
                            csrfmiddlewaretoken: token},
                     success: function(json){
                         var table = tables["table-shopping_list-" + list_id];
                         var done_button = '<input type="hidden" id="done-checked-' + json.pk + '" value=true />';
                         done_button += '<button type="button" class="btn btn-info" id="done-btn-' + json.shopping_list_id + '-' + json.pk + '">';
                         if(json.done){
                             done_button += 'Undone';
                         } else {
                             done_button += 'Done';
                         }
                         done_button += '</button>';

                         var link_name = '<button type="button" class="btn btn-link" id="link-' + json.pk + '" onclick="openItem(' + json.pk + ', ' + json.shopping_list_id + ');">';
                         link_name = link_name + json.name;
                         if(json.comments){
                              link_name += ' <span class="glyphicon glyphicon-plus-sign" aria-hidden="true"></span>';
                         }
                         link_name += '</button>';

                         table.row.add([link_name, done_button]).draw();
                         item_name.value = "";
                         item_comments.value = "";

                         var selectorID = "done-btn-" + json.shopping_list_id + "-" + json.pk;
                        jQuery('button[id="' + selectorID + '"]').click(function(){
                                // var item_id = this.id.match('[0-9]+$');
                                // var list_id = this.id.match('[0-9]+');
                                var checked = document.getElementById("done-checked-" + json.pk).value;
                                var row_elem = jQuery(this).parents('tr');
                                updateRow(json.pk, json.shopping_list_id, checked, row_elem);
                        });
                     },
                     error: function(json){
                         alert("An error has occurred");
                     }
        });
    }
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
