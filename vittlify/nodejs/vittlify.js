var express = require('express');
var app = express();
var http = require('http').createServer(app);
var http_local = require('http');
var sio = require('socket.io');
var bodyParser = require('body-parser');
var querystring = require('querystring');

var io = sio.listen(http, {origins: '*:*'});

var socket_tokens = {};

app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());

io.on('connection', function(socket){
    console.log('got a connection');
    socket.emit('message', {'message': 'welcome'});

    socket.on('send_token', function(token, fn){
        socket_tokens[socket] = token;
        fn('Token received');
        console.log(token);
    });

    var form_data = querystring.stringify({
        "pass" : "ALEXA_PASS",
    });

    socket.on('disconnect', function(){
        // Send deactivate message to django server
        var options = {host: 'localhost',
                       port: 8000,
                       path: '/vittlify/socket/' + socket_tokens[socket] + '/',
                       method: 'PUT',
                       headers: {'Content-Type': 'application/x-www-form-urlencoded',
                                 'Content-Length': Buffer.byteLength(form_data)
                                }
                      };

        var reqPut = http_local.request(options, function(res){
            console.log("statusCode: ", res.statusCode);
        });
        console.log(form_data);
        reqPut.write(form_data);
        reqPut.end();
        reqPut.on('error', function(e){
            console.error(e);
        });

        delete socket_tokens[socket];
    });
});

app.post('/item', function(req, res){
    var data = {item_id: req.body.item_id,
                list_id: req.body.list_id,
                name: req.body.name,
                comments: req.body.comments};

    var socket_token = req.body.socket_token;
    if(req.get('host') == 'localhost:3000'){
        console.log('POST-ing');
        console.log(data);
        io.emit('asyncAddItem_' + socket_token, data);
    } else {
        console.log('Request came from an invalid source. Ignoring');
    }
    res.send('Success!');
});

app.put('/item/:id', function(req, res){
    var data = {item_id: req.params.id,
                list_id: req.body.list_id,
                checked: req.body.checked,
                comments: req.body.comments,
                name: req.body.name,
                modified_done: req.body.modified_done,
                modified_comments: req.body.modified_comments};
    var socket_token = req.body.socket_token;
    if(req.get('host') == 'localhost:3000'){
        console.log('PUT-ing');
        console.log(data);
        if(data.modified_done === 'True'){
            io.emit('asyncUpdateRow_' + socket_token, data);
        }

        if(data.modified_comments === 'True'){
            io.emit('asyncComments', data);
        }
    } else {
        console.log('Request came from an invalid source. Ignoring');
    }
    res.send('Success!');
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});

