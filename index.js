const express = require('express');
const http = require('http');
const fs =  require('fs-extra');
const execSync = require('child_process').execSync;
const net = require('net');
const app = express();
const server = http.createServer(app);

// Body parser
app.use(express.json())

// var directories = new Map([
//     ['/mnt/data2/', 0],
//     ['/mnt/data3/', 0],
//     ['/mnt/data4/', 0],
//     ['/mnt/data5/', 0],
//     ['/mnt/data6/', 0],
//     ['/mnt/data7/', 0],
//     ['/mnt/data8/', 0],
//     ['/mnt/data9/', 0],
// ]);

var directories = new Map([
    ['/mnt/data2/', 0],
    ['/mnt/data3/', 0],
])

var volumes = new Map();

app.post('/Plugin.Activate', (req, res) => {
  res.json({"Implements": ["VolumeDriver"]})
})

app.post('/VolumeDriver.Create', (req, res) => {
    if (req.body === undefined){
        res.json({"Err": "Request is not correctly formatted"})
    } else if (volumes.has(req.body.Name)) {
        res.json({"Err": "Volume " + name + " already exists"})
    } else {
        const name = req.body.Name;
        // Calculate directories occupation
        directories.forEach((_ , folder) => {
            console.log(execSync('du -s ' + folder))
            const size = parseInt(execSync('du -s ' + folder + ' | cut -f1', { encoding: 'utf-8' }))
            directories.set(folder, size)
        })
        console.log(directories)
        const min = Math.min(...directories.values())
        const s = [...directories.entries()].find(([_, v]) => v === min)[0]
        console.log(s + name)
        fs.mkdir(s + name, (err) => {
            if (err) {
              res.json({"Err": "Volume " + name + " cannot be created. " + err})
            } else {
              res.send('OK')
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
