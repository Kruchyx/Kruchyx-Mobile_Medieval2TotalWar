@echo off
setlocal
cd /d "%~dp0"
echo =======================================
echo  Kruchyx v0.9.5 - budowanie Windows EXE
echo =======================================
where py >nul 2>nul
if errorlevel 1 (
 echo BLAD: Zainstaluj Python 3.10+ z python.org.
 pause
 exit /b 1
)
py -3 -m pip install --upgrade pyinstaller
if errorlevel 1 goto error
py -3 -m unittest discover -p "test_*.py"
if errorlevel 1 (
 echo Testy wykazaly bledy! Budowanie zatrzymane.
 pause
 exit /b 1
)
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed ^
 --name "Kruchyx Medieval Mod Studios" --icon "kruchyx.ico" ^
 --add-data "assets;assets" --add-data "examples;examples" ^
 --add-data "shared;shared" --add-data "kruchyx.ico;." ^
 --hidden-import studio081 "kruchyx_studio.py"
if errorlevel 1 goto error
echo.
echo SUKCES: dist\Kruchyx Medieval Mod Studios.exe
echo Skopiuj ten EXE na komputer z Windows i sprawdz z gra.
pause
exit /b 0
:error
echo BLAD: sprawdz powyzszy log.
pause
exit /b 1
