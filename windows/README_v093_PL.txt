KRUCHYX MEDIEVAL MOD STUDIOS — 0.9.3
======================================================

CO NOWEGO:
- Kalkulatory strategii: scenariusze trybutu liczone z twojego skarbca i rezerwy.
- Szybkie presety 10%, 20%, 30%, 50%; liczba tur; bilans wpłat; kopia planu.
- Kalkulator wielu kupców oparty na podanym przez użytkownika dochodzie.
- Linki do kalkulatorów z poradników exploitów.
- Instrukcja Vanilla PL/EN wewnątrz programu, plus osobny plik TXT.
- Wersja 0.9.3 we wszystkich nagłówkach nowego interfejsu.
- Zachowano Academy, analizy modów, trainer i starsze edytory.

JAK URUCHOMIĆ:
1. Rozpakuj całe ZIP.
2. Dwuklik: START_WINDOWS.bat (Python 3 z Tkinterem).
3. Kalkulatory — w menu po lewej, niezależnie od wczytania moda.
4. Biblioteka modów — instrukcja rozpakowania Vanilla i wybór kampanii.

JEDEN EXE:
Na Windows uruchom BUILD_JEDEN_EXE.bat; wymaga Pythona i PyInstaller.
Po POMYŚLNEJ kompilacji wynik znajdziesz w dist\Kruchyx Medieval Mod Studios.exe
Budowanie i działanie EXE wymaga testów na twoim Windows; tutaj nie wykonano kompilacji exe.

UWAGA O TRYBUCIE:
To arytmetyczny symulator, NIE wykrycie maksymalnej kwoty którą AI zaakceptuje.
Procent to propozycja żądania względem jednorazowego prezentu.
Testuj po wykonaniu zapisu kampanii i zawsze sprawdzaj KTO płaci komu.
Nie modyfikujemy pamięci gry ani plików save.

NAPRAWY VANILLA (0.9.3):
- Poprawiona składnia źródła dla starego unpacker.exe (ścieżka względna).
- Obsługa potwierdzeń Y przy zgodzie na rozpakowanie z poziomu GUI.
- Po błędzie pokazywany jest szczegółowy log i przycisk KOPIUJ DIAGNOSTYKĘ.
- Log jest zapisany w katalogu vanilla_cache jako Kruchyx_Vanilla_Unpack.log.
- Nie uruchamiamy unpack_all.bat ani nie zapisujemy danych w folderze gry.
