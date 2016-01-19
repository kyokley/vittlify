var express = require('express');
var app = express();
var http = require('http').createServer(app);
var sio = require('socket.io');
var bodyParser = require('body-parser');

var io = sio.listen(http, {origins: '*:*'});

app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());

io.on('connection', function(socket){
    console.log('got a connection');
    socket.emit('message', {'message': 'welcome'});

    //socket.on('send_asyncUpdateRow', function(data){
    //    console.log(data);
    //    socket.broadcast.emit('asyncUpdateRow', data);
    //});

    //socket.on('send_asyncAddItem', function(data){
    //    console.log(data);
    //    socket.broadcast.emit('asyncAddItem', data);
    //});
});

app.post('/item', function(req, res){
    var data = {item_id: req.body.item_id,
                list_id: req.body.list_id,
                name: req.body.name,
                comments: req.body.comments};

    console.log(data);
    console.log(req.get('host'));

    if(req.get('host') == 'localhost:3000'){
        io.emit('asyncAddItem', data);
    } else {
        console.log('Request came from an invalid source. Ignoring');
    }
    res.send('Success!');
});

app.put('/item/:id', function(req, res){
    var data = {item_id: req.id,
                list_id: req.body.list_id,
                checked: req.body.checked}
    if(req.get('host') == 'localhost:3000'){
        io.emit('asyncUpdateRow', data);
    } else {
        console.log('Request came from an invalid source. Ignoring');
    }
    res.send('Success!');
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});

