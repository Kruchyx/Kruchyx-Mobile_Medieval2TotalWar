@echo off
setlocal
cd /d "%~dp0windows"
call BUILD_WINDOWS_v096.bat
exit /b %errorlevel%
