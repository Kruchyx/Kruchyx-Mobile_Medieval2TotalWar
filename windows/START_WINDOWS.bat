@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Kruchyx Medieval Mod Studios v0.9.5
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 kruchyx_studio.py
) else (
  python kruchyx_studio.py
)
if errorlevel 1 (
  echo.
  echo Nie udalo sie uruchomic aplikacji. Sprawdz, czy masz Python 3.10+ z Tkinter.
  pause
)
