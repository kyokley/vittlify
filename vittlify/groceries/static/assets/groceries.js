var tables = {};
function addItem(token, list_id){
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
                 },
                 error: function(){
                     console.log("Failed");
                 }
    });
}
