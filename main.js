const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');

let mainWindow;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 600,
    frame: false,
    resizable: false,
    transparent: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('todo.html');
}

function createCharacterWindow(taskList, screenWidth) {
  mainWindow.setBounds({ width: 200, height: 220, x: screenWidth - 220, y: 20 });
  mainWindow.setResizable(true);
  mainWindow.setAlwaysOnTop(true);
  mainWindow.setBackgroundColor('rgba(69, 111, 173, 0.73)'); // Transparent
  mainWindow.setIgnoreMouseEvents(false);
  mainWindow.setOpacity(1);
  mainWindow.setMenuBarVisibility(false);
  mainWindow.loadFile('character.html');

  // Send task list to renderer
  setTimeout(() => {
    mainWindow.webContents.send('task-list', taskList);
  }, 500);
}

app.whenReady().then(() => {
  const screenWidth = screen.getPrimaryDisplay().workAreaSize.width;

  createMainWindow();

  ipcMain.on('switch-to-character', (event, taskList) => {
    createCharacterWindow(taskList, screenWidth);
  });
});

app.on('window-all-closed', () => {
  app.quit();
});

const { spawn } = require('child_process');
const python = spawn('python', ['chat_server.py']);

python.stdout.on('data', (data) => {
  console.log(`Python: ${data}`);
});
