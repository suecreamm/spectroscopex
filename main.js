const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

let lastUsedSaveDir = null;
let isSelectingDirectory = false;  // 디렉토리 선택 중 여부를 추적하는 플래그

function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'frontend', 'preload.js'),
            webSecurity: false,
            contextIsolation: true,
            nodeIntegration: false
        },
    });
  
    win.loadFile(path.join(__dirname, 'frontend', 'index.html'));
    win.webContents.openDevTools();  // 개발자 도구 열기
}

app.whenReady().then(createWindow);

ipcMain.handle('select-directory', async () => {
    console.log('select-directory handler called');  // 디버그 로그 추가
    
    if (isSelectingDirectory) {
        console.log('Directory selection already in progress');
        return null;
    }
    
    isSelectingDirectory = true;
    
    try {
        const result = await dialog.showOpenDialog({
            properties: ['openDirectory']
        });
        
        if (result.canceled) {
            console.log('Directory selection canceled');
            return null;
        }
        
        const directoryPath = result.filePaths[0];
        console.log('Selected directory path:', directoryPath);
        return directoryPath;
    } catch (error) {
        console.error('Error in directory selection:', error);
        throw error;
    } finally {
        isSelectingDirectory = false;
    }
});

ipcMain.handle('upload-directory', async (event, directoryPath) => {
    console.log('upload-directory handler called');  // 디버그 로그 추가
    try {
        const files = fs.readdirSync(directoryPath);
        const csvFiles = files.filter(file => file.endsWith('.csv'));

        const csvFilePaths = csvFiles.map(file => path.join(directoryPath, file));

        console.log('Sending request to server with files:', csvFilePaths);  // 디버그 로그 추가

        const response = await axios.post('http://localhost:7654/upload-directory', {
            directoryPath: directoryPath,
            filePaths: csvFilePaths
        });

        console.log('Server response:', response.data);  // 디버그 로그 추가
        return response.data;
    } catch (error) {
        console.error('Error processing directory:', error);
        throw error;
    }
});

ipcMain.handle('transform-image', async (event, action) => {
    try {
      const response = await axios.post('http://localhost:7654/transform', { action });
      console.log('Backend response:', response.data);  // 디버깅을 위해 추가
      if (response.data && response.data.success && response.data.image) {
        return {
          success: true,
          image: response.data.image
        };
      } else {
        throw new Error(response.data.error || 'Unknown error occurred');
      }
    } catch (error) {
      console.error('Error transforming image:', error);
      return {
        success: false,
        error: error.message
      };
    }
  });

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});