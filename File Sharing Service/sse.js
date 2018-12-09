const httpsPort = 6889,
      https = require('https'),
      ev = require('events'),
      bodyParser = require('body-parser'),
      emitter = new ev.EventEmitter(),
      fs = require('fs'),
      express = require('express'),
      application = express(),
      cors = require('cors');
	
      application.use(function (req, res, next){
      	res.header('Access-Control-Allow-Origin', '*');
	res.header('Access-Control-Allow-Headers', 'access-control-allow-origin, content-type, accept');
	next();
      });
      application.use(bodyParser.urlencoded({extended: false}));
 
application.post('/strachob/events/notify/:user', function(req, res, next){
  var data = req.body;
  var user = req.params.user;
  res.setHeader('Access-Control-Allow-Origin', '*');
  if(user){
      emitter.emit(user, data.file);
      res.writeHead(200, {"Content-Type": "text/html"});
      res.write('OK');
      res.end();
  } else {
    res.writeHeader(400, {"Content-Type": "text/html"});
    res.write('UserNotFound');
    res.end();
}

});

application.get('/strachob/events/sub/:user', function(req, res, next){
	res.writeHead(200, {
		'Connection': 'keep-alive',
		'Content-Type': 'text/event-stream',
		'Cache-Control': 'no-cache',
                'Access-Control-Allow-Origin': '*'
	});

	var user = req.params.user;
	if(user){
		emitter.on(user, function (filename){
			res.write(
				`data: User "${user}" has just uploaded a new file "${filename}" `);
			res.write('\n\n');
		});
	} else {
		res.writeHeader(400, {"Content-Type": "text/html"});
		res.write('BadRequest');
		res.end();
	}
});


const privKey = fs.readFileSync('key.pem', 'utf8'),
cert = fs.readFileSync('cert.pem', 'utf8'),
sslKeys = {key: privKey, cert: cert},
httpsServer = https.createServer(sslKeys, application);

httpsServer.listen(httpsPort, () => {
    console.log(`SSE server started on port ` + httpsPort);
});
