const express = require('express')
const upload = require('./upload')
const cors = require('cors')
const server = express()

var corsOptions = {
    origin: '*',
    optionsSuccessStatus: 200,
}
server.use(cors(corsOptions))



server.post('/upload_file', upload)

server.listen(5000, () => {
    console.log('Server started!')
})