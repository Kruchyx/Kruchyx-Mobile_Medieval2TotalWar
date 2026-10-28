@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (set "PYTHON=py -3") else (set "PYTHON=python")
%PYTHON% -m pip install --upgrade pyinstaller
if errorlevel 1 goto error
%PYTHON% -m unittest discover -p "test_*.py"
if errorlevel 1 goto error
%PYTHON% -m PyInstaller --noconfirm --clean --onefile --windowed ^
 --name "Kruchyx Medieval Mod Studios" --icon "kruchyx.ico" ^
 --add-data "assets;assets" --add-data "examples;examples" ^
 --add-data "shared;shared" --add-data "kruchyx.ico;." ^
 --hidden-import studio081 "kruchyx_studio.py"
if errorlevel 1 goto error
echo SUKCES: dist\Kruchyx Medieval Mod Studios.exe
pause
exit /b 0
:error
echo BLAD: sprawdz powyzsze logi
pause
exit /b 1
