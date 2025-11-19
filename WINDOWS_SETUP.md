# FPL Optimizer - Windows Setup Guide

Quick setup guide specifically for Windows users.

## Backend Setup (Windows)

### 1. Navigate to Backend Directory

```cmd
cd C:\Users\Nick\PycharmProjects\FPLOptimizer\backend
```

### 2. Check Python Installation

```cmd
python --version
```

If this doesn't work, try:
```cmd
python3 --version
```

Or:
```cmd
py --version
```

### 3. Create Virtual Environment (Recommended)

```cmd
python -m venv venv
```

### 4. Activate Virtual Environment

```cmd
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

### 5. Upgrade pip

```cmd
python -m pip install --upgrade pip
```

### 6. Install Dependencies

```cmd
python -m pip install -r requirements.txt
```

**Note:** If you get SSL certificate errors, use:
```cmd
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### 7. Start the Backend

```cmd
python start.py
```

Or directly:
```cmd
python -m app.main
```

The backend should now be running at: **http://localhost:8000**

Open http://localhost:8000/docs in your browser to verify it's working.

---

## Frontend Setup (Windows)

### 1. Navigate to Frontend Directory

Open a **NEW** command prompt (keep backend running) and run:

```cmd
cd C:\Users\Nick\PycharmProjects\FPLOptimizer\frontend
```

### 2. Check Node.js Installation

```cmd
node --version
npm --version
```

If not installed, download from: https://nodejs.org/ (LTS version)

### 3. Install Dependencies

```cmd
npm install
```

If you get permission errors, try:
```cmd
npm install --legacy-peer-deps
```

### 4. Start Frontend Development Server

```cmd
npm start
```

The frontend should now be running at: **http://localhost:4200**

---

## Quick Start (Both Servers)

### Terminal 1 - Backend
```cmd
cd C:\Users\Nick\PycharmProjects\FPLOptimizer\backend
venv\Scripts\activate
python start.py
```

### Terminal 2 - Frontend
```cmd
cd C:\Users\Nick\PycharmProjects\FPLOptimizer\frontend
npm start
```

Then open: **http://localhost:4200**

---

## Testing the Team Viewer

1. Go to https://fantasy.premierleague.com
2. Find any team and note the team ID from the URL:
   - Example: `https://fantasy.premierleague.com/entry/123456/event/1`
   - Team ID is `123456`

3. In your app at http://localhost:4200:
   - Scroll to "FPL Team Viewer"
   - Enter the team ID
   - Check "Include current team picks"
   - Click "Load Team"

---

## Common Windows Issues

### Issue: "pip is not recognized"

**Solution:** Use `python -m pip` instead of `pip`:
```cmd
python -m pip install -r requirements.txt
```

### Issue: "python is not recognized"

**Solutions:**
1. Try `py` instead of `python`:
   ```cmd
   py -m pip install -r requirements.txt
   py start.py
   ```

2. Or add Python to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" in System Variables
   - Add: `C:\Users\Nick\AppData\Local\Programs\Python\Python311` (adjust version)
   - Add: `C:\Users\Nick\AppData\Local\Programs\Python\Python311\Scripts`

### Issue: Virtual environment not activating

**Solution:** Use PowerShell script:
```powershell
venv\Scripts\Activate.ps1
```

If you get execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Port already in use

**Solution:** Kill the process using the port:

Find process on port 8000:
```cmd
netstat -ano | findstr :8000
```

Kill the process (replace PID with actual number):
```cmd
taskkill /PID <PID> /F
```

Or change the port in `backend\.env`:
```
PORT=8001
```

### Issue: Redis connection warnings

**Solution:** Don't worry! The app works fine without Redis. The warnings are normal.

To disable warnings, you can comment out Redis in the backend or ignore them.

### Issue: CORS errors in browser

**Solution:** Make sure:
1. Backend is running on port 8000
2. Frontend is running on port 4200
3. Check `backend\.env` has:
   ```
   CORS_ORIGINS=["http://localhost:4200","http://localhost:8000"]
   ```

---

## PowerShell Alternative Commands

If using PowerShell instead of CMD:

### Backend
```powershell
cd C:\Users\Nick\PycharmProjects\FPLOptimizer\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python start.py
```

### Frontend
```powershell
cd C:\Users\Nick\PycharmProjects\FPLOptimizer\frontend
npm install
npm start
```

---

## Verifying Everything Works

### 1. Backend Health Check
Open in browser or use curl:
```cmd
curl http://localhost:8000/api/v1/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Test Team Endpoint
```cmd
curl -H "X-API-Key: dev-api-key-change-in-production" http://localhost:8000/api/v1/teams/123456
```

### 3. Frontend Check
Open browser to: http://localhost:4200

You should see the FPL Optimizer interface.

---

## Stopping the Servers

### Backend
Press `Ctrl + C` in the backend terminal

### Frontend
Press `Ctrl + C` in the frontend terminal, then confirm with `Y`

---

## Next Steps

1. ✅ Both servers running
2. ✅ Backend at http://localhost:8000/docs
3. ✅ Frontend at http://localhost:4200
4. ✅ Enter a team ID and click "Load Team"
5. ✅ See team data displayed!

## Need Help?

- Backend API Docs: http://localhost:8000/docs (interactive testing)
- Check backend console for errors
- Check browser console (F12) for frontend errors
- Check [SETUP.md](SETUP.md) for detailed information

## Development Tips

### Keep Virtual Environment Activated
Always activate venv before working on backend:
```cmd
cd backend
venv\Scripts\activate
```

### Auto-reload During Development
Both servers support hot-reload:
- Backend: Automatically reloads when you edit Python files
- Frontend: Automatically reloads when you edit TypeScript/HTML/CSS

### View Logs
- Backend: Console output in Terminal 1
- Frontend: Browser console (F12 → Console tab)
- Network requests: Browser DevTools (F12 → Network tab)

---

## Project Structure

```
C:\Users\Nick\PycharmProjects\FPLOptimizer\
├── backend\
│   ├── app\              # Backend code
│   ├── venv\             # Virtual environment (created by you)
│   ├── .env              # Configuration
│   ├── requirements.txt  # Python dependencies
│   └── start.py          # Startup script
├── frontend\
│   ├── src\app\          # Frontend code
│   ├── node_modules\     # Node packages (created by npm)
│   └── package.json      # Node dependencies
├── SETUP.md              # General setup guide
└── WINDOWS_SETUP.md      # This file
```

Happy coding! 🎉