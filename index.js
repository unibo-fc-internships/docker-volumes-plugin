const express = require('express');
const http = require('http');
const fs =  require('fs');
const net = require('net');
const app = express();
const server = http.createServer(app);


app.post('/Plugin.Activate', (req, res) => {
  console.log("Request to Activate")
  res.json({"Implements": ["VolumeDriver"]})
})

app.post('/VolumeDriver.Create', (req, res) => {
  res.send('Create')
})

app.post('/VolumeDriver.Get', (req, res) => {
  res.send('Get')
})

app.post('/VolumeDriver.List', (req, res) => {
  res.send('List')
})

app.post('/VolumeDriver.Remove', (req, res) => {
  res.send('Remove')
})

app.post('/VolumeDriver.Path', (req, res) => {
  res.send('Path')
})

app.post('/VolumeDriver.Mount', (req, res) => {
  res.send('Mount')
})

app.post('/VolumeDriver.Unmount', (req, res) => {
  res.send('Unmount')
})

app.post('/VolumeDriver.Capabilities', (req, res) => {
  res.send('Capabilities')
})


const socket = '/run/docker/plugins/plugin.sock'
//const socket = '8080'
server.listen(socket, (req, res) => {
  console.log('Listening to ', socket)
})

server.on('listening', function() {
  // set permissions
  return fs.chmodSync(socket, 0777);
});

server.on('error', function(e) {
  if (e.code !== 'EADDRINUSE') throw e;
  net.connect({ path: socket }, function() {
    // really in use: re-throw
    throw e;
  }).on('error', function(e) {
    if (e.code !== 'ECONNREFUSED') throw e;
    // not in use: delete it and re-listen
    fs.unlinkSync(socket);
    server.listen(socket);
  });
});
