# KRUCHYX MEDIEVAL MOD STUDIOS v0.9.6 — GRAND COMPENDIUM

**Wykonane przez Kruchyx** · Medieval II: Total War companion · Windows / Android / iPhone (źródła iOS)

Ten ZIP jest gotowym **monorepozytorium GitHub**: rozpakuj i prześlij *zawartość*, tak aby `.github`, `windows`, `mobile` i `README.md` leżały bezpośrednio na gałęzi `main`. Nie publikuj samego ZIP zamiast zawartości.

## Co jest w paczce?

- **Windows (`windows/`):** oryginalny Kruchyx v0.9.5 wraz z nowym automatycznym kalkulatorem negocjacji i numerem v0.9.6. Zachowano dotychczasowe narzędzia: analizator modów/EDU, eksplorator save, trener komend, pakiety MAX, Kroniki, Akademię, rankingi, kreator armii, kalkulatory i edytory.
- **Android / iPhone (`mobile/kruchyx_mobile/`):** Flutter v0.9.6, na bazie wcześniej uruchomionej przez użytkownika wersji v0.9.5. Dodano atlas 22 frakcji z 22 **autorskimi emblematami ilustracyjnymi**, atlas 24 lokalizacji, filtrowane rankingi, 32 nowe hasła mechanik, duży nagłówek graficzny, bardziej rozbudowaną wyszukiwarkę, poprawiony atlas jednostek z importu danych, automatyczny kalkulator żądania trybutu.
- **GitHub Actions (`.github/workflows/`):** trzy oddzielne workflowy: Android APK (Linux), Windows EXE (Windows) i iOS unsigned `.app` (macOS, uruchamiany ręcznie).
- **Skrypty lokalne:** `BUILD_WINDOWS_v096.bat`, `BUILD_ANDROID_v096.bat`, `BUILD_IPHONE_MAC_v096.command`.

> **Nie zawiera prekompilowanych EXE / APK / IPA.** Kompilację przeprowadza GitHub Actions lub lokalne środowisko z odpowiednim SDK. Testów Flutter na GitHubie nie uruchomiono jeszcze dla v0.9.6. Weryfikacja testów Python została wykonana lokalnie.

## Najprostsza droga: aktualizuj istniejące repozytorium

Masz już repozytorium [Kruchyx-Mobile_Medieval2TotalWar](https://github.com/Kruchyx/Kruchyx-Mobile_Medieval2TotalWar). Zobacz **`docs/INSTRUKCJA_GITHUB_PL.md`** — szczegółowe kroki od sklonowania repozytorium do pobrania APK/EXE.

## GitHub Actions — co pobierzesz?

| Workflow | Uruchamianie | Artefakt | Instalacja |
|---|---|---|---|
| `Kruchyx v0.9.6 - Android APK` | po zmianach w `mobile/`, ręcznie | `Kruchyx-Mobile-v0.9.6.apk` | Android, po pobraniu z Artifacts/Release |
| `Kruchyx v0.9.6 - Windows EXE` | po zmianach w `windows/`, ręcznie | `Kruchyx Medieval Mod Studios.exe` | Windows PC |
| `Kruchyx v0.9.6 - iPhone (unsigned iOS app)` | **tylko ręcznie** | ZIP z niepodpisanym `Runner.app` | NIE jest gotowym instalatorem iPhone’a — wymaga podpisania przez Apple |

Komendy lokalne:

```powershell
# Windows, w katalogu głównym repozytorium
.\BUILD_WINDOWS_v096.bat
.\BUILD_ANDROID_v096.bat
```

```bash
# macOS + Xcode, w katalogu głównym
./BUILD_IPHONE_MAC_v096.command
```

## Przykład automatycznego kalkulatora dyplomacji

Wariant zrównoważony dla skarbca 30 000 fl.:

- jednorazowy prezent AI: **10 000 fl.**
- żądany trybut od AI: **4 000 fl./turę**
- rezerwa w twoim skarbcu: **20 000 fl.**
- teoretyczne odzyskanie prezentu: **po 3 faktycznych wpłatach**

**Ostrzeżenie:** to wyłącznie heurystyka (ok. 1/3 skarbca jako prezent i ok. 40% prezentu jako żądanie). Nie jest to odkryty algorytm Medieval II, kalkulator szans ani obietnica akceptacji lub wypłaty przez AI. Przycisk „AI odrzuciło” obniża propozycję, ale nie uczy się modelu gry ani nie komunikuje się z AI w grze.

## Wiarygodność atlasu

- Oceny frakcji i miast 1–5 są **subiektywnymi ocenami redakcyjnymi**, z podanymi kryteriami. Nie są rzeczywistymi dochodami, wynikiem symulacji bitwy ani rankingami wyliczonymi z każdej kampanii.
- Atlas miast ma charakter strategiczno-geograficzny; **położenie i własność osad w konkretnym modzie** potwierdzaj poprzez jego pliki kampanii.
- Autorskie herby/emblematy nie są oficjalnymi herbami z Medieval II ani kopią grafik gry.
- Karty jednostek w telefonie korzystają z **przykładowego raportu** lub prawdziwego JSON zaimportowanego z Kruchyx Windows; nie obiecujemy nieistniejących danych o jednostkach z instalacji gracza bez importu.
- W folderze `windows/examples` i `windows/fixtures` są historyczne pliki testowe EDU i kampanii przekazane podczas wcześniejszych iteracji projektu. **Przed przesłaniem całego repozytorium jako PUBLIC sprawdź, czy wolno je redystrybuować; jeżeli nie, usuń te pliki i dostosuj testy/dema do własnych przykładów.** Nie publikuj bez zgody zasobów należących do twórców modów.

## Wersje i wymagania

Flutter 3.47.8 · Dart w zestawie Flutter · Python >=3.10 na Windows · GitHub Actions do budowania bez lokalnych SDK · iOS: Xcode na macOS i podpisanie aplikacji do instalacji. Testowe APK z różnych maszyn CI mogą być podpisane innymi kluczami, więc aktualizacja poprzedniego wydania może wymagać odinstalowania starej wersji. Do stabilnych aktualizacji skonfiguruj własny klucz podpisu.

## Szczegółowe instrukcje

- [`docs/INSTRUKCJA_GITHUB_PL.md`](docs/INSTRUKCJA_GITHUB_PL.md)
- [`docs/INSTRUKCJA_BUDOWANIA_IPHONE_PL.md`](docs/INSTRUKCJA_BUDOWANIA_IPHONE_PL.md)
- [`docs/WERYFIKACJA_I_OGRANICZENIA.md`](docs/WERYFIKACJA_I_OGRANICZENIA.md)
