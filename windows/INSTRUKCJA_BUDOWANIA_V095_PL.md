# KRUCHYX MEDIEVAL MOD STUDIOS v0.9.5 — INSTRUKCJA BUDOWANIA

**Wykonane przez Kruchyx** • Windows (Python/Tkinter) + Android/iPhone (Flutter)

## Co jest w paczce

- `kruchyx_studio.py`: zachowany interfejs i funkcje Windows z v0.9.4, rozszerzony do v0.9.5.
- `empire_companion.py`: Kroniki, wyszukiwarka, kreator armii 20 slotów, eksport JSON.
- `shared/knowledge_v095.json`: baza porad, exploitów i wydarzeń z oznaczeniem pewności.
- `mobile/kruchyx_mobile/`: **rzeczywisty projekt źródłowy Flutter**, współdzielony przez Android/iOS.
- `mobile/kruchyx_mobile/assets/demo_report.json`: demonstracyjne jednostki z dostarczonego wcześniej EDU, NIE bazowe Vanilla.
- `test_v095_companion.py`: testy parsowania wydarzeń i eksportu.

**W paczce są źródła i skrypty budowania; nie ma gotowego EXE, APK ani IPA.** W obecnym środowisku nie ma Windows, Flutter SDK ani Xcode, więc nie można było wykonać natywnych kompilacji. Poniższe kroki wykonuje się na odpowiednich systemach.

## A. Windows: uruchomienie źródeł (najprostsze)

1. Rozpakuj ZIP, najlepiej do `D:\Kruchyx\v0.9.5`.
2. Zainstaluj **Python 3.10 lub nowszy** ze strony https://www.python.org/downloads/windows/; zaznacz dodanie Python do PATH.
3. Kliknij `START_WINDOWS.bat` albo w terminalu VS Code z folderu projektu wpisz:

   ```powershell
   py -3 kruchyx_studio.py
   ```

4. Wybierz folder Medieval II, Vanilla lub moda. W razie potrzeby odczytaj archiwa Vanilla według istniejącej `INSTRUKCJA_VANILLA_PL.txt`.
5. Otwórz „Kroniki kampanii”, „Kreator armii”, „Wyszukiwarka” i „Kruchyx Mobile”.

**Pamiętaj:** aplikacja nie steruje pamięcią gry. Cheat trainer generuje polecenia konsoli; reszta analizuje pliki. Zrób kopię zapisów przed użyciem edytorów.

## B. Windows: kompilacja pojedynczego EXE

1. Na **komputerze Windows** z Python 3.10+ otwórz rozpakowany folder.
2. Dwukrotnie kliknij `BUILD_WINDOWS_v095.bat` (alternatywnie `BUILD_JEDEN_EXE.bat`).
3. Skrypt instaluje PyInstaller, wykonuje testy Python i kompiluje program.
4. Wynik: `dist\Kruchyx Medieval Mod Studios.exe`.
5. Skopiuj EXE na komputer z Medieval II, uruchom i sprawdź wczytywanie moda.

Przy problemach z antywirusem, uruchamianiem lub brakującym plikiem `shared`: sprawdź log terminala. Buduj na Windows, nie na Linuksie. Oficjalna dokumentacja: https://pyinstaller.org/en/stable/usage.html .

## C. Android: APK z Windows + VS Code

1. Zainstaluj **Flutter SDK (stable)** i dodaj folder `flutter\bin` do systemowego PATH: https://docs.flutter.dev/get-started/install/windows/mobile .
2. Zainstaluj **Android Studio** z Android SDK, Command-line Tools i Platform Tools. VS Code jest wygodnym edytorem, ale Android SDK nadal jest potrzebny.
3. Otwórz PowerShell lub terminal VS Code i wykonaj:

   ```powershell
   flutter doctor
   flutter doctor --android-licenses
   ```

4. Przejdź do folderu mobilnego i uruchom skrypt:

   ```powershell
   cd mobile\kruchyx_mobile
   .\BUILD_ANDROID_WINDOWS.bat
   ```

   Skrypt sam wygeneruje **standardowe pliki platformowe Androida** (`flutter create --platforms=android --org com.kruchyx .`), rozwiąże zależności, wykona analizę/testy i zbuduje APK.

5. Wynik: `mobile\kruchyx_mobile\build\app\outputs\flutter-apk\app-release.apk`.
6. Przenieś APK na Androida i zainstaluj po włączeniu instalowania aplikacji z wybranego zaufanego źródła. Możesz też podłączyć telefon USB i wykonać `flutter install`.

**Google Play:** do publikacji użyj `flutter build appbundle` i skonfiguruj klucz podpisu release zgodnie z oficjalną instrukcją. APK wygenerowany bez własnego release-keystore jest przeznaczony do testów i lokalnego użycia, NIE do publikacji. Oficjalna dokumentacja: https://docs.flutter.dev/deployment/android .

### Android: jeśli chcesz uruchomić bez skryptu

```powershell
cd mobile\kruchyx_mobile
flutter create --platforms=android --org com.kruchyx .
flutter pub get
flutter analyze
flutter test
flutter run
flutter build apk --release
```

**Ważne:** `flutter create .` uzupełnia brakujące katalogi `android/` i nie powinno nadpisywać istniejącego `lib/main.dart` bez opcji `--overwrite`. Nie używaj `--overwrite` przy aktualizacji.

## D. iPhone: kompilacja i instalacja z macOS

**Na samym Windows nie zbudujesz ani nie podpiszesz IPA na iPhone’a.** Potrzebujesz Maca (lub usługi macOS CI) z Xcode i Flutter SDK. Oficjalnie: https://docs.flutter.dev/platform-integration/ios/setup .

1. Skopiuj cały folder `mobile/kruchyx_mobile` na Maca.
2. Zainstaluj najnowszy zgodny **Xcode** i **Flutter SDK**. W Terminalu:

   ```bash
   sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
   sudo xcodebuild -runFirstLaunch
   flutter doctor
   ```

3. W folderze `mobile/kruchyx_mobile` wykonaj:

   ```bash
   flutter create --platforms=ios --org com.kruchyx .
   flutter pub get
   flutter analyze
   flutter test
   ```

4. Otwórz w Xcode **`ios/Runner.xcworkspace`** (nie sam `Runner.xcodeproj`).
5. W **Runner → Signing & Capabilities** wybierz swoje **Team** (konto Apple ID lub Apple Developer), włącz **Automatically manage signing** i ustaw unikatowy **Bundle Identifier** (np. `com.kruchyx.medievalcompanion` zamiast domyślnego, jeśli jest zajęty).
6. Podłącz iPhone’a, zaufaj komputerowi i włącz **Developer Mode**, jeśli system o to poprosi.
7. W Terminalu wykonaj:

   ```bash
   flutter devices
   flutter run -d ID_URZADZENIA
   ```

8. Do dystrybucji przez TestFlight/App Store potrzebne jest uczestnictwo w Apple Developer Program, konfiguracja certyfikatów i provisioning profiles; wykonaj:

   ```bash
   flutter build ipa --release
   ```

   Wynik to katalog `build/ios/ipa/` (tylko przy prawidłowym podpisie). Można też uruchomić `./BUILD_IPHONE_MAC.command`, który przygotowuje niesygnowany build kontrolny, a nie instalowalny IPA.

Oficjalna dokumentacja: https://docs.flutter.dev/deployment/ios . **Konto Apple ID może wystarczyć do lokalnych testów na własnym urządzeniu; TestFlight/App Store wymagają programu deweloperskiego.**

## E. Przenoszenie danych z Windows do Androida i iPhone’a

1. W Kruchyx Windows wybierz moda i przeprowadź analizę.
2. Otwórz **Kruchyx Mobile** → **EKSPORTUJ RAPORT NA TELEFON**.
3. Otrzymasz `Kruchyx_Mobile_Raport.json` z jednostkami, frakcjami i wykrytymi wydarzeniami. Nie zawiera zapisów ani kluczy systemowych.
4. Przenieś go na Androida (USB, Dysk, Wiadomości) lub iPhone’a (iCloud Drive, AirDrop, aplikacja Pliki).
5. Na telefonie w Kruchyx wybierz ikonę **Importuj raport** i wskaż JSON. Wczyta się lokalnie, bez sieci i bez konta.
6. Po ponownym uruchomieniu aplikacja wraca do przykładu DEMO — **v0.9.5 nie zapisuje jeszcze importu na stałe**.

## F. Najważniejsze ograniczenia v0.9.5

- **Brak Live Trainera** i sterowania grą z telefonu; mobilny Kruchyx to aplikacja offline.
- Wydarzenia w plikach `descr_events.txt` są podawane w **latach od początku kampanii**; przelicznik na turę w tej wersji zakłada 2 lata/turę. Mody ze zmienioną skalą mogą mieć inne wyniki.
- Skrypty (`campaign_script.txt`) decydują o pojawieniu się hord **po** ostrzeżeniu; sama data nie oznacza automatycznie spawnu.
- Kreator armii korzysta z EDU; nie sprawdza faktycznej dostępności budynków, bonusów i rekrutacji z aktualnego zapisu.
- W Windows baza wiedzy zawiera instrukcje i eksploity do testowania, ze źródłami i ostrzeżeniami. Nie twierdzimy, że wszystkie działają w każdej wersji gry.
- Tylko właściciel urządzenia i uprawniony wydawca może zgodnie z regułami sklepów publikować aplikację; to prywatny projekt fanowski, niezwiązany z Creative Assembly/Sega.

## G. Testy i diagnostyka

- Windows: `py -3 -m unittest discover -p "test_*.py"`.
- Flutter: `flutter analyze` i `flutter test` w folderze `mobile/kruchyx_mobile`.
- Nie wykonano tutaj natywnej kompilacji EXE/APK/IPA ani testu na fizycznym Windows/Android/iOS; zweryfikowano testy Python i format zasobów.

**Nie dodajemy „Trybu Brata”.** Jest jedna pełna wersja na każdą platformę.
