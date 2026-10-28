import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kruchyx_mobile/main.dart';

void main() {
  test('formatter groups thousands', () {
    expect(fmt(1000000), '1 000 000');
    expect(number(22.5), 22);
  });

  testWidgets('application loads offline knowledge and report', (tester) async {
    await tester.pumpWidget(const KruchyxApp());
    await tester.pumpAndSettle(const Duration(seconds: 4));
    expect(find.text('KRUCHYX'), findsOneWidget);
    expect(find.textContaining('Centrum dowodzenia'), findsWidgets);
  });
}
