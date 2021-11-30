/*jslint browser:true */
var tables = {};
var deletedTable;
var socket;
var node_port;
var socket_token;

function updateRow(item_id,
                   list_id,
                   checked,
                   row_elem,
                   category_id){
    jQuery.ajax({url: "/vittlify/item/" + item_id + "/",
                 type: "PUT",
                 dataType: "json",
                 data: {done: checked,
                        category_id: category_id},
                 statusCode: {
                     403: function() {
                         alert("You don't have access to this list.\nPlease try refreshing the page.");
                     },
                     404: function() {
                         alert("Could not find the list.\nPlease try refreshing the page.");
                     }
                 },
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
     if(!table){
         return;
     }
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
    var item_category = document.getElementById("new-item-category-" + list_id);

    if(!item_name.value){
        alert('Name is a required field for new items');
    } else {
        jQuery.ajax({url: "/vittlify/item/",
                     type: "POST",
                     dataType: "json",
                     data: {shopping_list_id: list_id,
                            name: item_name.value,
                            comments: item_comments.value,
                            category_id: item_category.value},
                     statusCode: {
                         403: function() {
                             alert("You don't have access to this list.\nPlease try refreshing the page.");
                         }
                     },
                     success: function(json){
                         item_name.value = "";
                         item_comments.value = "";
                         item_category.value = "";
                         var saved_message = jQuery('#saved-item-' + list_id);
                         var saved_message_field = saved_message[0];
                         saved_message_field.innerText = 'Item added successfully';

                         saved_message.fadeOut(2000, function() {
                             saved_message_field.innerText = "";
                             saved_message.show(0);
                         });
                         // We depend on the node server to actually call addItemHelper later
                     },
                     error: function(json){
                         alert("An error has occurred");
                     }
        });
    }
}

function addItemHelper(list_id, item_id, name, comments, category_id, category_name){
     var table = tables["table-shopping_list-" + list_id];
     if(table){
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

         var category = '<span id="item-category-name-' + item_id + '">' + category_name + '</span>';
         category += '<span class="hidden-span" id="item-category-id-' + item_id + '">' + category_id + '</span>';

         var row = table.row.add([link_name, category, done_button]).draw(false);
         var rowNode = row.node();

        var selectorID = "done-btn-" + list_id + "-" + item_id;
        table.$('button[id="' + selectorID + '"]').click(function(){
               var checked = document.getElementById("done-checked-" + item_id).value;
               var row_elem = $(this).parents('tr');
               var category_id = document.getElementById("item-category-id-" + item_id).innerHTML;
               updateRow(item_id,
                         list_id,
                         checked,
                         row_elem,
                         category_id);
        });
        incrementShoppingListBadgeCount(list_id);
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
                     var edit_item_category = document.getElementById("category-item-" + shopping_list_id);

                     edit_item_name_elem.value = json.name;
                     edit_item_comment_elem.value = json.comments;

                     if(json.category_id){
                         var found = false;
                         for(i=0; i < edit_item_category.length; i++){
                             if(edit_item_category.options[i].value == json.category_id){
                                 edit_item_category.options[i].selected = true;
                                 found = true;
                             }
                         }

                         if(!found){
                             var opt = document.createElement('option');
                             opt.appendChild(document.createTextNode(json.category_name));
                             opt.value = json.category_id;
                             edit_item_category.appendChild(opt);
                             edit_item_category.options[edit_item_category.length].selected = true;
                         }
                     } else {
                         edit_item_category.options[0].selected = true;
                     }
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
    var edit_item_category = document.getElementById("category-item-" + shopping_list_id);
    var category_id;
    if(edit_item_category.value){
        category_id = edit_item_category.value;
    } else {
        category_id = '';
    }

    var item_id = edit_item_id_elem.value;

    jQuery.ajax({url: "/vittlify/item/" + item_id + "/",
                 type: "PUT",
                 dataType: "json",
                 data: {comments: edit_item_comment_elem.value,
                        category_id: category_id},
                 statusCode: {
                     403: function() {
                         alert("You don't have access to this list.\nPlease try refreshing the page.");
                     }
                 },
                 success: function(json){
                     closeEditPanel(shopping_list_id);
                 },
                 error: function(){
                     alert("An error has occurred!");
                     closeEditPanel(shopping_list_id);
                 }
    });
}

function saveCommentsHelper(item_id,
                            list_id,
                            item_name,
                            item_comments){
     var innerHTML;
     var table = tables["table-shopping_list-" + list_id];

     if(!table){
         return;
     }

     var link_id = table.$("#link-" + item_id);
     if(link_id){
         if(item_comments){
             innerHTML = item_name + ' <span class="glyphicon glyphicon-plus-sign" aria-hidden="true"></span>';
         } else {
             innerHTML = item_name;
         }
     }
     link_id.html(innerHTML);
}

function saveCategoryHelper(item_id,
                            list_id,
                            item_category_id,
                            item_category_name){
     var innerHTML;
     var table = tables["table-shopping_list-" + list_id];

     if(!table){
         return;
     }

     var item_category_id_elem = table.$("#item-category-id-" + item_id);
     if(item_category_id){
         innerHTML = item_category_id;
     }else{
         innerHTML = "";
     }
     item_category_id_elem.html(innerHTML);

     var item_category_name_elem = table.$("#item-category-name-" + item_id);
     if(item_category_name){
         innerHTML = item_category_name;
     }else{
         innerHTML = "None";
     }
     item_category_name_elem.html(innerHTML);
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

        if(table){
            var row_elem = table.$("#done-btn-" + data.list_id + "-" + data.item_id).parents("tr");
            console.log("updateRowHelper");
            updateRowHelper(data.item_id,
                            data.list_id,
                            data.checked,
                            row_elem);
        }

    });

    socket.on("asyncComments_" + socket_token, function(data){
        console.log("asyncComments");
        console.log(data);
        saveCommentsHelper(data.item_id,
                           data.list_id,
                           data.name,
                           data.comments);
        console.log("saveCommentsHelper " + data);
    });

    socket.on("asyncCategory_" + socket_token, function(data){
        console.log("asyncCategory");
        console.log(data);
        saveCategoryHelper(data.item_id,
                           data.list_id,
                           data.category_id,
                           data.category_name);
        console.log("saveCategoryHelper " + data);
    });

    socket.on("asyncAddItem_" + socket_token, function(data){
        console.log("addItemHelper");
        console.log(data);
        addItemHelper(data.list_id,
                      data.item_id,
                      data.name,
                      data.comments,
                      data.category_id,
                      data.category_name);
    });
}
