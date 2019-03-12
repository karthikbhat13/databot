var express = require('express');

var app = express();

app.use('/assets', express.static('assets'))
app.use('/views', express.static('views'))
app.use('/controllers', express.static('controllers'))


app.get('/', function(req, res){
    res.sendFile(__dirname + '/views' +'/index.html');
})

var server = app.listen(9000, function () {
    var host = server.address().address
    var port = server.address().port
    
    console.log("Example app listening at http://%s:%s", host, port)
 })