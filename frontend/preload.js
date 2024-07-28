const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  uploadDirectory: (directoryPath) => ipcRenderer.invoke('upload-directory', directoryPath)
});
