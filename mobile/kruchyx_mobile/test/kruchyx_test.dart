import 'package:flutter_test/flutter_test.dart';
import 'package:kruchyx_mobile/main.dart';

void main() {
  test('formatter groups thousands', () {
    expect(fmt(1000000), '1 000 000');
    expect(number(22.5), 22);
  });

  test('calculator: 30k -> 10k gift / 4k per turn / 20k reserve', () {
    final plan = suggestTributeOffer(30000);
    expect(plan['gift'], 10000);
    expect(plan['request'], 4000);
    expect(plan['reserve'], 20000);
    expect(suggestTributeOffer(30000, rejections: 1)['request'], 3600);
    expect(suggestTributeOffer(30000, preset: 'safe')['gift'], 6000);
    expect(suggestTributeOffer(30000, preset: 'aggressive')['gift'], 15000);
  });

  testWidgets('application loads offline compendium', (tester) async {
    await tester.pumpWidget(const KruchyxApp());
    await tester.pumpAndSettle(const Duration(seconds: 4));
    expect(find.text('KRUCHYX'), findsOneWidget);
    expect(find.textContaining('Centrum dowodzenia'), findsWidgets);
    expect(find.text('Wielkie kompendium Medieval II'), findsOneWidget);
  });
}
