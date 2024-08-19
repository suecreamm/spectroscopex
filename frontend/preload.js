const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  selectSaveDirectory: () => ipcRenderer.invoke('select-directory').catch(console.error),
  uploadDirectory: (directoryPath) => ipcRenderer.invoke('upload-directory', directoryPath).catch(console.error),
  qEnergyLoss: (data) => ipcRenderer.invoke('q-energyloss', data).catch(console.error),
  transformImage: (action) => ipcRenderer.invoke('transform-image', action).catch(console.error),
  exportCSV: (data, fileName) => ipcRenderer.invoke('export-csv', data, fileName).catch(console.error)  
});