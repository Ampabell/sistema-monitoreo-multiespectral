
const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('node:child_process');
const path = require('node:path');

let procesoPython = null;

function iniciarServicioPython() {
  const python = path.join(
    __dirname, '.venv', 'Scripts', 'python.exe'
  );

  procesoPython = spawn(
    python,
    [
      '-m',
      'uvicorn',
      'python_service.main:app',
      '--host',
      '127.0.0.1',
      '--port',
      '8001'
    ],
    {
      cwd: __dirname,
      windowsHide: true,
      shell: false,
      stdio: 'ignore'
    }
  );

  procesoPython.on('error', error => {
    console.error('No se pudo iniciar FastAPI:', error.message);
  });

  procesoPython.on('close', () => {
    procesoPython = null;
  });
}

function crearVentana() {
  const ventana = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'Sistema de Monitoreo Multiespectral',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  ventana.loadFile(path.join(__dirname, 'index.html'));
}

ipcMain.handle('camara:probar', async () => {
  try {
    const respuesta = await fetch(
      'http://127.0.0.1:8001/camara/conectar',
      { method: 'POST' }
    );

    const datos = await respuesta.json();

    return {
      correcto: respuesta.ok && datos.ok === true,
      mensaje: respuesta.ok
        ? datos.mensaje
        : `Error al conectar: ${datos.detail || 'Error desconocido'}`,
      salida: JSON.stringify(datos, null, 2)
    };
  } catch (error) {
    return {
      correcto: false,
      mensaje: 'No se pudo conectar con el servicio Python.',
      salida: error.message
    };
  }
});

app.whenReady().then(() => {
  iniciarServicioPython();

  crearVentana();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      crearVentana();
    }
  });
});

app.on('before-quit', () => {
  if (procesoPython && !procesoPython.killed) {
    procesoPython.kill();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
