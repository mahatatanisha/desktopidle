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
  const box = document.getElementById('dialogue');
  box.textContent = msg;
  box.style.display = 'block';

  setTimeout(() => {
    box.style.display = 'none';
  }, 6000);
}

setInterval(updateClock, 1000);
updateClock();
