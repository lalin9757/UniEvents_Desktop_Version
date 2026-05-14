# 🎓 Uni Events Management — Desktop App

The Django project is wrapped with **Electron** to create a desktop application.
Django runs as a local server, and Electron displays it in a native desktop window.

---

## 📁 Folder Structure

```
desktop_app/
├── electron/
│   └── main.js          ← Electron main process
├── django_app/          ← Your Django project (see below)
├── package.json         ← Electron config
├── setup.bat            ← Windows setup script
├── setup.sh             ← Linux/Mac setup script
└── run.bat              ← Quick run (Windows)
```

---

## 🚀 First-Time Setup

### Step 1: Place Your Files

Put all your Django project files inside the `django_app/` folder:

```
desktop_app/
└── django_app/
    ├── manage.py
    ├── requirements.txt
    ├── db.sqlite3
    ├── config/
    ├── accounts/
    ├── clubs/
    ├── events/
    ├── dashboard/
    ├── api/
    ├── templates/
    └── static/
```

### Step 2: Install Prerequisites

- **Python 3.10+** → https://python.org (on Windows, make sure to check "Add to PATH")
- **Node.js 18+** → https://nodejs.org

### Step 3: Run Setup

**Windows:**
```
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Step 4: Launch the App

```bash
npm start
```

Or double-click `run.bat` on Windows.

---

## 🏗️ Build an Executable (.exe / .AppImage)

### Windows (.exe installer):
```bash
npm run build:win
```

### Linux (.AppImage):
```bash
npm run build:linux
```

### Mac (.dmg):
```bash
npm run build:mac
```

The output will be in the `dist/` folder.

---

## ⚙️ App Features

| Feature | Details |
|---------|---------|
| **Django Backend** | Runs locally on port 8765 |
| **Splash Screen** | Loading animation with status messages |
| **App Menu** | Shortcuts for Home, Events, Clubs, Dashboard |
| **Full Screen** | Press F11 or use the View menu |
| **Auto-close** | Django server stops automatically when the app closes |
| **Admin Panel** | Accessible via Navigate > Admin Panel |

---

## 🔧 Troubleshooting

### "Python not found" error
- Install Python and make sure it is added to PATH
- On Windows, verify by running `python --version` in Command Prompt

### "Django project not found" error
- Make sure `manage.py` exists inside the `django_app/` folder

### Port already in use
- Check if another Django server is already running
- Change `DJANGO_PORT = 8765` to a different number in `main.js`

### Static files not loading
```bash
cd django_app
python manage.py collectstatic --noinput
```

---

## 📝 Notes

- To create the first superadmin: `python manage.py createsuperuser`
- Database file: `django_app/db.sqlite3` — keep a backup of this file
- For production, set `DEBUG = False` in `django_app/config/settings.py`
