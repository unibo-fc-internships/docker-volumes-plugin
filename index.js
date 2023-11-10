const express = require('express');
const http = require('http');
const fs =  require('fs-extra');
const execSync = require('child_process').execSync;
const net = require('net');
const app = express();
const server = http.createServer(app);

// Body parser
app.use(express.json())

const volumesDirectory = "/mnt/common-volume/"

var volumes = new Map();

app.post('/Plugin.Activate', (req, res) => {
  res.json({"Implements": ["VolumeDriver"]})
})

app.post('/VolumeDriver.Create', (req, res) => {
    if (req.body === undefined){
        res.json({"Err": "Request is not correctly formatted"})
    } else if (volumes.includes(req.body.Name)) {
        res.json({"Err": "Volume " + req.body.Name + " already exists"})
    } else {
        const name = req.body.Name
        fs.mkdir(volumesDirectory + name, (err) => {
            if (err) {
              res.json({"Err": "Volume " + name + " cannot be created. " + err})
            } else {
              volumes.push(name)
              res.json({"Err": ""})
            }
        })
    }
})

app.post('/VolumeDriver.Get', (req, res) => {
  res.send('Get')
})

app.post('/VolumeDriver.List', (req, res) => {
  res.send('List')
})

app.post('/VolumeDriver.Remove', (req, res) => {
    if (req.body === undefined){
      res.json({"Err": "Request is not correctly formatted"})
    } else if (!volumes.includes(req.body.Name)) {
        res.json({"Err": "Volume " + req.body.Name + " doesn't exists"})
    } else {
        const name = req.body.Name
        fs.rmdir(volumesDirectory + name, (err) => {
            if (err) {
              res.json({"Err": "Volume " + name + " cannot be deleted. " + err})
            } else {
              volumes.pop(name)
              res.json({"Err": ""})
            }
        })
    }
})

app.post('/VolumeDriver.Path', (req, res) => {
  res.send('Path')
})

app.post('/VolumeDriver.Mount', (req, res) => {
  if (req.body === undefined){
    res.json({"Err": "Request is not correctly formatted"})
  } else if (!volumes.includes(req.body.Name)) {
      res.json({"Err": "Volume " + req.body.Name + " doesn't exists"})
  } else {
      const name = req.body.Name
      fs.rmdir(volumesDirectory + name, (err) => {
          if (err) {
            res.json({"Err": "Volume " + name + " cannot be deleted. " + err})
          } else {
            volumes.pop(name)
            res.json({"Err": ""})
          }
      })
  }
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
