const { ipcRenderer } = require('electron');

let tasks = [];

ipcRenderer.on('task-list', (event, receivedTasks) => {
  tasks = receivedTasks;
  
});

function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent = now.toLocaleTimeString();
console.log(tasks)
  const currentTime = now.toTimeString().substring(0, 5); // HH:MM

  tasks.forEach(task => {
    if (task.time === currentTime && !task.notified) {
      showTask(task.desc);
      task.notified = true;
    }
  });
}

function showTask(msg) {
  const box = document.getElementById('task-text');
  box.textContent = msg;
  box.style.display = 'block';

  setTimeout(() => {
    box.style.display = 'none';
  }, 6000);
}

setInterval(updateClock, 1000);
updateClock();


function openChat() {
  document.querySelector(".character").style.display = "none"; // Hide character
  document.querySelector(".dialogue").style.display = "none";

   ipcRenderer.send('switch-to-chat');
}

function hideDialogue() {
  document.querySelector(".dialogue").style.display = 'none';
}

function sendQuestion() {
  const question = document.getElementById('user-input').value;

  fetch('http://localhost:5005/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  })
  .then(res => res.json())
  .then(data => {
    const reply = data.reply || "Error: " + data.error;
    document.getElementById('chat-log').innerHTML += `<p><b>You:</b> ${question}</p><p><b>Bot:</b> ${reply}</p>`;
    document.getElementById('user-input').value = '';
  });
}

