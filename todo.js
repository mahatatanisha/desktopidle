const { ipcRenderer } = require('electron');

function addTask() {
  const taskContainer = document.getElementById('taskContainer');
  const div = document.createElement('div');
  div.classList.add('task');
  div.innerHTML = `
    <input type="text" placeholder="Task" />
    <input type="time" />
  `;
  taskContainer.appendChild(div);
}

function saveTasks() {
  const tasks = [];
  document.querySelectorAll('.task').forEach(el => {
    const desc = el.children[0].value;
    const time = el.children[1].value;
    if (desc && time) {
      tasks.push({ desc, time });
    }
  });

  ipcRenderer.send('switch-to-character', tasks);
}
