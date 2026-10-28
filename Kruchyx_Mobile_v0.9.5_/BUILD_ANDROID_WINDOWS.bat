@echo off
setlocal
cd /d "%~dp0"
echo =======================================
echo  Kruchyx Mobile v0.9.5 - Android APK
echo =======================================
where flutter >nul 2>nul
if errorlevel 1 (
 echo BLAD: Zainstaluj Flutter SDK i dodaj jego bin do PATH.
 echo https://docs.flutter.dev/get-started/install/windows/mobile
 pause
 exit /b 1
)
flutter doctor
flutter create --platforms=android --org com.kruchyx .
if errorlevel 1 goto error
flutter pub get
if errorlevel 1 goto error
flutter analyze
if errorlevel 1 goto error
flutter test
if errorlevel 1 goto error
flutter build apk --release
if errorlevel 1 goto error
echo.
echo SUKCES: build\app\outputs\flutter-apk\app-release.apk
echo To build testowy. Publikacja w Google Play wymaga wlasnego podpisu wydawcy.
pause
exit /b 0
:error
echo BLAD budowania Android. Skopiuj log z konsoli.
pause
exit /b 1
