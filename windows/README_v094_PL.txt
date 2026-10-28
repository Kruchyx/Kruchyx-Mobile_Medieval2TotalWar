Kruchyx Medieval Mod Studios v0.9.4 — Naprawa odczytu Vanilla

Dla logu użytkownika z dnia 25.10.2026:
- Oficjalny unpacker.exe uruchamia się poprawnie (exit 0).
- Z plików .pack znaleziono 4 definicje: EDU, EDB, zasoby oraz descr_campaign_db.xml.
- descr_regions.txt i descr_strat.txt mogą leżeć luzem w data/world/maps i nie muszą być w .pack.

Poprawki w v0.9.4:
- Nowy wspólny stan plików: z archiwum / w katalogu gry / brak.
- Rozpoznawanie luźnych opisów regionów i kampanii Vanilla, bez modyfikacji gry.
- Dziennik diagnostyczny rozdziela FOUND_IN_PACK_CACHE i FOUND_IN_GAME_FOLDER.
- Instrukcja krok po kroku wskazuje oba położenia i sprawdza ich obecność.
- Obsługa starego błędu DLL 0xC0000135 pozostaje dostępna: PATH procesu + opcjonalna naprawa wyłącznie za zgodą.
- Po przełączeniu języka wraca znikająca wcześniej zakładka Kalkulatory.

Ochrona gry:
Wszystkie dane z .pack trafiają tylko do LOCALAPPDATA/Kruchyx.../vanilla_cache,
a dwa luźne pliki są odczytywane bezpośrednio z gry — tylko do odczytu.
Nie uruchamiaj unpack_all.bat.

Uruchom START_WINDOWS.bat albo zbuduj pojedynczy EXE przez BUILD_JEDEN_EXE.bat na Windows.
Wynik EXE oraz zgodność ze Steam nie były tutaj zweryfikowane na fizycznej instalacji gry.
