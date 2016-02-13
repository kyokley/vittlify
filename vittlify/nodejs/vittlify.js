var express = require('express');
var app = express();
var http = require('http').createServer(app);
var sio = require('socket.io');
var bodyParser = require('body-parser');
var querystring = require('querystring');
var config = require('./config');

var io = sio.listen(http, {origins: '*:*'});

var socket_tokens = {};

app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());

var http_local;

if(config.protocol === 'http'){
    http_local = require('http');
} else {
    http_local = require('https');
}
var socket_token_put_request = {host: config.host,
                                port: config.port,
                                // path: '/vittlify/socket/' + socket_tokens[socket] + '/',
                                method: 'PUT',
                                headers: {'Content-Type': 'application/x-www-form-urlencoded'
                                         }
                                };

var socket_token_get_request = {host: config.host,
                                port: config.port,
                                // path: '/vittlify/socket/' + socket_tokens[socket] + '/',
                                method: 'GET'
                                };

io.on('connection', function(socket){
    console.log('got a connection');
    socket.emit('message', {'message': 'Welcome to Vittlify!'});

    socket.on('send_token', function(token, fn){
        if(!token){
            return;
        }

        socket_token_get_request['path'] = '/vittlify/socket/' + token + '/';
        console.log("Sending GET request to: ", socket_token_get_request['path']);
        var reqGet = http_local.request(socket_token_get_request, function(response){
            delete socket_token_get_request['path'];
            var body = "";
            response.on('data', function(chunk){
                body += chunk;
            });

            response.on('end', function(){
                var res = JSON.parse(body);
                console.log("res: ", res);
                if(res.active === true){
                    fn('Valid token received');
                    socket_tokens[socket] = token;
                    console.log("Token is valid: ", token);
                } else {
                    console.log("Token is inactive: ", token);
                    console.log("Attempting to reactivate: ", token);
                    var data = querystring.stringify({
                        "active": true
                    });
                    socket_token_put_request['path'] = '/vittlify/socket/' + token + '/';
                    socket_token_put_request['headers']['Content-Length'] = Buffer.byteLength(data)
                    var reqPut = http_local.request(socket_token_put_request, function(res){
                        delete socket_token_put_request['path'];
                        if(res.statusCode === "200" ||
                                res.statusCode === 200){
                            fn('Token has been re-activated');
                            socket_tokens[socket] = token;
                            console.log("Token has been re-activated: ", token);
                        } else {
                            fn('Invalid token');
                            socket.emit("refresh", {"message": "Invalid token!"});
                            console.log("Invalid token, forcing refresh: ", token);
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
});

app.post('/item', function(req, res){
    var data = {item_id: req.body.item_id,
                list_id: req.body.list_id,
                name: req.body.name,
                comments: req.body.comments,
                category_id: req.body.category_id,
                category_name: req.body.category_name};

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
                modified_comments: req.body.modified_comments,
                modified_category: req.body.modified_category,
                category_id: req.body.category_id,
                category_name: req.body.category_name};
    var socket_token = req.body.socket_token;
    if(req.get('host') == 'localhost:3000'){
        console.log('PUT-ing to ' + socket_token);
        console.log(data);
        if(data.modified_done === 'True'){
            io.emit('asyncUpdateRow_' + socket_token, data);
        }

        if(data.modified_category === 'True'){
            io.emit('asyncCategory_' + socket_token, data);
        }

        if(data.modified_comments === 'True'){
            io.emit('asyncComments_' + socket_token, data);
        }
    } else {
        console.log('Request came from an invalid source. Ignoring');
    }
    res.send('Success!');
});

http.listen(3000, function(){
  console.log('listening on *:3000');
  console.log('Config Data');
  console.log(config);
});

