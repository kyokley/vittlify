/*jslint browser:true */
var token;

function addShoppingList(){
    var new_list_name = document.getElementById("new-list-name");
    if(!new_list_name.value){
        alert('Name is a required field for new shopping lists');
    } else {
        jQuery.ajax({url: "/vittlify/shopping_list/",
                     type: "POST",
                     dataType: "json",
                     data: {owner_id: list_id,
                            name: item_name.value,
                            comments: item_comments.value,
                            csrfmiddlewaretoken: token},
                     success: function(json){
