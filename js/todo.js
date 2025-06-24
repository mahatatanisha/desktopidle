const { ipcRenderer } = require('electron');

window.onload = () => {
  const savedTasks = JSON.parse(localStorage.getItem('tasks') || '[]');
  savedTasks.forEach(({ desc, time }) => {
    addTask(desc, time);
  });
};

function addTask(desc = '', time = '') {
  const taskContainer = document.getElementById('taskContainer');
  const div = document.createElement('div');
  div.classList.add('task');
  div.innerHTML = `
    <input type="text" placeholder="Task" value="${desc}" />
    <input type="time" value="${time}" />
    <button class="delete-btn" title="Delete Task">🗑️</button>
  `;
  taskContainer.appendChild(div);

  div.querySelector('.delete-btn').addEventListener('click', () => {
    div.remove();
    saveTasks(); // update storage after deletion
  });
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

  localStorage.setItem('tasks', JSON.stringify(tasks));
    const box = document.getElementById('saved');
  box.style.display = 'block';

  setTimeout(() => {
    box.style.display = 'none';
  }, 6000);

}


function goToPet() {
  
const tasks = JSON.parse(localStorage.getItem('tasks') || '[]');
  tasks.forEach(({ desc, time }) => {
    addTask(desc, time);
  });
  ipcRenderer.send('switch-to-character', tasks);
}
