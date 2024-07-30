const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const axios = require('axios');  // 서버와의 통신을 위한 HTTP 클라이언트


function createWindow() {
    const win = new BrowserWindow({
      width: 800,
      height: 600,
      webPreferences: {
        preload: path.join(__dirname, 'frontend', 'preload.js'),
        webSecurity: false,  // CORS 문제 방지 
        contextIsolation: true,
        nodeIntegration: false
      },
    });
  
    win.loadFile(path.join(__dirname, 'frontend', 'index.html'));
    win.webContents.openDevTools();  // 개발자 도구 열기
  }

app.whenReady().then(createWindow);

ipcMain.handle('select-directory', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory']
    });
    if (result.canceled) {
      return null;  // 사용자가 선택을 취소한 경우
    }
    
    const directoryPath = result.filePaths[0];
    console.log('Selected directory path:', directoryPath);  // 경로 로그
    return directoryPath;  // 선택된 디렉토리 경로 반환
  });

ipcMain.handle('upload-directory', async (event, directoryPath) => {
  try {
    const files = fs.readdirSync(directoryPath);
    const csvFiles = files.filter(file => file.endsWith('.csv'));

    const csvFilePaths = csvFiles.map(file => path.join(directoryPath, file));

    // 서버로 디렉토리 경로와 파일 목록 전송
    const response = await axios.post('http://localhost:5000/upload-directory', {
      directoryPath: directoryPath,
      filePaths: csvFilePaths
    });

    return response.data;
  } catch (error) {
    console.error('Error processing directory:', error);
    throw error;
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
