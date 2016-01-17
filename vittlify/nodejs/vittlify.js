//var app = require('express')();
//var http = require('http').Server(app);
//var io = require('socket.io')(http);
//io.set('origins', '*:*');

var app = require('express')()
var http = require('http').createServer(app)
var sio = require('socket.io');

var io = sio.listen(http, { origins: '*:*' });

//app.use(function(req, res, next) {
//        res.header("Access-Control-Allow-Origin", "*");
//        res.header("Access-Control-Allow-Headers", "X-Requested-With");
//        res.header("Access-Control-Allow-Headers", "Content-Type");
//        res.header("Access-Control-Allow-Methods", "PUT, GET, POST, DELETE, OPTIONS");
//        next();
//    });

app.get('/', function(req, res){
  res.send('<h1>Hello world</h1>');
});

io.on('connection', function(socket){
    console.log('got a connection');
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
