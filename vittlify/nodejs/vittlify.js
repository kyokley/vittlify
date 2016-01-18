var app = require('express')()
var http = require('http').createServer(app)
var sio = require('socket.io');

var io = sio.listen(http, {origins: '*:*'});

io.on('connection', function(socket){
    console.log('got a connection');
    socket.emit('message', {'message': 'welcome'});

    socket.on('send_asyncUpdateRow', function(data){
        console.log(data);
        socket.broadcast.emit('asyncUpdateRow', data);
    });

    socket.on('send_asyncAddItem', function(data){
        console.log(data);
        socket.broadcast.emit('asyncAddItem', data);
    });
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
