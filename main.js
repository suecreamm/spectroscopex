const { app, BrowserWindow, ipcMain, dialog, session } = require('electron');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

const SERVER_URL = 'http://localhost:7654';
let isSelectingDirectory = false;


function createWindow() {
    const privateSession = session.fromPartition('persist:private', {
        cache: false,
        storage: true
    });

    const win = new BrowserWindow({
        width: 1000,
        height: 750,
        webPreferences: {
            preload: path.join(__dirname, 'frontend', 'preload.js'),
            session: privateSession, // Private mode in Chrome
            nodeIntegration: true,
            contextIsolation: false
        },
    });
  
    win.loadFile(path.join(__dirname, 'frontend', 'index.html'));
    if (process.env.NODE_ENV === 'development') {
        win.webContents.openDevTools();
    }
}

app.whenReady().then(createWindow);

ipcMain.handle('select-directory', async () => {
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
    try {
        const files = fs.readdirSync(directoryPath);
        const csvFiles = files.filter(file => file.endsWith('.csv'));
        const csvFilePaths = csvFiles.map(file => path.join(directoryPath, file));

        console.log('Sending request to server with files:', csvFilePaths);

        const response = await axios.post(`${SERVER_URL}/upload-directory`, {
            directoryPath: directoryPath,
            filePaths: csvFilePaths
        });

        console.log('Server response:', response.data);
        return response.data;
    } catch (error) {
        console.error('Error processing directory:', error);
        throw new Error(`Failed to process directory: ${error.message}`);
    }
});

ipcMain.handle('transform-image', async (event, action) => {
    try {
        const response = await axios.post(`${SERVER_URL}/transform`, { action });
        console.log('Backend response:', response.data);

        if (response.data && response.data.success) {
            const base64Image = response.data.image;

            let mimeType = 'image/png';

            if (base64Image.length > 1024 || base64Image.startsWith('/9j/')) {
                mimeType = 'image/jpeg';
            }

            return {
                success: true,
                image: `data:${mimeType};base64,${base64Image}`,
                explistPath: response.data.explist_path
            };
        } else {
            throw new Error(response.data.error || 'Unknown error occurred');
        }
    } catch (error) {
        console.error('Error transforming image:', error);
        return {
            success: false,
            error: `Image transformation failed: ${error.message}`
        };
    }
});


ipcMain.handle('export-csv', async (event, data, suggestedFileName) => {
    try {
        const result = await dialog.showSaveDialog({
            title: 'Export CSV',
            defaultPath: path.join(app.getPath('downloads'), suggestedFileName || 'export.csv'),
            filters: [
                { name: 'CSV Files', extensions: ['csv'] }
            ]
        });

        if (result.canceled) {
            console.log('CSV export canceled');
            return { success: false, message: 'Export canceled' };
        }

        fs.writeFileSync(result.filePath, data, 'utf-8');
        console.log('CSV exported successfully to:', result.filePath);
        return { success: true, filePath: result.filePath };
    } catch (error) {
        console.error('Error exporting CSV:', error);
        return { success: false, error: `Failed to export CSV: ${error.message}` };
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