const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');

let mainWindow;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 600,
    frame: false,
    resizable: false,
    transparent: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('templates/todo.html');
}

function createCharacterWindow(taskList, screenWidth) {
  mainWindow.setBounds({ width: 200, height: 420, x: screenWidth - 220, y: 20 });
  mainWindow.setResizable(true);
  mainWindow.setAlwaysOnTop(true);
  mainWindow.setBackgroundColor('rgba(0, 0, 0, 0)'); // Transparent
  mainWindow.setIgnoreMouseEvents(false);
  mainWindow.setOpacity(1);
  mainWindow.setMenuBarVisibility(false);
  mainWindow.loadFile('templates/character.html');

  // Send task list to renderer
  setTimeout(() => {
    mainWindow.webContents.send('task-list', taskList);
  }, 500);
}

function creatChatWindow(screenWidth, tasks){
  mainWindow.setBounds({ width: 300, height: 540, x: screenWidth - 300, y: 130  });
   mainWindow.setResizable(true);
  // mainWindow.setAlwaysOnTop(true);
  // mainWindow.setAlwaysOnBottom(true);
  mainWindow.setBackgroundColor('rgba(220, 17, 17, 0)'); // Transparent
  mainWindow.setIgnoreMouseEvents(false);
  mainWindow.setOpacity(1);
  mainWindow.loadFile('templates/chatWindow1.html');
  setTimeout(() => {
    mainWindow.webContents.send('task-list', tasks);
  }, 500);
}

app.whenReady().then(() => {
  const screenWidth = screen.getPrimaryDisplay().workAreaSize.width;

  createMainWindow();

  ipcMain.on('switch-to-character', (event, taskList) => {
 
    createCharacterWindow(taskList, screenWidth);
  });
  ipcMain.on('switch-to-chat', (event, tasks) => {
    creatChatWindow(screenWidth, tasks);
  });
});

ipcMain.on('switch-to-todo', () => {
  if (mainWindow) {
    mainWindow.close();
    mainWindow = null; // Optional: helps prevent reuse of stale window reference
  }
  createMainWindow();
});



app.on('window-all-closed', () => {
  app.quit();
});

const { spawn } = require('child_process');
const python = spawn('python', ['chat_server1.py']);

python.stdout.on('data', (data) => {
  console.log(`Python: ${data}`);
});
