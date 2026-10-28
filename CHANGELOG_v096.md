# Changelog v0.9.6 — Kruchyx Grand Compendium

### Mobilne Flutter
- Atlas frakcji Vanilla: 22 profile (w tym frakcje specjalne), autorskie ilustracyjne emblematy.
- Atlas 24 miast/regionów: ranking potencjału handlowego i strategicznego (oceny redakcyjne, jawnie opisane).
- Filtrowalne rankingi frakcji: wojsko, gospodarka, łatwość startu, mobilność.
- 32 artykuły „Wielkiej Księgi Mechanik” z wyszukiwaniem.
- Rozbudowany ekran główny z autorskim bannerem oraz bezpośrednim przejściem do atlasów.
- Automatyczny kalkulator trybutu: preset 20% / 33% / 50% skarbca; 40% prezentu jako żądanie; „AI odrzuciło — obniż żądanie”; kopiowanie.
- Zachowanie Kronik, exploitów, kreatora armii, importu raportów i Akademii z v0.9.5.
- Rozszerzona wyszukiwarka o frakcje, miasta i mechaniki.
- Usunięta niedozwolona właściwość `isThreeLine` z `ExpansionTile` (w `ListTile` pozostaje poprawne użycie).

### Windows Python
- Zachowane funkcje v0.9.5 oraz zintegrowany automatyczny doradca trybutu z przyciskami redukcji kwoty.
- Testy deterministycznego kalkulatora dla skarbca 30k.

### GitHub iOS/Android/Windows
- Monorepo z workflowami GitHub Actions dla trzech platform.
- Android `android-actions/setup-android@v4`; Flutter 3.47.8; testy i kompilacja APK.
- Windows PyInstaller jednoplikowy EXE i testy Python.
- iOS macOS runner: unsigned `.app` w ZIP, manualne uruchomienie.
- Kompletna instrukcja po polsku i skrypty lokalne.
