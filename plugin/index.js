const express = require('express')
const app = express()
const sock = '/run/docker/plugins/your-plugin.sock'

app.get('/', (req, res) => {
  res.send('Hello World!')
})

app.listen(sock, () => {
  console.log(`Example app listening on port ${sock}`)
})
