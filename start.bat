@echo off
title SmartLoad Launcher
color 0B
echo ====================================================================
echo         ⚡ SMARTLOAD — LANZADOR UNIFICADO DE SERVIDORES ⚡
echo ====================================================================
echo.
echo  Este script iniciara el backend de datos (FastAPI) y la interfaz
echo  interactiva (Vite/React/HeroUI) en ventanas separadas para ver
echo  los registros (logs) en tiempo real.
echo.
echo --------------------------------------------------------------------
echo.

:: 1. Start Backend API
echo [*] Iniciando el Servidor Backend (FastAPI en http://127.0.0.1:8000)...
start "SmartLoad Backend API" cmd /k ".\venvfutbol\Scripts\python.exe -m uvicorn src.server:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak > nul

:: 2. Start Frontend App
echo [*] Iniciando el Servidor Frontend (Vite/React en http://127.0.0.1:5173)...
start "SmartLoad Frontend UI" cmd /k "npm --prefix front run dev"

echo.
echo ====================================================================
echo  [🎉] ¡TODO INICIADO CON EXITO!
echo ====================================================================
echo   - Panel del Frontend: http://127.0.0.1:5173
echo   - Documentacion API:   http://127.0.0.1:8000/docs
echo.
echo  Cierra las ventanas individuales para detener los servidores.
echo --------------------------------------------------------------------
echo.
pause
