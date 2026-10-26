const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('cameraAPI', {
  probarConexion: () => ipcRenderer.invoke('camara:probar')
});