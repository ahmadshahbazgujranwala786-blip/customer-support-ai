@echo off
setlocal
cd /d "%~dp0"

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo Created .env from .env.example.
  echo Please add your PostgreSQL password and Gemini/Tavily keys in .env,
  echo then run this launcher again.
  start "" notepad.exe "%~dp0.env"
  pause
  exit /b 1
)

set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"

start "Customer Support API" /D "%~dp0" "%PYTHON_EXE%" -m uvicorn web_api:app --reload --host 127.0.0.1 --port 8000
start "Customer Support Website" /D "%~dp0frontend" "%PYTHON_EXE%" -m http.server 5173 --bind 127.0.0.1

timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5173/"
endlocal
