// Kept in source control so `flutter create` does not generate the default
// Flutter demo widget test calling MyApp (not part of Kruchyx).
// The main app integration tests live in kruchyx_test.dart.
import 'package:flutter_test/flutter_test.dart';
import 'package:kruchyx_mobile/main.dart';

void main() {
  test('Kruchyx v0.9.6 currency formatting', () {
    expect(fmt(30000), '30 000');
    final proposal = suggestTributeOffer(30000);
    expect(proposal['gift'], 10000);
    expect(proposal['request'], 4000);
  });
}
