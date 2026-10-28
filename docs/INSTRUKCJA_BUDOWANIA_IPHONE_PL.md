# iPhone/iOS — budowanie i podpisywanie Kruchyx

**Ważne:** Flutter SDK i VS Code na Windows pozwalają edytować projekt iOS, ale **nie** budować finalnego `.ipa` na Windows. Do kompilacji i podpisania wymagane są macOS i Xcode. GitHub Actions z runnerem macOS może wykonać **unsigned** build kontrolny, jednak to nie jest gotowy instalator iPhone’a.

## Jeśli masz dostęp do Maca z Xcode

1. Zainstaluj Flutter SDK i Xcode; uruchom `flutter doctor` i skonfiguruj Xcode Command Line Tools.
2. Skopiuj cały folder `mobile/kruchyx_mobile` z repozytorium na Maca.
3. W Terminalu wykonaj:

   ```bash
   cd /sciezka/do/kruchyx_mobile
   flutter create --platforms=ios --org com.kruchyx .
   flutter pub get
   flutter test
   flutter build ios --release --no-codesign
   ```

4. Otwórz w Xcode `ios/Runner.xcworkspace` (nie tylko `Runner.xcodeproj`).
5. Wybierz target `Runner` → **Signing & Capabilities**, własny **Team** i unikalny Bundle Identifier. Ustaw podpis i profil zgodne z urządzeniem lub dystrybucją.
6. Do testowania na własnym iPhonie podłącz urządzenie do Maca, zaufaj komputerowi, ustaw Developer Mode zgodnie z instrukcją Apple i uruchom projekt przez Xcode. Indywidualne konto Apple ID może umożliwiać bezpłatne testy na swoim urządzeniu, z ograniczeniami; dystrybucja w TestFlight/App Store zwykle wymaga członkostwa Apple Developer Program.
7. Dla podpisanego wydania z odpowiednim kontem/deklaracjami wykonaj archiwizację w Xcode / Organizer lub użyj `flutter build ipa --release`, po przygotowaniu certyfikatów i profili.

**Nie przesyłaj prywatnych certyfikatów i kluczy signing do publicznego GitHuba.** Jeśli chcesz kiedyś generować podpisany IPA na GitHubie, trzeba skonfigurować Secrets, bezpieczny dostęp do certyfikatów oraz provisioning profiles; tej automatyzacji obecna paczka **nie** zawiera.

Oficjalne źródła: https://docs.flutter.dev/deployment/ios i https://docs.flutter.dev/platform-integration/ios/setup
