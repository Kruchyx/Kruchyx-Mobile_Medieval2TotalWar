# Weryfikacja i znane ograniczenia v0.9.6

## Sprawdzone w środowisku przygotowania paczki

- Testy Python w `windows/`: **83 wykonane, 82 zaliczone, 1 pominięty** (uruchomione `python -m unittest discover -p 'test_*.py' -q`).
- Wszystkie moduły Python przechodzą `compileall`.
- Walidacja składni YAML w trzech workflowach, w tym `setup-android@v4` (naprawa błędu `Failed to find package tools` z v0.9.5).
- Walidacja JSON atlasu: 22 frakcje, 24 miasta; osobny plik: 32 opisy mechanik; 22 grafiki PNG.
- Kalkulator Windows: dla 30 000 fl. zwraca prezent 10 000, trybut 4 000, rezerwę 20 000.
- Utworzone archiwa ZIP zostały sprawdzone pod kątem uszkodzenia wpisów.

## Czego NIE sprawdzono w tym środowisku

- Flutter `flutter test`, `flutter analyze` i `flutter build apk --release` dla **nowego** kodu v0.9.6 (Flutter SDK nie jest zainstalowany w dostępnym środowisku). Poprzednia v0.9.5 została zbudowana pomyślnie przez użytkownika na GitHubie, ale to nie jest dowód powodzenia nowej kompilacji.
- Rzeczywisty Windows PyInstaller na Windows i działanie EXE w instalacji Medieval II.
- Build iOS na Macu i podpisanie certyfikatami Apple.
- Zachowanie exploitów w każdym modzie i skuteczność żądania trybutu.

## Specyfika Androida

Karty frakcji i miast to atlas orientacyjny podstawowej gry. Ranking 1–5 jest oceną redakcyjną, nie pochodną EDU. Mobilny kreator armii i szczegółowe karty jednostek korzystają z zaimportowanego raportu, który należy utworzyć w Windows; początkowe dane demonstracyjne nie stanowią pełnej bazy statystyk Vanilla.

## Specyfika iPhone'a

Workflow generuje **unsigned Runner.app**, zapakowany w ZIP. To nie jest podpisana paczka IPA i nie jest bezpośrednio instalowalna na telefonie. Podpisanie i własna dystrybucja wymagają Mac/Xcode i odpowiedniego Apple ID / konta Apple Developer.

## Licencje i źródła grafik

Emblematy i banner zostały wygenerowane dla tej aplikacji jako **własne, ilustracyjne grafiki**, a nie skopiowane ekrany/grafiki Medieval II. Nie publikuj dodatkowych kart i tekstur pochodzących z gry lub cudzych modów bez uprawnienia. Dane zaimportowane z prywatnych instalacji powinny zostać na urządzeniu użytkownika, chyba że ich licencja pozwala na redystrybucję.

**Ważne dla repozytorium publicznego:** paczka Windows zachowuje wcześniejsze pliki testowe `examples/export_descr_unit.txt` i `fixtures/kirsi_descr_strat.txt` powiązane z modami. Ich uprawnienia redystrybucyjne nie zostały zweryfikowane; przed publikacją publiczną sprawdź licencję lub zastąp je własnymi fixtures. Usunięcie ich bez dostosowania testów może zepsuć automatyczny build Windows.
