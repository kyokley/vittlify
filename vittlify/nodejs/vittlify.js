var express = require('express');
var app = express();
var router = express.Router();
var http = require('http').createServer(app);
var sio = require('socket.io');
var bodyParser = require('body-parser');

var io = sio.listen(http, {origins: '*:*'});

app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());

router.route('/unsafe_item')
      .post(function(req, res){

      });
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

