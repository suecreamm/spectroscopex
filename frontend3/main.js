// Importing Electron modules
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

// Function to create the main application window
function createWindow() {
  // Create the browser window
  const mainWindow = new BrowserWindow({
    width: 800,   // Initial width of the window
    height: 600,  // Initial height of the window
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), // Preload script
      contextIsolation: true,  // Isolate context to improve security
      enableRemoteModule: false  // Disable remote module for security
    }
  });

  // Load the index.html file into the window
  mainWindow.loadFile('index.html');

  // Optionally open the DevTools
  // mainWindow.webContents.openDevTools();
}

// Electron app event listener for when the app is ready
app.whenReady().then(createWindow);

// Quit the application when all windows are closed
app.on('window-all-closed', () => {
  // Quit the app if not on macOS (macOS apps generally stay open)
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Re-create a window in the app when the dock icon is clicked on macOS
app.on('activate', () => {
  // Re-create window if none are open (macOS specific behavior)
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC communication (frontend to backend) - optional example
ipcMain.on('asynchronous-message', (event, arg) => {
  console.log(arg);  // Prints message from renderer process
  event.reply('asynchronous-reply', 'Pong');
});

ipcMain.on('synchronous-message', (event, arg) => {
  console.log(arg);  // Prints message from renderer process
  event.returnValue = 'Pong';
});

