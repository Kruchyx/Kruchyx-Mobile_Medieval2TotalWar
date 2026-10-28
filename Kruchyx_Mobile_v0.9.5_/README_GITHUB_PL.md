# Kruchyx Mobile v0.9.5 — Android przez GitHub Actions

Ten projekt jest gotowy do wgrania na GitHuba i wygenerowania **APK na serwerach GitHub**. Na komputerze nie musisz instalować Android Studio ani Android SDK.

## Instrukcja krok po kroku

1. Rozpakuj ten ZIP. W katalogu glownym sa pliki `pubspec.yaml` i foldery `lib`, `assets`, `.github`.
2. Na https://github.com/new stworz repozytorium, najlepiej prywatne. Nazwa np. `Kruchyx-Mobile`.
3. Wgraj **zawartosc rozpakowanego folderu**, nie sam plik ZIP. `pubspec.yaml` musi znajdowac sie w katalogu glownym repozytorium. Wgraj tez `.github/workflows/build-android.yml`.
4. Otworz w repozytorium zakladke **Actions**, wybierz **Kruchyx Mobile - build Android APK**, kliknij **Run workflow**, potem zielony przycisk uruchomienia.
   - Workflow uruchomi sie tez automatycznie po przeslaniu plikow do galezi `main`.
5. Gdy kompilacja sie powiedzie (zielony znacznik), otworz skonczony przebieg. U dolu w **Artifacts** pobierz `Kruchyx-Mobile-v0.9.5-APK`.
6. GitHub udostepnia artifact jako ZIP: rozpakuj go i znajdz `app-release.apk`.
7. Jezeli chcesz pobierac APK na telefon bez rozpakowywania archiwum, utworz w repozytorium **Releases -> Draft a new release**, tag `v0.9.5`, dodaj `app-release.apk` do Assets i opublikuj wydanie. Potem na telefonie otworz GitHub -> Releases -> Assets -> APK.
8. Android moze poprosic o zgode na instalacje aplikacji z przegladarki. Instaluj tylko swoj sprawdzony build.

## Wazne

- Sam GitHub Pages nie uruchamia natywnego APK; dla aplikacji w przegladarce potrzebny jest osobny build Flutter Web.
- To **testowy build**, nie gotowy oficjalny pakiet podpisany kluczem produkcyjnym. Dla przyszlych aktualizacji Androida bez reinstalacji nalezy skonfigurowac staly klucz podpisu i bezpiecznie przechowywac go np. w GitHub Actions Secrets.
- Nie wgrywaj do publicznego repo prywatnych zapisow gry, sekretow, kluczy podpisu ani plikow modow z ograniczeniami licencyjnymi.
- Konfiguracji nie uruchomiono na serwerach GitHub w tym srodowisku. Jesli build ma blad, sprawdz log w zakladce Actions.
- Workflow wymaga uprawnienia GitHub Actions dla repozytorium oraz dostepnych minut GitHub Actions (plan i limity moga sie roznic).
- Projekt korzysta z Flutter 3.47.8 tak jak instalacja, ktora pokazales w `flutter doctor`.
