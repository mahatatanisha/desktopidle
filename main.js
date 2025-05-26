const { app, BrowserWindow } = require("electron");

let win;
let yOffset = 0;
let direction = 1;
const speed = 0.5; // Smaller step size for smoother motion

function animateWindow() {
  if (!win || win.isDestroyed()) return; // Ensure window exists before updating

  yOffset += direction * 0.5;

  if (yOffset > 8 || yOffset < -8) direction *= -1;

  win.setBounds({ x: 20, y: 20 + yOffset, width: 400, height: 300 });

  setTimeout(animateWindow, 16);
}


app.whenReady().then(() => {

const win = new BrowserWindow({
  titleBarStyle: 'hidden',
  titleBarOverlay: {
    color: '#2f3241',
    symbolColor: '#74b1be',
  }
})
  win.loadFile("index.html");

  setTimeout(animateWindow, 16); // Start animation loop
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
