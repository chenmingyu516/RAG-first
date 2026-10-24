@echo off
cd /d "%~dp0backend"
echo [1/2] Starting backend server ...
start "RAG Backend" cmd /k ".venv\Scripts\python.exe run.py"

timeout /t 3 /nobreak >nul

cd /d "%~dp0frontend"
echo [2/2] Starting frontend server ...
start "RAG Frontend" cmd /k "npm run dev"

echo.
echo ============================================
echo   Backend : http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo   Open http://localhost:5173 in your browser
echo   Admin login: admin / 123456
echo ============================================
echo.
pause
