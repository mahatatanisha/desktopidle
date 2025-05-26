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

  mainWindow.loadFile('todo.html');
}

function createCharacterWindow(taskList, screenWidth) {
  mainWindow.setBounds({ width: 200, height: 250, x: screenWidth - 220, y: 20 });
  mainWindow.setResizable(false);
  mainWindow.setAlwaysOnTop(true);
  mainWindow.setBackgroundColor('rgba(0, 0, 0, 0)'); // Transparent
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
