/*jslint browser:true */
function addShoppingList(owner_id){
    var new_list_name = document.getElementById("new-list-name");
    if(new_list_name.value){
        jQuery.ajax({url: "/vittlify/shopping_list/",
                     type: "POST",
                     dataType: "json",
                     data: {owner_id: owner_id,
                            name: new_list_name.value},
                     success: function(json){
                         newShoppingList(json.name, json.pk);
                         var new_list_name = document.getElementById("new-list-name");
                         new_list_name.value = "";
                     },
                     error: function(){
                         alert("An error has occurred");
                     }
        });
    }
}

function newShoppingList(name, list_id){
    var list_select = document.getElementById("owned-lists-select");
    var opt = document.createElement('option');
    opt.appendChild(document.createTextNode(name));
    opt.value = "owned_list_opt-" + list_id;
    list_select.appendChild(opt);
}

function deleteShoppingList(){
    var list = document.getElementById("owned-lists-select");
    if(list.selectedIndex >= 0){
        var sel = list.options[list.selectedIndex];
        var list_id = sel.value.match('[0-9]+');

        jQuery.ajax({url: "/vittlify/shopping_list/" + list_id + "/",
                     type: "DELETE",
                     dataType: "json",
                     success: function(){
                         removeShoppingList();
                     },
                     error: function(){
                         alert("An error has occurred");
                     }
        });
    }
}

function removeShoppingList(){
    var list = document.getElementById("owned-lists-select");
    list.removeChild(list.options[list.selectedIndex]);
}
