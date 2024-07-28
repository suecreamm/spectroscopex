const { contextBridge, ipcRenderer } = require('electron');
const fs = require('fs');
const Papa = require('papaparse');

contextBridge.exposeInMainWorld('myAPI', {
  readFile: (filePath) => fs.readFileSync(filePath, 'utf8'),
  parseCSV: (data) => Papa.parse(data, { header: true, dynamicTyping: true })
});
