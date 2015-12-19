/*jslint browser:true */
var token;

function addShoppingList(owner_id){
    var new_list_name = document.getElementById("new-list-name");
    if(!new_list_name.value){
        alert('Name is a required field for new shopping lists');
    } else {
        jQuery.ajax({url: "/vittlify/shopping_list/",
                     type: "POST",
                     dataType: "json",
                     data: {owner_id: owner_id,
                            name: new_list_name.value,
                            csrfmiddlewaretoken: token},
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

}
