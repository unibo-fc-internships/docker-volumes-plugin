const express = require('express');
const http = require('http');

const app = express();
const server = http.createServer(app);

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


// /run/docker/plugins/plugin.sock
server.listen('/run/docker/plugins/plugin.sock');
