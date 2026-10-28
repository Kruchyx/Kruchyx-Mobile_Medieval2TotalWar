#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/mobile/kruchyx_mobile"
flutter create --platforms=ios --org com.kruchyx .
flutter pub get
flutter test
flutter build ios --release --no-codesign
printf 'Unsigned .app: %s\n' "$(pwd)/build/ios/iphoneos/Runner.app"
printf 'Do instalacji na fizycznym iPhonie potrzebne jest podpisanie w Xcode.\n'
