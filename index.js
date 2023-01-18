// Program was implemented with the aid of https://www.youtube.com/watch?v=UymGJnv-WsE
// Video was followed through for an understanding of the topic as it wasn't of my knowledge
// Research was also conducted and through countless blogs, articles and videos, this reference was the one that got my understanding to the fullest

const express = require('express')
const app = express()

const server = require('http').Server(app) // http library and pass in the app from express
const io = require('socket.io')(server) // pass sever

app.set('views', './views') // where views is located
app.set('view engine', 'ejs') // use ejs

app.use(express.static('public')) // where public is located and where javascript travels to
app.use(express.urlencoded({ extended: true })) // allow to utilize url parameters

// rooms variable, set to empty so when you go to page no past pages exist
const rooms = {}

// render index page to pass all rooms
app.get('/', (req, res) => {
  res.render('index', { rooms : rooms })
})

// post route to route to /room
app.post('/room', (req, res) => {
  if (rooms[req.body.room] != null) { // checker to see if room exists
    return res.redirect('/') // if room exists they are redirected back to path
  }
  rooms[req.body.room] = { users: {} } // empty users variable for rooms
  res.redirect(req.body.room) // redriect user to room, access room through the javascript file
  io.emit('room has been created', req.body.room) // send msg to user (io.emit) when created a new room is created
})

// get route to get a room
app.get('/:room', (req, res) => { // all rooms will be passed through this route
  if (rooms[req.params.room] == null) { // checker if room exists
    return res.redirect('/') // if room does not exist, user is redirected back to home
  }
  res.render('room', { roomName: req.params.room }) // pass room
})

// Port variable being used for application
const PORT = 4200;
// server listen and then log that it is running as well as to what port
server.listen(PORT, () => console.log(`Server is broadcasting on ${PORT}`));
                          console.log(`Access http://localhost:${PORT} to inspect Chat Application`);
 
io.on('connection', socket => {
  socket.on('new-user', (room, name) => { // room and name that is being sent
    socket.join(room) // places user to room
    rooms[room].users[socket.id] = name // access room and get users by socket.id from room 
    socket.to(room).emit('user has successfully connected', name) // broadcast to room users
  })
  socket.on('send-chat-message', (room, message) => {
    socket.to(room).emit('chat-message', { message: message, name: rooms[room].users[socket.id] })
  })
  socket.on('disconnect', () => {
    // function to pass into the socket to indicate user and loop over each rooms
    getUserRooms(socket).forEach(room => {
      socket.to(room).emit('user has disconnected from room', rooms[room].users[socket.id]) // broadcast that a user disconnected from a room
      delete rooms[room].users[socket.id] // removes user from the room
    })
  })
})

// check all rooms and users and return name of all rooms that user is apart of
function getUserRooms(socket) {
  // convert object to array to use in a method by using reduce, it will group by names and name and room array parameters
  return Object.entries(rooms).reduce((names, [name, room]) => {
    if (room.users[socket.id] != null) names.push(name) // check if there is a user with socket.id
    return names
  }, []) // default names to empty array 

}

// run commands :
// sudo npm run devStart
// yarn devStart