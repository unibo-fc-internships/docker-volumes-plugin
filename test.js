const http = require('http');

const options = {
    socketPath: '/run/docker/plugins/plugin.sock',
    path: '/Plugin.Activate',
    method: 'POST',
};

const callback = res => {
    console.log(`STATUS: ${res.statusCode}`);
    res.setEncoding('utf8');
    res.on('data', data => console.log(data));
    res.on('error', data => console.error(data));
};

const clientRequest = http.request(options, callback);
clientRequest.end();