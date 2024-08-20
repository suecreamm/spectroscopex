const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  // Function to select a directory for loading files
  selectSaveDirectory: async () => {
    try {
      return await ipcRenderer.invoke('select-directory');
    } catch (error) {
      console.error('Error selecting directory:', error);
      return null;
    }
  },
  
  // Function to upload a directory
  uploadDirectory: async (directoryPath) => {
    try {
      return await ipcRenderer.invoke('upload-directory', directoryPath);
    } catch (error) {
      console.error('Error uploading directory:', error);
      return null;
    }
  },

  // Function to perform Q-Energy Loss transformation
  qEnergyLoss: async (data) => {
    try {
      return await ipcRenderer.invoke('q-energyloss', data);
    } catch (error) {
      console.error('Error performing Q-Energy Loss:', error);
      return null;
    }
  },

  // Function to transform an image
  transformImage: async (action) => {
    try {
      return await ipcRenderer.invoke('transform-image', action);
    } catch (error) {
      console.error('Error transforming image:', error);
      return null;
    }
  },

  // Function to export data as a CSV file
  exportCSV: async (data, fileName) => {
    try {
      const directoryPath = await ipcRenderer.invoke('select-directory');
      if (directoryPath) {
        return await ipcRenderer.invoke('export-csv', { data, fileName, directoryPath });
      } else {
        console.error('No directory selected for exporting CSV.');
        return null;
      }
    } catch (error) {
      console.error('Error exporting CSV:', error);
      return null;
    }
  }
});
