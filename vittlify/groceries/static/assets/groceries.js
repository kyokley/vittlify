var tables = {};
function addItem(token, list_id){
    var item_name = document.getElementById("new-item-name-" + list_id).value;
    var item_comments = document.getElementById("new-item-comment-" + list_id).value;
    jQuery.ajax({url: "/vittlify/item/",
                 type: "POST",
                 dataType: "json",
                 data: {shopping_list_id: list_id,
                        name: item_name,
                        comments: item_comments,
                        csrfmiddlewaretoken: token},
                 success: function(json){
                     var table = tables["table-shopping_list-" + list_id];
                     var checkbox = '<input type="checkbox" id="checkbox-' + list_id + '-' + json.pk + '" name="checkbox-' + json.name + '" />';
                     table.row.add([item_name, json.comments, checkbox]).draw();
                 },
                 error: function(){
                     console.log("Failed");
                 }
    });
}
