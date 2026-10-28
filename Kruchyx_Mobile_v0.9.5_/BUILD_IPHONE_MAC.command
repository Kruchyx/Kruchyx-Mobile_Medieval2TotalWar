#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
echo 'Kruchyx Mobile v0.9.5 — iOS (macOS + Xcode)'
command -v flutter >/dev/null || { echo 'Zainstaluj Flutter SDK: https://docs.flutter.dev/platform-integration/ios/setup'; exit 1; }
flutter doctor
flutter create --platforms=ios --org com.kruchyx .
flutter pub get
flutter analyze
flutter test
echo 'Otworz ios/Runner.xcworkspace i ustaw Team / Bundle Identifier w Signing & Capabilities.'
echo 'Nastepnie uruchom: flutter run -d <ID_iphone> lub flutter build ipa.'
echo 'Generuje niesygnowany build kontrolny iOS...'
flutter build ios --release --no-codesign
echo 'Gotowe: build/ios/iphoneos/Runner.app (niesygnowany, nie do instalacji bez podpisu).'
