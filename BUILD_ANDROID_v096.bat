@echo off
setlocal
cd /d "%~dp0mobile\kruchyx_mobile"
flutter create --platforms=android --org com.kruchyx .
if errorlevel 1 goto error
flutter pub get
if errorlevel 1 goto error
flutter test
if errorlevel 1 goto error
flutter build apk --release
if errorlevel 1 goto error
echo SUKCES: build\app\outputs\flutter-apk\app-release.apk
pause
exit /b 0
:error
echo BLAD: sprawdz log kompilacji
pause
exit /b 1
