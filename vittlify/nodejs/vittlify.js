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

var socket_token_put_request = {host: 'localhost',
                                port: 8000,
                                // path: '/vittlify/socket/' + socket_tokens[socket] + '/',
                                method: 'PUT',
                                headers: {'Content-Type': 'application/x-www-form-urlencoded'
                                         }
                                };

var socket_token_get_request = {host: 'localhost',
                                port: 8000,
                                // path: '/vittlify/socket/' + socket_tokens[socket] + '/',
                                method: 'GET'
                                };

io.on('connection', function(socket){
    console.log('got a connection');
    socket.emit('message', {'message': 'welcome'});

    socket.on('send_token', function(token, fn){
        socket_token_get_request['path'] = '/vittlify/socket/' + token + '/';
        var reqGet = http_local.request(socket_token_get_request, function(response){
            var body = "";
            response.on('data', function(chunk){
                body += chunk;
            });

            response.on('end', function(){
                var res = JSON.parse(body);
                console.log(res);
                if(res.active){
                    fn('Valid token received');
                    socket_tokens[socket] = token;
                    console.log(token);
                } else {
                    console.log(res.active);
                    var data = querystring.stringify({
                        "active": true
                    });
                    socket_token_put_request['path'] = '/vittlify/socket/' + token + '/';
                    socket_token_put_request['headers']['Content-Length'] = Buffer.byteLength(data)
                    var reqPut = http_local.request(socket_token_put_request, function(res){
                        if(res.statusCode == "200"){
                            fn('Token has been re-activated');
                            socket_tokens[socket] = token;
                            console.log("Token has been re-activated");
                            console.log(token);
                        } else {
                            fn('Invalid token');
                            socket.emit("refresh", {"message": "Invalid token!"});
                            console.log("Invalid token, forcing refresh");
                        }
                    });
                    reqPut.write(data);
                    reqPut.end();
                    reqPut.on('error', function(e){
                        console.error(e);
                        socket.emit("refresh", {"message": "Invalid token!"});
                    });
                }
            });

        }).end();
    });


    socket.on('disconnect', function(){
        // Send deactivate message to django server
        var data = querystring.stringify({
            "active": false
        });
        socket_token_put_request['path'] = '/vittlify/socket/' + socket_tokens[socket] + '/';
        socket_token_put_request['headers']['Content-Length'] = Buffer.byteLength(data)

        var reqPut = http_local.request(socket_token_put_request, function(res){
            console.log("statusCode: ", res.statusCode);
            if(res.statusCode == "200"){
                console.log("Token deactivated successfully");
                console.log(socket_tokens[socket]);
                delete socket_tokens[socket];
            }
        });

        reqPut.write(data);
        reqPut.end();
        reqPut.on('error', function(e){
            console.error(e);
        });

    });
});

app.post('/item', function(req, res){
    var data = {item_id: req.body.item_id,
                list_id: req.body.list_id,
                name: req.body.name,
                comments: req.body.comments};

    var socket_token = req.body.socket_token;
    if(req.get('host') == 'localhost:3000'){
        console.log('POST-ing to ' + socket_token);
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
        console.log('PUT-ing to ' + socket_token);
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

