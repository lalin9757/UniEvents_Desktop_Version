const { app, BrowserWindow, shell, Menu, dialog, ipcMain } = require('electron');
const { spawn, exec } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

// ==============================
// Configuration
// ==============================
const DJANGO_PORT = 8765;
const DJANGO_HOST = '127.0.0.1';
const DJANGO_URL = `http://${DJANGO_HOST}:${DJANGO_PORT}`;

let mainWindow = null;
let djangoProcess = null;
let splashWindow = null;

// ==============================
// Find Python executable
// ==============================
function findPython() {
  const candidates = ['python3', 'python', 'py'];
  // On Windows, check common install paths
  const winPaths = [
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python311', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python310', 'python.exe'),
    'C:\\Python311\\python.exe',
    'C:\\Python310\\python.exe',
  ];

  if (process.platform === 'win32') {
    for (const p of winPaths) {
      if (fs.existsSync(p)) return p;
    }
  }
  return candidates[0]; // fallback to PATH lookup
}

// ==============================
// Find Django project root
// ==============================
function getDjangoPath() {
  // In development, look relative to electron folder
  const devPath = path.join(__dirname, '..', '..', 'django_app');
  if (fs.existsSync(path.join(devPath, 'manage.py'))) return devPath;

  // In packaged app (resources/app/django_app)
  const prodPath = path.join(process.resourcesPath || '', 'django_app');
  if (fs.existsSync(path.join(prodPath, 'manage.py'))) return prodPath;

  // Fallback: same directory as electron folder
  const siblingPath = path.join(__dirname, '..', 'django_app');
  if (fs.existsSync(path.join(siblingPath, 'manage.py'))) return siblingPath;

  return null;
}

// ==============================
// Start Django server
// ==============================
function startDjango() {
  return new Promise((resolve, reject) => {
    const djangoPath = getDjangoPath();
    if (!djangoPath) {
      reject(new Error('Django project not found! Please place it in the django_app folder.'));
      return;
    }

    const python = findPython();
    const managePy = path.join(djangoPath, 'manage.py');

    console.log(`Starting Django from: ${djangoPath}`);
    console.log(`Using Python: ${python}`);

    djangoProcess = spawn(python, [
      managePy,
      'runserver',
      `${DJANGO_HOST}:${DJANGO_PORT}`,
      '--noreload',
    ], {
      cwd: djangoPath,
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
    });

    djangoProcess.stdout.on('data', (data) => {
      console.log('[Django]', data.toString().trim());
    });

    djangoProcess.stderr.on('data', (data) => {
      const msg = data.toString().trim();
      console.log('[Django stderr]', msg);
      // Django prints "Starting development server" to stderr
      if (msg.includes('Starting development server')) {
        setTimeout(() => resolve(), 800);
      }
    });

    djangoProcess.on('error', (err) => {
      reject(new Error(`Failed to start Python: ${err.message}\n\nMake sure Python 3 is installed and in your PATH.`));
    });

    djangoProcess.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.error(`Django exited with code ${code}`);
      }
    });

    // Fallback resolve after 5 seconds if we don't see the message
    setTimeout(() => resolve(), 5000);
  });
}

// ==============================
// Wait for Django to respond
// ==============================
function waitForDjango(maxAttempts = 20) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const check = () => {
      const req = http.get(`${DJANGO_URL}/`, (res) => {
        resolve();
      });
      req.on('error', () => {
        attempts++;
        if (attempts >= maxAttempts) {
          reject(new Error('Django server did not start in time.'));
        } else {
          setTimeout(check, 500);
        }
      });
      req.end();
    };
    check();
  });
}

// ==============================
// Create splash/loading window
// ==============================
function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 480,
    height: 300,
    frame: false,
    alwaysOnTop: true,
    transparent: true,
    resizable: false,
    webPreferences: { nodeIntegration: true, contextIsolation: false },
  });

  const splashHTML = `
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  }
  .logo { font-size: 52px; margin-bottom: 12px; }
  h1 { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
  p { font-size: 13px; opacity: 0.75; margin-bottom: 32px; }
  .spinner {
    width: 40px; height: 40px;
    border: 4px solid rgba(255,255,255,0.2);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 16px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .status { font-size: 12px; opacity: 0.6; }
</style>
</head>
<body>
  <div class="logo">🎓</div>
  <h1>Uni Events Management</h1>
  <p>University Club & Event Portal</p>
  <div class="spinner"></div>
  <div class="status" id="status">Starting server...</div>
  <script>
    const { ipcRenderer } = require('electron');
    ipcRenderer.on('status', (e, msg) => {
      document.getElementById('status').textContent = msg;
    });
  </script>
</body>
</html>`;

  splashWindow.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(splashHTML));
}

// ==============================
// Create main app window
// ==============================
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    show: false,
    title: 'Uni Events Management',
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false, // allow loading local resources
    },
    backgroundColor: '#f8f9fa',
  });

  // Build application menu
  const menu = Menu.buildFromTemplate([
    {
      label: 'File',
      submenu: [
        {
          label: 'Go to Home',
          accelerator: 'CmdOrCtrl+H',
          click: () => mainWindow.loadURL(DJANGO_URL),
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => app.quit(),
        },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload', label: 'Reload Page' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Navigate',
      submenu: [
        {
          label: '🏠 Home',
          click: () => mainWindow.loadURL(`${DJANGO_URL}/`),
        },
        {
          label: '📅 Events',
          click: () => mainWindow.loadURL(`${DJANGO_URL}/events/`),
        },
        {
          label: '🏛️ Clubs',
          click: () => mainWindow.loadURL(`${DJANGO_URL}/clubs/`),
        },
        {
          label: '📊 Dashboard',
          click: () => mainWindow.loadURL(`${DJANGO_URL}/dashboard/`),
        },
        { type: 'separator' },
        {
          label: '⚙️ Admin Panel',
          click: () => mainWindow.loadURL(`${DJANGO_URL}/admin/`),
        },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              title: 'About Uni Events Management',
              message: 'Uni Events Management System',
              detail: 'University Club & Event Portal\n\nBuilt with Django + Electron\n\nVersion 1.0.0',
              icon: path.join(__dirname, 'icon.png'),
            });
          },
        },
      ],
    },
  ]);
  Menu.setApplicationMenu(menu);

  // Open external links in browser, not Electron
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (!url.startsWith(DJANGO_URL)) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  mainWindow.on('ready-to-show', () => {
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.close();
    }
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  return mainWindow;
}

// ==============================
// App lifecycle
// ==============================
app.whenReady().then(async () => {
  createSplashWindow();

  try {
    splashWindow.webContents.send('status', 'Starting Django server...');
    await startDjango();

    splashWindow.webContents.send('status', 'Waiting for server...');
    await waitForDjango();

    splashWindow.webContents.send('status', 'Loading application...');

    const win = createMainWindow();
    win.loadURL(DJANGO_URL);

  } catch (err) {
    console.error('Startup error:', err);
    if (splashWindow && !splashWindow.isDestroyed()) splashWindow.close();

    dialog.showErrorBox('Startup Failed', err.message);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
});

app.on('before-quit', () => {
  if (djangoProcess) {
    console.log('Stopping Django...');
    if (process.platform === 'win32') {
      exec(`taskkill /pid ${djangoProcess.pid} /T /F`);
    } else {
      djangoProcess.kill('SIGTERM');
    }
  }
});
