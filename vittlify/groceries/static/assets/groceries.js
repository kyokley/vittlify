/*jslint browser:true */
var tables = {};
var deletedTable;
var socket;
var node_port;
var socket_token;

function updateRow(item_id, list_id, checked, row_elem){
    jQuery.ajax({url: "/vittlify/item/" + item_id + "/",
                 type: "PUT",
                 dataType: "json",
                 data: {done: checked},
                 success: function(json){
                     console.log("Successfully handled put for " + item_id)
                 },
                 error: function(){
                     alert("An error has occurred");
                 }
    });
}

function updateRowHelper(item_id, list_id, checked, row_elem){
     console.log('Set item ' + item_id + ' to ' + checked);
     var table = tables["table-shopping_list-" + list_id];
     // var hiddenInput = document.getElementById('done-checked-' + item_id);
     // var button = document.getElementById('done-btn-' + list_id + '-' + item_id);
     // if(!button){
     //     debugger;
     // }
     // var link_btn = document.getElementById('link-' + item_id);
     var hiddenInput = row_elem.find("input")[0];
     var buttons = row_elem.find("button");
     var link_btn = buttons[0];
     var button = buttons[1];
     var row, rowNode;

     if(checked === "true" ||
             checked === "t" ||
             checked === "True"){
         row = table.row(row_elem);
         rowNode = row.node();

         row.remove().draw(false);
         deletedTable.row.add(rowNode).draw(false);
         button.innerHTML = "Undone";
         hiddenInput.value = false;
         link_btn.disabled = true;
         decrementShoppingListBadgeCount(list_id);
     } else {
         row = deletedTable.row(row_elem);
         rowNode = row.node();

         row.remove().draw(false);
         table.row.add(rowNode).draw(false);
         button.innerHTML = "Done";
         hiddenInput.value = true;
         link_btn.disabled = false;
         incrementShoppingListBadgeCount(list_id);
     }
}

function incrementShoppingListBadgeCount(list_id){
    var badge = document.getElementById("shopping-list-badge-" + list_id);
    var newCount = Number(badge.innerHTML) + 1;
    badge.innerHTML = newCount;
}

function decrementShoppingListBadgeCount(list_id){
    var badge = document.getElementById("shopping-list-badge-" + list_id);
    var newCount = Number(badge.innerHTML) - 1;
    badge.innerHTML = newCount;
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
                            comments: item_comments.value},
                     success: function(json){
                         item_name.value = "";
                         item_comments.value = "";
                         // We depend on the node server to actually call addItemHelper later
                     },
                     error: function(json){
                         alert("An error has occurred");
                     }
        });
    }
}

function addItemHelper(list_id, item_id, name, comments){
     var table = tables["table-shopping_list-" + list_id];
     var done_button = '<input type="hidden" id="done-checked-' + item_id + '" value=true />';
     done_button += '<button type="button" class="btn btn-info done-btn-class" id="done-btn-' + list_id + '-' + item_id + '">';
     done_button += 'Done';
     done_button += '</button>';

     var link_name = '<button type="button" class="btn btn-link" id="link-' + item_id + '" onclick="openItem(' + item_id + ', ' + list_id + ');">';
     link_name = link_name + name;
     if(comments){
          link_name += ' <span class="glyphicon glyphicon-plus-sign" aria-hidden="true"></span>';
     }
     link_name += '</button>';

     var row = table.row.add([link_name, done_button]).draw(false);
     var rowNode = row.node();

    var selectorID = "done-btn-" + list_id + "-" + item_id;
    table.$('button[id="' + selectorID + '"]').click(function(){
           var checked = document.getElementById("done-checked-" + item_id).value;
           var row_elem = $(this).parents('tr');
           updateRow(item_id, list_id, checked, row_elem);
    });
    incrementShoppingListBadgeCount(list_id);
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
                 data: {comments: edit_item_comment_elem.value},
                 success: function(json){
                     closeEditPanel(shopping_list_id);
                 },
                 error: function(){
                     alert("An error has occurred!");
                     closeEditPanel(shopping_list_id);
                 }
    });
}

function saveCommentsHelper(item_id, item_name, item_comments){
     var link_id = document.getElementById("link-" + item_id);
     if(item_comments){
         link_id.innerHTML = item_name + ' <span class="glyphicon glyphicon-plus-sign" aria-hidden="true"></span>';
     } else {
         link_id.innerHTML = item_name;
     }
}

function initSocketIO(){
    // WebSocket test settings
    socket.on("connect", function(){
        console.log("connect");
        socket.emit('send_token', socket_token, function(data){
            console.log(socket_token);
            console.log(data);
        });
    });

    socket.on("message", function(message) {
        console.log(message.message);
    });

    socket.on("refresh", function(message) {
        console.log(message.message);
        location.reload(true);
    });

    socket.on("asyncUpdateRow_" + socket_token, function(data){
        console.log("asyncUpdateRow");
        console.log(data);
        var table;
        if(data.checked === "True"){
            table = tables["table-shopping_list-" + data.list_id];
        } else {
            table = deletedTable;
        }
        var row_elem = table.$("#done-btn-" + data.list_id + "-" + data.item_id).parents("tr");
        console.log("updateRowHelper");
        updateRowHelper(data.item_id, data.list_id, data.checked, row_elem);

    });

    socket.on("asyncComments_" + socket_token, function(data){
        console.log("asyncComments");
        console.log(data);
        saveCommentsHelper(data.item_id, data.name, data.comments);
        console.log("saveCommentsHelper " + data);
    });

    socket.on("asyncAddItem_" + socket_token, function(data){
        console.log("addItemHelper");
        console.log(data);
        addItemHelper(data.list_id, data.item_id, data.name, data.comments);
    });
}
