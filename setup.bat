@echo off
cd /d "%~dp0"

echo ============================================
echo   RAG QA System - Install Dependencies
echo ============================================
echo.

echo [1/4] Preparing .env ...
cd /d "%~dp0backend"
if not exist .env (
  copy .env.example .env >nul
  echo   Created backend\.env, please fill in DASHSCOPE_API_KEY
) else (
  echo   backend\.env already exists, skip
)

echo [2/4] Creating Python venv and installing backend deps ...
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo [3/4] Installing frontend deps ...
cd /d "%~dp0frontend"
call npm install --registry=https://registry.npmmirror.com

cd /d "%~dp0"
echo.
echo [4/4] Done!
echo.
echo Next: edit backend\.env to fill DASHSCOPE_API_KEY,
echo       then double-click start.bat to run.
echo.
pause
