/*jslint browser:true */
var sharing_select;
var owner_id;

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
                         refreshSharedLists();
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
                         refreshSharedLists();
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

function updateSharedList(){
    var list = document.getElementById("shopper-select");
    var sel = list.options[list.selectedIndex];
    var shopper_id = sel.value.match('[0-9]+');
    var sharing_select_elem = document.getElementById("sharing-select");
    for(var i = 0; i < sharing_select_elem.options.length; i++){
        var opt = sharing_select_elem.options[i];
        var list_id = opt.value.match('[0-9]+');
        if(opt.selected){
            jQuery.ajax({url: "/vittlify/shared_list_member/" + shopper_id + "/" + list_id + "/",
                         type: "POST",
                         dataType: "json",
                         success: function(json){
                            console.log(json)
                         },
                         error: function(){
                             alert("An error has occurred");
                         }
            });
        } else {
            jQuery.ajax({url: "/vittlify/shared_list_member/" + shopper_id + "/" + list_id + "/",
                         type: "DELETE",
                         dataType: "json",
                         success: function(json){
                            console.log(json)
                         },
                         error: function(){
                             alert("An error has occurred");
                         }
            });
        }
    }
}

function refreshSharedLists(){
    var list = document.getElementById("shopper-select");
    if(list.selectedIndex >= 0){
        var sel = list.options[list.selectedIndex];
        var shopper_id = sel.value.match('[0-9]+');

        jQuery.ajax({url: "/vittlify/shared_lists/" + shopper_id + "/",
                     type: "GET",
                     dataType: "json",
                     success: function(json){
                        var list = document.getElementById("sharing-select");

                        for(var i = list.options.length - 1; i >= 0; i--){
                            list.removeChild(list.options[i]);
                        }

                        for(var i = 0; i < json.unselected.length; i++){
                            var opt = document.createElement("option");
                            opt.value = "sharing-select-opt-" + json.unselected[i].id;
                            opt.text = json.unselected[i].name;
                            list.appendChild(opt);
                        }

                        for(var i = 0; i < json.selected.length; i++){
                            var opt = document.createElement("option");
                            opt.value = "sharing-select-opt-" + json.selected[i].id;
                            opt.selected = true;
                            opt.text = json.selected[i].name;
                            list.appendChild(opt);
                        }
                        sharing_select.bootstrapDualListbox('refresh');
                     },
                     error: function(){
                         alert("An error has occurred");
                     }
        });
    }
}

function clearEmailText(){
    var textbox = document.getElementById("user-email-text");
    textbox.value = "";
}

function saveEmailText(){
    var user_email_field = document.getElementById("user-email-text");
    var user_email = user_email_field.value;

    jQuery.ajax({url: "/vittlify/shopper/" + owner_id + "/",
                 type: "PUT",
                 dataType: "json",
                 data: {"email": user_email},
                 success: function(json){
                    var res = jQuery("#email-saved-text");
                    var savedField = res[0];
                    savedField.style.color = "Black";
                    savedField.innerText = "Saved Successfully";
                    res.fadeOut(2000, function() {
                        savedField.innerText = "";
                        res.show(0);
                    });
                 },
                 error: function(json){
                     console.log(json);
                    var res = jQuery("#email-saved-text");
                    var savedField = res[0];
                    savedField.style.color = "Red";
                    savedField.innerText = "Save failed: " + json.responseJSON["email"];
                    res.fadeOut(2000, function() {
                        savedField.style.color = "Black";
                        savedField.innerText = "";
                        res.show(0);
                    });
                 }
    });
}
