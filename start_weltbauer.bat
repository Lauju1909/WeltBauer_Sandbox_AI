@echo off
title WeltBauer Sandbox AI
echo Starte WeltBauer...
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python wurde nicht gefunden. Bitte installiere Python.
    pause
    exit /b
)

echo Pruefe Abhaengigkeiten (pygame)...
pip install pygame --quiet

echo.
echo LM Studio sollte auf Port 1234 laufen fuer KI-Funktionen.
echo.
python main.py
if %errorlevel% neq 0 (
    echo Spiel wurde mit Fehlern beendet oder abgebrochen.
    pause
)
