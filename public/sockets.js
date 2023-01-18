// Program was implemented with the aid of https://www.youtube.com/watch?v=UymGJnv-WsE
// Video was followed through for an understanding of the topic as it wasn't of my knowledge
// Research was also conducted and through countless blogs, articles and videos, this reference was the one that got my understanding to the fullest

const socket = io('http://localhost:4200')
const messageContainer = document.getElementById('message-container')
const roomContainer = document.getElementById('room-container')
const messageForm = document.getElementById('send-container')
const messageInput = document.getElementById('message-input')

if (messageForm != null) { // checker to see if messageform exists
  const name = prompt('What is your name?')
  appendMessage('You joined')
  socket.emit('new-user', roomName, name)

  messageForm.addEventListener('submit', e => {
    e.preventDefault() // permits the default action from occuring by user
    const message = messageInput.value
    appendMessage(`You: ${message}`)
    socket.emit('send-chat-message', roomName, message) // pass  message and roomname
    messageInput.value = ''
  })
}

socket.on('room-created', room => {
  const roomElement = document.createElement('div') // name of room from javascript
  roomElement.innerText = room // set innertext and make name equal to div name
  const roomLink = document.createElement('a') // anchor tag roomlink
  roomLink.href = `/${room}` // link to room variable 
  roomLink.innerText = 'join' // equal to join tag
  // add content to page
  // access roomContainer and append all components
  roomContainer.append(roomElement)
  roomContainer.append(roomLink)
})
// socket.io routes
socket.on('chat-message', data => {
  appendMessage(`${data.name}: ${data.message}`)
})

socket.on('user-connected', name => {
  appendMessage(`${name} connected`)
})

socket.on('user-disconnected', name => {
  appendMessage(`${name} disconnected`)
})
// function to pass messages to container
function appendMessage(message) {
  const messageElement = document.createElement('div')
  messageElement.innerText = message
  messageContainer.append(messageElement)
}