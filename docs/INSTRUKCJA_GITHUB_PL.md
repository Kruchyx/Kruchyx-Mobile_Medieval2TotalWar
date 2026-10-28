# Instrukcja krok po kroku — APK, EXE i iPhone przez GitHub

Repozytorium docelowe: `https://github.com/Kruchyx/Kruchyx-Mobile_Medieval2TotalWar`

## A. Aktualizacja istniejącego repozytorium (zalecane: VS Code + Git)

**Ważne:** wcześniej wgrałeś pliki v0.9.5 do dodatkowego katalogu `Kruchyx_Mobile_v0.9.5_`. Nowa paczka jest monorepozytorium: foldery `mobile`, `windows` i `.github` muszą być na samym początku repozytorium, obok README.

1. Pobierz ZIP v0.9.6 i **rozpakuj go do osobnego folderu**, np. `D:\Kruchyx_096_GitHub`. Otwórz ten folder, nie jego nadrzędny katalog.
2. Zainstaluj [Git for Windows](https://git-scm.com/downloads/win), jeśli polecenie `git` nie działa. Otwórz VS Code i terminal PowerShell.
3. Wpisz w terminalu:

   ```powershell
   cd D:\
   git clone https://github.com/Kruchyx/Kruchyx-Mobile_Medieval2TotalWar.git
   cd .\Kruchyx-Mobile_Medieval2TotalWar
   ```

   Jeśli repozytorium zostało już sklonowane, po prostu otwórz jego folder i wykonaj `git pull`.
4. Skopiuj **zawartość** rozpakowanej paczki v0.9.6 do folderu sklonowanego repozytorium. W Eksploratorze Windows zaznacz pliki i foldery: `.github`, `mobile`, `windows`, `docs`, `README.md`, skrypty `BUILD_...` itd. Upewnij się, że pliki `.github/workflows/*.yml` zastąpiły stare pliki o tych samych nazwach. W Windows można włączyć „Pokaż ukryte elementy”.
5. Opcjonalnie usuń **stary** folder `Kruchyx_Mobile_v0.9.5_` z repozytorium (gdy nowy `mobile/kruchyx_mobile/pubspec.yaml` jest już na miejscu). Nie usuwaj nowego folderu `mobile` ani `.github`.
6. W terminalu sklonowanego repozytorium:

   ```powershell
   git status
   git add -A
   git commit -m "Kruchyx Grand Compendium v0.9.6 - Android Windows iOS"
   git push origin main
   ```

   Jeśli Git zapyta o tożsamość, ustaw `git config --global user.name "Kruchyx"` i `git config --global user.email "TWÓJ_EMAIL_GITHUB"` (użyj swojego realnego e-maila lub GitHub noreply). Nie publikuj haseł, kluczy ani zapisów `.sav`.

7. Wejdź na GitHuba: **Code** — na głównym poziomie musisz widzieć `.github`, `mobile`, `windows`, `docs`, `README.md`.

Możesz również wgrać pliki przez przeglądarkę, ale łatwo wtedy niechcący dodać kolejny zbędny podfolder; Git + VS Code jest pewniejszy dla takiej dużej aktualizacji.

## B. Android — pobranie APK bez Android Studio

1. GitHub → zakładka **Actions** → workflow **Kruchyx v0.9.6 - Android APK**.
2. Po wysłaniu `mobile/` powinien uruchomić się sam; w przeciwnym razie wybierz **Run workflow**, gałąź `main`.
3. Otwórz zakończony zielony przebieg.
4. Sekcja **Artifacts** → pobierz `Kruchyx-Android-v0.9.6-APK`.
5. Rozpakuj ZIP pobrany z Artifacts; w środku jest `Kruchyx-Mobile-v0.9.6.apk`.
6. W repozytorium: **Releases → Draft a new release**. Tag `v0.9.6`, tytuł `Kruchyx Grand Compendium v0.9.6`, do sekcji Assets dodaj **sam plik APK**, nie ZIP z Artifacts. Zaznacz pre-release przy pierwszym teście.
7. Otwórz Releases na Androidzie, pobierz APK i uruchom instalator. Android może wymagać zgody na instalowanie z przeglądarki.

**Uwaga o aktualizacji v0.9.5:** GitHub Actions buduje testowy APK z podpisem tworzonym w środowisku runnera. Jeśli telefon odrzuci aktualizację z powodu konfliktu podpisu, należy zrobić kopię ewentualnych własnych danych, odinstalować v0.9.5 i dopiero zainstalować v0.9.6. Stały klucz podpisu jest zadaniem na późniejszą wersję; nie dodawaj kluczy prywatnych do publicznego repozytorium.

## C. Windows — pobranie EXE

1. GitHub → **Actions** → **Kruchyx v0.9.6 - Windows EXE**.
2. Po dodaniu `windows/` build powinien uruchomić się automatycznie; możesz wybrać **Run workflow**.
3. Po zielonym przebiegu pobierz **Kruchyx-Windows-v0.9.6-EXE** w Artifacts.
4. Rozpakuj ZIP z Artifacts — znajdziesz `Kruchyx Medieval Mod Studios.exe`.
5. Na Windows skopiuj EXE do wygodnego katalogu i uruchom. Wybierz folder instalacji Medieval II / modu.
6. Możesz dodać EXE do *tego samego* GitHub Release `v0.9.6`, obok APK, przez edycję wydania.

EXE uruchamia analizator, edytory, trener komend i eksport raportów. Gra i pliki modów pozostają na komputerze. Windows EXE nie jest aplikacją Flutter, tylko dotychczasową aplikacją Python/Tkinter zintegrowaną w repozytorium.

## D. iPhone — testowy, niepodpisany build iOS

1. GitHub → **Actions** → **Kruchyx v0.9.6 - iPhone (unsigned iOS app)**.
2. Kliknij **Run workflow**. MacOS runner skompiluje projekt Flutter.
3. Po sukcesie pobierzesz ZIP z `Runner.app`, ale jest on **niepodpisany**. Nie można go po prostu pobrać na iPhone i zainstalować jak APK!
4. Do instalacji potrzebujesz **macOS + Xcode + podpisu Apple**. Dalsze kroki są w `INSTRUKCJA_BUDOWANIA_IPHONE_PL.md`.

## E. Co robić, gdy zobaczysz czerwony krzyżyk?

Otwórz: Actions → konkretny nieudany przebieg → zadanie Android/Windows/iOS → **pierwszy krok z czerwonym X**. Sprawdź końcowe linijki logu. Nie wymieniaj automatycznie wszystkich plików YAML — najpierw ustal rzeczywisty błąd. Jeżeli np. błędny jest sam kod Flutter, trzeba poprawić plik wskazany w logu `lib/...dart`.

## F. Lokalne budowanie alternatywnie

- **Android Windows:** w katalogu głównym `.\BUILD_ANDROID_v096.bat`; potrzebne Flutter SDK, Android SDK i Java.
- **Windows EXE:** `.\BUILD_WINDOWS_v096.bat`; potrzebny Python 3.10+ i instalowany automatycznie PyInstaller.
- **iOS Mac:** `./BUILD_IPHONE_MAC_v096.command`; potrzebne Flutter i Xcode; ten skrypt tworzy unsigned `.app`, nie podpisane IPA.

Oficjalne dokumenty:
- https://docs.flutter.dev/deployment/android
- https://docs.flutter.dev/platform-integration/ios/setup
- https://docs.flutter.dev/deployment/ios
- https://docs.github.com/actions
