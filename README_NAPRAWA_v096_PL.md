# Naprawa kompilacji Kruchyx v0.9.6 (Android + Windows)

Ta paczka zawiera **tylko poprawione pliki**. Wgraj całą zawartość rozpakowanego ZIP-a do **głównego folderu** sklonowanego repozytorium `Kruchyx-Mobile_Medieval2TotalWar`. Wyraź zgodę na zastąpienie istniejących plików, ale nie usuwaj `.git` ani innych folderów.

## Dlaczego poprzedni build nie przeszedł

- Android: `flutter create` dodał domyślny `test/widget_test.dart`, który próbował wywołać `MyApp()`. W Kruchyx istnieje `KruchyxApp`, nie `MyApp`. Nowy `widget_test.dart` w repozytorium zapobiega generowaniu testu demo i sprawdza faktyczny kalkulator.
- Windows: `test_analytics.py` odwoływał się do `/mnt/data/...`, nieobecnego na runnerze Windows. Testy korzystają teraz z wersji demonstracyjnych plików w `windows/examples`. Dodatkowo porównania ścieżek zostały uodpornione na aliasy `runneradmin` / `RUNNER~1`.

## Kroki

1. Rozpakuj patch ZIP.
2. Skopiuj **zawartość** patcha (foldery `.github`, `mobile`, `windows`, plik README) do `Dokumenty\GitHub\Kruchyx-Mobile_Medieval2TotalWar`.
3. Kliknij **Zastąp pliki w miejscu docelowym** (jeśli system spyta).
4. Otwórz GitHub Desktop: `Changes` → wpisz `Fix Android and Windows build tests v0.9.6` → `Commit to main` → `Push origin`.
5. Otwórz `https://github.com/Kruchyx/Kruchyx-Mobile_Medieval2TotalWar/actions`. Nowy commit powinien wywołać obie kompilacje.
6. Jeśli którykolwiek proces zakończy się czerwono, otwórz nieudany krok i sprawdź pełny błąd. Nowa paczka eliminuje **konkretne problemy pokazane na screenach**, ale nie gwarantuje jeszcze kompletnej kompilacji wszystkich platform.

Wersja iOS również korzysta z `flutter test`, więc ten sam `widget_test.dart` naprawia potencjalny błąd testu MyApp na Macu. Produkcyjny plik IPA nadal wymaga podpisu Apple.
