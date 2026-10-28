import 'dart:convert';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

const ink = Color(0xFFF0E9DB);
const gold = Color(0xFFE2BB75);
const base = Color(0xFF0D1418);
const panel = Color(0xFF1C292F);
const muted = Color(0xFFB6C0BD);

void main() => runApp(const KruchyxApp());

List<Map<String, dynamic>> rows(dynamic value) => value is List
    ? value.whereType<Map>().map((e) => Map<String, dynamic>.from(e)).toList()
    : <Map<String, dynamic>>[];

int number(dynamic value) => value is num ? value.toInt() : int.tryParse('$value') ?? 0;
String text(dynamic value) => value?.toString() ?? '';
String fmt(int value) => value.toString().replaceAllMapped(
      RegExp(r'\B(?=(\d{3})+(?!\d))'), (m) => ' ',
    );

/// An experimental proposal; it does NOT model or guarantee AI acceptance.
Map<String, int> suggestTributeOffer(int rawTreasury, {String preset = 'balanced', int rejections = 0}) {
  final treasury = rawTreasury.clamp(0, 2000000000).toInt();
  final steps = rejections.clamp(0, 9).toInt();
  final gift = switch (preset) {
    'safe' => ((treasury * 20) ~/ 10000) * 100,
    'aggressive' => ((treasury * 50) ~/ 10000) * 100,
    _ => ((treasury ~/ 3) ~/ 100) * 100,
  };
  final baseRequest = ((gift * 40) ~/ 10000) * 100;
  final request = ((baseRequest * (10 - steps)) ~/ 10 ~/ 100) * 100;
  return {'treasury': treasury, 'gift': gift, 'request': request, 'reserve': treasury - gift};
}


class KruchyxApp extends StatelessWidget {
  const KruchyxApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Kruchyx Empire Companion',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          brightness: Brightness.dark,
          scaffoldBackgroundColor: base,
          colorScheme: ColorScheme.fromSeed(
            seedColor: gold,
            brightness: Brightness.dark,
            surface: panel,
          ),
          appBarTheme: const AppBarTheme(backgroundColor: base, foregroundColor: ink),
          cardTheme: CardThemeData(color: panel, elevation: 0, margin: const EdgeInsets.symmetric(vertical: 5)),
          inputDecorationTheme: InputDecorationTheme(
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          ),
        ),
        home: const KruchyxHome(),
      );
}

class KruchyxHome extends StatefulWidget {
  const KruchyxHome({super.key});
  @override
  State<KruchyxHome> createState() => _KruchyxHomeState();
}

class _KruchyxHomeState extends State<KruchyxHome> {
  Map<String, dynamic> knowledge = {};
  Map<String, dynamic> codex = {};
  Map<String, dynamic> mechanics = {};
  String mechanicQuery = '';
  Map<String, dynamic> report = {};
  String? error;
  int page = 0;
  int turn = 60;
  String search = '';
  String faction = '';
  final Map<String, int> army = {};
  final TextEditingController giftController = TextEditingController(text: '3333333');
  final TextEditingController tributeController = TextEditingController(text: '1000000');
  final TextEditingController turnsController = TextEditingController(text: '20');
  final TextEditingController filterController = TextEditingController();
  final TextEditingController searchController = TextEditingController();
  String unitFilter = '';
  String factionQuery = '';
  String cityQuery = '';
  String citySort = 'trade_index';
  String rankingMetric = 'wojsko';
  bool showSpecial = false;
  String diplomacyPreset = 'balanced';
  int rejectedSteps = 0;
  bool autoDiplomacy = true;
  final TextEditingController treasuryController = TextEditingController(text: '30000');

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final a = jsonDecode(await rootBundle.loadString('assets/knowledge_v095.json')) as Map;
      final b = jsonDecode(await rootBundle.loadString('assets/demo_report.json')) as Map;
      final c = jsonDecode(await rootBundle.loadString('assets/codex_v096.json')) as Map;
      final d = jsonDecode(await rootBundle.loadString('assets/mechanics_v096.json')) as Map;
      final loaded = Map<String, dynamic>.from(b);
      if (loaded['schema'] != 'kruchyx-companion-v1') throw const FormatException('Nieobsługiwany format danych');
      if (!mounted) return;
      setState(() {
        knowledge = Map<String, dynamic>.from(a);
        codex = Map<String, dynamic>.from(c);
        mechanics = Map<String, dynamic>.from(d);
        report = loaded;
        final fs = rows(report['factions']);
        faction = fs.isEmpty ? '' : text(fs.first['name']);
      });
    } catch (e) {
      if (mounted) setState(() => error = '$e');
    }
  }

  Future<void> _import() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom, allowedExtensions: ['json'], withData: true,
      );
      if (result == null || result.files.isEmpty) return;
      final bytes = result.files.single.bytes;
      if (bytes == null) throw const FormatException('Nie udało się odczytać pliku. Skopiuj go lokalnie i ponów próbę.');
      final decoded = jsonDecode(utf8.decode(bytes)) as Map;
      final incoming = Map<String, dynamic>.from(decoded);
      if (incoming['schema'] != 'kruchyx-companion-v1') {
        throw const FormatException('Nie jest to raport Kruchyx Companion v1');
      }
      final fs = rows(incoming['factions']);
      if (!mounted) return;
      setState(() {
        report = incoming;
        faction = fs.isEmpty ? '' : text(fs.first['name']);
        army.clear();
        unitFilter = '';
        filterController.clear();
      });
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Wczytano raport z Windows.')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Błąd importu: $e')));
    }
  }

  @override
  void dispose() {
    treasuryController.dispose();
    giftController.dispose();
    tributeController.dispose();
    turnsController.dispose();
    filterController.dispose();
    searchController.dispose();
    super.dispose();
  }

  void navigate(int id) {
    Navigator.of(context).maybePop();
    setState(() => page = id);
  }

  @override
  Widget build(BuildContext context) {
    final pages = ['Centrum dowodzenia', 'Kroniki', 'Exploity', 'Kreator armii', 'Kalkulator', 'Akademia', 'Szukaj', 'Raport', 'Atlas frakcji', 'Atlas miast', 'Rankingi', 'Atlas jednostek', 'Mechaniki gry'];
    return Scaffold(
      appBar: AppBar(
        title: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('KRUCHYX', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 2, color: gold, fontSize: 18)),
          Text('${pages[page]}  •  v0.9.6', style: const TextStyle(color: muted, fontSize: 12)),
        ]),
        actions: [IconButton(tooltip: 'Wczytaj raport', icon: const Icon(Icons.file_open, color: gold), onPressed: _import)],
      ),
      drawer: Drawer(
        backgroundColor: panel,
        child: SafeArea(child: ListView(children: [
          const ListTile(title: Text('EMPIRE COMPANION', style: TextStyle(color: gold, fontWeight: FontWeight.bold)), subtitle: Text('Wykonane przez Kruchyx')),
          const Divider(),
          for (var i = 0; i < pages.length; i++)
            ListTile(
              selected: page == i,
              leading: Icon([Icons.home, Icons.event, Icons.auto_stories, Icons.shield, Icons.calculate, Icons.school, Icons.search, Icons.import_export, Icons.flag, Icons.location_city, Icons.emoji_events, Icons.military_tech, Icons.menu_book][i]),
              title: Text(pages[i]),
              onTap: () => navigate(i),
            ),
        ])),
      ),
      body: error != null
          ? Center(child: Text('Błąd inicjalizacji: $error'))
          : knowledge.isEmpty
              ? const Center(child: CircularProgressIndicator())
              : SafeArea(child: _content()),
      bottomNavigationBar: NavigationBar(
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        selectedIndex: [0, 8, 9, 4, 10].contains(page) ? [0, 8, 9, 4, 10].indexOf(page) : 0,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Start'),
          NavigationDestination(icon: Icon(Icons.flag_outlined), label: 'Frakcje'),
          NavigationDestination(icon: Icon(Icons.location_city_outlined), label: 'Miasta'),
          NavigationDestination(icon: Icon(Icons.calculate_outlined), label: 'Trybut'),
          NavigationDestination(icon: Icon(Icons.emoji_events_outlined), label: 'TOP'),
        ],
        onDestinationSelected: (v) => setState(() => page = [0, 8, 9, 4, 10][v]),
      ),
    );
  }

  Widget _content() => switch (page) {
        0 => _dashboard(),
        1 => _chronicles(),
        2 => _exploits(),
        3 => _army(),
        4 => _calculator(),
        5 => _academy(),
        6 => _search(),
        7 => _report(),
        8 => _factions(),
        9 => _cities(),
        10 => _rankings(),
        11 => _unitAtlas(),
        _ => _mechanics(),
      };

  Widget _scroll(List<Widget> children) => ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 22),
        children: children,
      );

  Widget _title(String t, {String? sub}) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(t, style: const TextStyle(color: gold, fontSize: 23, fontWeight: FontWeight.bold)),
          if (sub != null) Padding(padding: const EdgeInsets.only(top: 7), child: Text(sub, style: const TextStyle(color: muted))),
        ]),
      );

  Widget _tile(String title, String subtitle, IconData icon, VoidCallback action) =>
      Card(child: ListTile(
        onTap: action,
        leading: Icon(icon, color: gold, size: 30),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(subtitle, maxLines: 2, overflow: TextOverflow.ellipsis),
        trailing: const Icon(Icons.chevron_right, color: muted),
      ));

  Widget _dashboard() {
    final fs = rows(report['factions']);
    final units = rows(report['units']);
    return _scroll([
      ClipRRect(borderRadius: BorderRadius.circular(15), child: Image.asset('assets/codex_banner.png', fit: BoxFit.cover, height: 138)),
      _title('Wielkie kompendium Medieval II', sub: 'Frakcje, miasta, wojsko, rankingi, sekrety i kalkulatory — offline.'),
      _tile('Atlas 22 frakcji', 'Ilustrowane karty, mocne strony, taktyki i strategie', Icons.flag, () => setState(() => page = 8)),
      _tile('Atlas 24 miast', 'Gospodarka, strategiczne położenie i ranking lokalizacji', Icons.location_city, () => setState(() => page = 9)),
      _tile('Rankingi frakcji', 'Wojsko, gospodarka, łatwość startu, mobilność', Icons.emoji_events, () => setState(() => page = 10)),
      _tile('Atlas jednostek z raportu', 'Pełne statystyki po imporcie raportu Windows', Icons.military_tech, () => setState(() => page = 11)),
      _tile('Wielka Księga Mechanik', '32 praktyczne artykuły: gospodarka, bitwy, religia, kampania', Icons.menu_book, () => setState(() => page = 12)),
      _tile('Kalkulator AI: mam 30 000 fl.', 'Automatyczna propozycja prezentu i żądanego trybutu', Icons.calculate, () => setState(() => page = 4)),
      Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('AKTYWNY RAPORT', style: TextStyle(color: gold, fontWeight: FontWeight.bold)),
          const SizedBox(height: 7),
          Text(text(report['mod']), style: const TextStyle(fontSize: 18)),
          const SizedBox(height: 6),
          Text('${units.length} jednostek   •   ${fs.length} frakcji', style: const TextStyle(color: muted)),
          const SizedBox(height: 12),
          FilledButton.icon(onPressed: _import, icon: const Icon(Icons.file_open), label: const Text('Importuj raport z Windows')),
          const SizedBox(height: 7),
          const Text('Raport startowy to DEMO, nie dokładne dane Vanilla. Wczytaj własny plik JSON.', style: TextStyle(color: muted, fontSize: 12)),
        ],
      ))),
      _tile('Kroniki kampanii', 'Mongołowie, Timurydzi, dżuma, proch', Icons.event, () => setState(() => page = 1)),
      _tile('Encyklopedia exploitów', '${rows(knowledge['exploits']).length} opisów i instrukcji testowania', Icons.auto_stories, () => setState(() => page = 2)),
      _tile('Kreator armii', '20 slotów; koszty rekrutacji i utrzymania z EDU', Icons.shield, () => setState(() => page = 3)),
      _tile('Kalkulator trybutu', 'Oblicz nominalne płatności — bez obietnic AI', Icons.calculate, () => setState(() => page = 4)),
      _tile('Akademia', '${rows(knowledge['lessons']).length} lekcji i porad', Icons.school, () => setState(() => page = 5)),
      const SizedBox(height: 16),
      const Text('Wykonane przez Kruchyx • v0.9.6', textAlign: TextAlign.center, style: TextStyle(color: muted)),
    ]);
  }

  Widget _chronicles() {
    final events = rows(report['events']).isNotEmpty ? rows(report['events']) : rows(knowledge['events']);
    events.sort((a, b) => number(a['turn_from']).compareTo(number(b['turn_from'])));
    return _scroll([
      _title('Kroniki kampanii', sub: 'Ostrzeżenie o hordzie nie oznacza dokładnej tury pojawienia się armii.'),
      Card(child: Padding(padding: const EdgeInsets.all(15), child: Column(children: [
        Text('Aktualna tura: $turn', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: gold)),
        Slider(min: 1, max: 220, divisions: 219, value: turn.toDouble(), label: '$turn', onChanged: (v) => setState(() => turn = v.round())),
        const Text('Domyślne 2 lata na turę. Mody mogą używać innej skali.', style: TextStyle(fontSize: 12, color: muted)),
      ]))),
      for (final e in events)
        Card(child: ExpansionTile(
          leading: Icon(turn < number(e['turn_from']) ? Icons.schedule : Icons.history, color: gold),
          title: Text(text(e['title'])),
          subtitle: Text('Tury ${e['turn_from']}–${e['turn_to']}  •  ${turn < number(e['turn_from']) ? "za ${number(e['turn_from']) - turn}–${number(e['turn_to']) - turn} tur" : turn <= number(e['turn_to']) ? "okno wydarzenia" : "miniony przedział"}'),
          childrenPadding: const EdgeInsets.fromLTRB(18, 0, 18, 16),
          expandedCrossAxisAlignment: CrossAxisAlignment.start,
          children: [Text(text(e['after'])), const SizedBox(height: 10), Text('Rada: ${text(e['advice'])}'),
            const SizedBox(height: 6), Text('Typ danych: ${text(e['confidence'])}', style: const TextStyle(color: muted, fontSize: 12))],
        )),
      const SizedBox(height: 10),
      Text('Źródło: ${text(report['events_source'])}', style: const TextStyle(fontSize: 12, color: muted)),
    ]);
  }

  Widget _exploits() {
    final all = rows(knowledge['exploits']);
    final filtered = all.where((e) => ('${e['title']} ${e['category']} ${e['short']}').toLowerCase().contains(search.toLowerCase())).toList();
    return _scroll([
      _title('Księga exploitów', sub: 'Testuj tylko na osobnych zapisach. Wersje i mody mogą się różnić.'),
      TextField(decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Szukaj exploitu'),
        onChanged: (v) => setState(() => search = v)),
      const SizedBox(height: 12),
      for (final e in filtered)
        Card(child: ExpansionTile(
          title: Text(text(e['title'])),
          subtitle: Text('${e['category']}  •  ${e['confidence']}\n${e['short']}'),
          childrenPadding: const EdgeInsets.fromLTRB(18, 0, 18, 16),
          expandedCrossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (var i = 0; i < rowsToStrings(e['steps']).length; i++)
              Padding(padding: const EdgeInsets.only(bottom: 7), child: Text('${i + 1}. ${rowsToStrings(e['steps'])[i]}')),
            const Divider(),
            Text('Ograniczenia: ${e['limits']}', style: const TextStyle(color: muted)),
            const SizedBox(height: 7),
            SelectableText('Źródło: ${e['source']}', style: const TextStyle(fontSize: 12, color: gold)),
          ],
        )),
    ]);
  }

  List<String> rowsToStrings(dynamic v) => v is List ? v.map((e) => text(e)).toList() : [];

  Widget _army() {
    final units = rows(report['units']);
    final fs = rows(report['factions']).map((e) => text(e['name'])).where((e) => e.isNotEmpty).toList();
    final active = fs.contains(faction) ? faction : (fs.isEmpty ? '' : fs.first);
    final available = units.where((u) => (u['owners'] is List && (u['owners'] as List).contains(active))
              && text(u['role']) != 'Okręty'
              && text(u['name']).toLowerCase().contains(unitFilter.toLowerCase())).toList()
      ..sort((a, b) => text(a['name']).compareTo(text(b['name'])));
    final count = army.values.fold<int>(0, (a, b) => a + b);
    var price = 0;
    var upkeep = 0;
    for (final u in units) {
      final n = army[text(u['name'])] ?? 0;
      price += n * number(u['cost']);
      upkeep += n * number(u['upkeep']);
    }
    return _scroll([
      if (report['sample']==true) const Card(child:Padding(padding:EdgeInsets.all(12),child:Text('TRYB DEMO: jednostki i koszty są przykładowe. Importuj prawdziwy raport Windows, aby planować realne armie.',style:TextStyle(color:gold)))),
      _title('Kreator armii', sub: 'Do 20 slotów. Ceny z raportu EDU lub UMOWNE dane demo; bez dynamicznych premii i bez analizy budynków.'),
      if (fs.isEmpty) const Card(child: Padding(padding: EdgeInsets.all(16), child: Text('W raporcie nie ma frakcji. Importuj raport Windows.'))),
      if (fs.isNotEmpty) DropdownButtonFormField<String>(
        key: ValueKey(active), value: active,
        decoration: const InputDecoration(labelText: 'Frakcja'),
        items: fs.map((f) => DropdownMenuItem(value: f, child: Text(f))).toList(),
        onChanged: (v) { if (v != null) setState(() { faction = v; army.clear(); }); },
      ),
      const SizedBox(height: 12),
      Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('$count/20 slotów', style: const TextStyle(color: gold, fontSize: 21, fontWeight: FontWeight.bold)),
        Text('Rekrutacja: ${fmt(price)} fl.\nUtrzymanie: ${fmt(upkeep)} fl./tura'),
        const SizedBox(height: 9),
        for (final entry in army.entries.where((e) => e.value > 0))
          Padding(padding: const EdgeInsets.symmetric(vertical: 3), child: Row(children: [
            Expanded(child: Text('${entry.value}× ${entry.key}', maxLines: 2)),
            IconButton(tooltip: 'Usuń oddział', onPressed: () => setState(() {
              final old = army[entry.key] ?? 0;
              if (old <= 1) { army.remove(entry.key); } else { army[entry.key] = old - 1; }
            }), icon: const Icon(Icons.remove_circle_outline)),
          ])),
        if (army.isNotEmpty)
          OutlinedButton.icon(onPressed: () {
            final result = 'Kruchyx — armia $active\n${army.entries.map((e) => "${e.value}× ${e.key}").join("\n")}\nRekrutacja: $price\nUtrzymanie: $upkeep';
            Clipboard.setData(ClipboardData(text: result));
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Plan armii skopiowany.')));
          }, icon: const Icon(Icons.copy), label: const Text('Kopiuj plan')),
      ]))),
      TextField(controller: filterController,
        decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Filtruj jednostki'),
        onChanged: (v) => setState(() => unitFilter = v)),
      const SizedBox(height: 8),
      Text('Wyświetlono ${available.length > 120 ? 120 : available.length} z ${available.length} jednostek', style: const TextStyle(color: muted)),
      for (final u in available.take(120))
        Card(child: ListTile(
          title: Text(text(u['name']), maxLines: 2),
          subtitle: Text('${u['role']} • koszt ${fmt(number(u['cost']))} • utrzymanie ${fmt(number(u['upkeep']))}'),
          trailing: IconButton(tooltip: 'Dodaj oddział', icon: Icon(Icons.add_circle, color: count < 20 ? gold : muted),
            onPressed: count >= 20 ? null : () => setState(() => army.update(text(u['name']), (v) => v + 1, ifAbsent: () => 1))),
        )),
    ]);
  }

  Widget _calculator() {
    final amount = int.tryParse(treasuryController.text.replaceAll(' ', '')) ?? 0;
    final plan = suggestTributeOffer(amount, preset: diplomacyPreset, rejections: rejectedSteps);
    final treasury = plan['treasury']!;
    final gift = plan['gift']!;
    final requested = plan['request']!;
    final retained = plan['reserve']!;
    final initial = suggestTributeOffer(amount, preset: diplomacyPreset)['request']!;
    final payback = requested > 0 ? (gift / requested).ceil() : 0;
    return _scroll([
      _title('Kalkulator żądań od AI', sub: 'Wpisz swój skarbiec. Kruchyx proponuje prezent dla AI i wysokość trybutu do przetestowania.'),
      Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('ILE MASZ FLORENÓW?', style: TextStyle(color: gold, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        TextField(controller: treasuryController, keyboardType: TextInputType.number, decoration: const InputDecoration(prefixIcon: Icon(Icons.savings), labelText: 'Twój skarbiec (np. 30000)'), onChanged: (_) => setState(() { rejectedSteps = 0; })),
        const SizedBox(height: 14),
        Wrap(spacing: 8, runSpacing: 6, children: [
          ChoiceChip(label: const Text('Ostrożny'), selected: diplomacyPreset == 'safe', onSelected: (_) => setState(() { diplomacyPreset='safe'; rejectedSteps=0; })),
          ChoiceChip(label: const Text('Zrównoważony'), selected: diplomacyPreset == 'balanced', onSelected: (_) => setState(() { diplomacyPreset='balanced'; rejectedSteps=0; })),
          ChoiceChip(label: const Text('Agresywny'), selected: diplomacyPreset == 'aggressive', onSelected: (_) => setState(() { diplomacyPreset='aggressive'; rejectedSteps=0; })),
        ]),
        const SizedBox(height: 12),
        Text('Do testowej oferty przeznaczamy ${diplomacyPreset == 'safe' ? '20%' : diplomacyPreset == 'aggressive' ? '50%' : 'około 33%'} twojego skarbca.',style:const TextStyle(color:muted)),
      ]))),
      Card(color: const Color(0xFF302B20), child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('SUGEROWANA PROPOZYCJA',style:TextStyle(color:gold,fontWeight:FontWeight.bold)),
        const SizedBox(height: 14),
        const Text('DAJ AI JEDNORAZOWO',style:TextStyle(color:muted,fontSize:12)),
        Text('${fmt(gift)} fl.',style:const TextStyle(color:ink,fontSize:28,fontWeight:FontWeight.bold)),
        const Divider(),
        const Text('ZAŻĄDAJ OD AI / TURĘ',style:TextStyle(color:muted,fontSize:12)),
        Text('${fmt(requested)} fl.',style:const TextStyle(color:gold,fontSize:30,fontWeight:FontWeight.bold)),
        const SizedBox(height: 8),
        Text('Zostanie u ciebie: ${fmt(retained)} fl.\nTeoretyczny zwrot: ${requested > 0 ? '$payback wpłat' : 'brak'}\nDługość żądania w teście: 99 999 999 tur',style: const TextStyle(height:1.6)),
        const SizedBox(height: 12),
        FilledButton.icon(onPressed: () {
          Clipboard.setData(ClipboardData(text:'Kruchyx v0.9.6 — propozycja eksperymentalna\nSkarbiec: ${fmt(treasury)} fl.\nDaj AI jednorazowo: ${fmt(gift)} fl.\nZażądaj od AI: ${fmt(requested)} fl./turę\nLiczba tur: 99999999\nPozostanie: ${fmt(retained)} fl.\nBrak gwarancji akceptacji AI.'));
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content:Text('Propozycja skopiowana.')));
        },icon:const Icon(Icons.copy),label:const Text('Kopiuj ofertę')),
        const SizedBox(height: 8),
        OutlinedButton.icon(onPressed: initial <= 0 || rejectedSteps >= 9 ? null : () => setState(() => rejectedSteps++),icon:const Icon(Icons.trending_down),label:const Text('AI odrzuciło — obniż żądanie o ~10%')),
        if (rejectedSteps > 0) Text('Wariant próbny ${rejectedSteps+1}; zmiana dotyczy tylko kalkulatora.',style:const TextStyle(color:muted,fontSize:12)),
      ]))),
      const Padding(padding:EdgeInsets.symmetric(vertical:10),child:Text('Uwaga: stawka 40% wartości prezentu i obniżki to przyjęta heurystyka do eksperymentów. Nie znamy algorytmu decyzji AI. Umowa może zostać odrzucona, a płatności mogą nie nadejść. Testuj na osobnym zapisie.',style:TextStyle(color:muted,fontSize:12))),
      Card(child: ExpansionTile(title:const Text('Zaawansowany: własne kwoty'),subtitle:const Text('Ręczne liczenie z poprzedniej wersji'),childrenPadding:const EdgeInsets.all(16),children: [
        TextField(controller: giftController,keyboardType:TextInputType.number,decoration:const InputDecoration(labelText:'Własny prezent AI'),onChanged:(_)=>setState((){})),
        const SizedBox(height:9),
        TextField(controller: tributeController,keyboardType:TextInputType.number,decoration:const InputDecoration(labelText:'Własny trybut / turę'),onChanged:(_)=>setState((){})),
        const SizedBox(height:9),
        TextField(controller:turnsController,keyboardType:TextInputType.number,decoration:const InputDecoration(labelText:'Liczba tur'),onChanged:(_)=>setState((){})),
        const SizedBox(height:12),
        Builder(builder:(context){
          final g=int.tryParse(giftController.text)??0; final t=int.tryParse(tributeController.text)??0;final n=int.tryParse(turnsController.text)??0;
          return Text(g>=0&&t>=0&&n>=0?'Nominalny bilans po $n wpłatach: ${fmt(t*n-g)} fl.':'Wprowadź nieujemne kwoty.');
        }),
      ])),
    ]);
  }

  Widget _academy() => _scroll([
    _title('Akademia Medieval II', sub: 'Podstawy bez oddzielnych trybów gracza.'),
    for (final e in rows(knowledge['lessons']))
      Card(child: ExpansionTile(title: Text(text(e['title'])), childrenPadding: const EdgeInsets.all(16), children: [Text(text(e['body']))])),
  ]);

  Widget _search() {
    final contents = <Map<String, String>>[];
    for (final e in rows(knowledge['events'])) {contents.add({'title': text(e['title']), 'body': '${e['after']} ${e['advice']}'});}
    for (final e in rows(knowledge['exploits'])) {contents.add({'title': text(e['title']), 'body': '${e['short']} ${e['limits']}'});}
    for (final e in rows(knowledge['lessons'])) {contents.add({'title': text(e['title']), 'body': text(e['body'])});}
    for (final e in rows(mechanics['articles'])) {contents.add({'title': text(e['title']), 'body': '${e['body']} ${e['tip']}'});}
    for (final e in rows(codex['factions'])) {contents.add({'title': text(e['name']), 'body': '${e['region']} ${e['strength']} ${e['strategy']}'});}
    for (final e in rows(codex['cities'])) {contents.add({'title': text(e['name']), 'body': '${e['region']} ${e['description']}'});}
    final matches = contents.where((e) => '${e['title']} ${e['body']}'.toLowerCase().contains(search.toLowerCase())).toList();
    return _scroll([
      _title('Szukaj w Kruchyx'),
      TextField(controller: searchController, decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Np. Mongołowie, dyplomacja, zamek'), onChanged: (v) => setState(() => search = v)),
      const SizedBox(height: 12),
      for (final entry in matches)
        Card(child: ListTile(title: Text(entry['title']!), subtitle: Text(entry['body']!, maxLines: 3, overflow: TextOverflow.ellipsis))),
    ]);
  }

  Widget _report() => _scroll([
    _title('Raport moda', sub: 'Wczytywany lokalnie; aplikacja nie wysyła plików do serwera.'),
    _tile('Importuj plik JSON', 'Plik wyeksportowany przez Kruchyx Windows v0.9.6 (format v1)', Icons.file_open, _import),
    Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text('Mod: ${text(report['mod'])}', style: const TextStyle(color: gold, fontWeight: FontWeight.bold)),
      const SizedBox(height: 10),
      Text('Jednostki: ${rows(report['units']).length}\nFrakcje: ${rows(report['factions']).length}\nŹródło kalendarza: ${text(report['events_source'])}\nWygenerowano: ${text(report['created_at'])}'),
      const SizedBox(height: 12),
      Text(text(report['disclaimer']), style: const TextStyle(color: muted)),
    ]))),
    if (report['sample']==true) const Text('DEMO: brak wiarygodnego rankingu EDU. Zaimportuj dane modu.',style:TextStyle(color:gold)),
    if (report['sample']!=true) _title('Najwyżej ocenione frakcje (indeks EDU)'),
    if (report['sample']!=true) for (final e in (rows(report['factions'])..sort((a, b) => (number(b['score'])).compareTo(number(a['score'])))).take(20))
      Card(child: ListTile(title: Text(text(e['name'])), subtitle: Text('Indeks jednostek: ${e['score']} • liczba jednostek: ${e['unit_count']}'))),
  ]);

  Widget _factionBadge(Map<String,dynamic> f, {double size=66}) =>
    Image.asset(text(f['art']),width:size,height:size,fit:BoxFit.contain,
      errorBuilder: (_,__,___) => const Icon(Icons.shield_outlined, color: gold, size: 42));

  Widget _factions() {
    final factions = rows(codex['factions']).where((f) =>
      ('${f['name']} ${f['region']} ${f['strength']}').toLowerCase().contains(factionQuery.toLowerCase())).toList();
    return _scroll([
      _title('Atlas 22 frakcji',sub:'Autorskie emblematy ilustracyjne. Profile dotyczą ogólnie Vanilla, nie automatycznie każdego moda.'),
      TextField(decoration:const InputDecoration(prefixIcon:Icon(Icons.search),labelText:'Szukaj frakcji'),onChanged:(v)=>setState(()=>factionQuery=v)),
      const SizedBox(height:9),
      Text('${factions.length} frakcji • dotknij, aby otworzyć pełny profil',style:const TextStyle(color:muted)),
      for (final f in factions) Card(child: ListTile(
        contentPadding:const EdgeInsets.symmetric(horizontal:12,vertical:7),
        leading:_factionBadge(f),
        title:Text(text(f['name']),style:const TextStyle(fontWeight:FontWeight.bold)),
        subtitle:Text('${f['region']} • ${f['religion']}\n${f['strength']}',maxLines:3,overflow:TextOverflow.ellipsis),
        isThreeLine:true,
        trailing: const Icon(Icons.chevron_right,color:gold),
        onTap:()=>_showFaction(f),
      )),
      const Text('Uwaga: frakcje specjalne mogą być niegrywalne w zwykłym wyborze kampanii.',style:TextStyle(color:muted,fontSize:12)),
    ]);
  }

  void _showFaction(Map<String,dynamic> f) {
    final scores=Map<String,dynamic>.from(f['scores'] as Map);
    showModalBottomSheet(context:context,isScrollControlled:true,showDragHandle:true,
      backgroundColor:panel,builder:(context)=>SafeArea(child:FractionallySizedBox(heightFactor:0.8,
        child:ListView(padding:const EdgeInsets.all(20),children:[
          Center(child:_factionBadge(f,size:130)),
          const SizedBox(height:10),
          Text(text(f['name']),textAlign:TextAlign.center,style:const TextStyle(color:gold,fontSize:24,fontWeight:FontWeight.bold)),
          const SizedBox(height:4),
          Text('${f['region']} • ${f['religion']}',textAlign:TextAlign.center,style:const TextStyle(color:muted)),
          if(f['special']==true) const Padding(padding:EdgeInsets.symmetric(vertical:10),child:Text('FRAKCJA SPECJALNA — zasady kampanii odbiegają od zwykłych.',style:TextStyle(color:gold))),
          const Divider(),
          const Text('MOCNE STRONY',style:TextStyle(color:gold,fontWeight:FontWeight.bold)),
          const SizedBox(height:8),Text(text(f['strength'])),
          const SizedBox(height:16),const Text('STRATEGIA',style:TextStyle(color:gold,fontWeight:FontWeight.bold)),
          const SizedBox(height:8),Text(text(f['strategy'])),
          const SizedBox(height:16),const Text('OCENY REDAKCYJNE',style:TextStyle(color:gold,fontWeight:FontWeight.bold)),
          const SizedBox(height:8),
          for(final key in ['wojsko','gospodarka','start','mobilnosc'])
            Padding(padding:const EdgeInsets.symmetric(vertical:4),child:Row(children:[
              SizedBox(width:112,child:Text(key,style:const TextStyle(color:muted))),
              Expanded(child:LinearProgressIndicator(value:number(scores[key])/5,backgroundColor:base,color:gold,minHeight:7)),
              const SizedBox(width:10),Text('${scores[key]}/5'),
            ])),
          const SizedBox(height:15),
          const Text('Oceny 1–5 są poglądowymi wskazówkami strategicznymi, nie wynikają z rzeczywistych statystyk EDU. Sprawdzaj zmiany w danym modzie.',style:TextStyle(color:muted,fontSize:12)),
        ]))));
  }

  Widget _cities() {
    final cityList=rows(codex['cities']).where((c)=>
       ('${c['name']} ${c['region']} ${c['description']}').toLowerCase().contains(cityQuery.toLowerCase())).toList();
    cityList.sort((a,b){
      final v=number(b[citySort]).compareTo(number(a[citySort]));
      return v!=0?v:text(a['name']).compareTo(text(b['name']));
    });
    return _scroll([
      _title('Atlas 24 ważnych miast',sub:'Handel, geografia, obrona i znaczenie strategiczne. Bez zmyślonych dochodów.'),
      TextField(decoration:const InputDecoration(prefixIcon:Icon(Icons.search),labelText:'Szukaj miasta lub regionu'),onChanged:(v)=>setState(()=>cityQuery=v)),
      const SizedBox(height:10),
      Wrap(spacing:8,children:[
        ChoiceChip(label:const Text('TOP handel'),selected:citySort=='trade_index',onSelected:(_)=>setState(()=>citySort='trade_index')),
        ChoiceChip(label:const Text('TOP strategiczne'),selected:citySort=='strategic_index',onSelected:(_)=>setState(()=>citySort='strategic_index')),
      ]),
      const SizedBox(height:8),
      for(final city in cityList) Card(child:ExpansionTile(
        leading:const CircleAvatar(backgroundColor:Color(0xFF3E3A2D),child:Icon(Icons.location_city,color:gold)),
        title:Text(text(city['name']),style:const TextStyle(fontWeight:FontWeight.w600)),
        subtitle:Text('${city['region']} • handel ${city['trade_index']}/5 • strategia ${city['strategic_index']}/5'),
        childrenPadding:const EdgeInsets.fromLTRB(16,0,16,16),
        expandedCrossAxisAlignment:CrossAxisAlignment.start,
        children:[Text(text(city['description'])),const SizedBox(height:10),Text('Wskazówka: ${city['focus']}',style:const TextStyle(color:gold)),
          const SizedBox(height:7),Text(text(city['note']),style:const TextStyle(color:muted,fontSize:12))],
      )),
      const Text('Atlas ma charakter strategiczno-geograficzny. Konkretne osady w danej kampanii weryfikuj w plikach moda.',style:TextStyle(color:muted,fontSize:12)),
    ]);
  }

  Widget _rankings() {
    final values=rows(codex['factions']).where((f)=>showSpecial||f['special']!=true).toList();
    values.sort((a,b){
      final aScore=number((a['scores'] as Map)[rankingMetric]);
      final bScore=number((b['scores'] as Map)[rankingMetric]);
      final compare=bScore.compareTo(aScore);
      return compare!=0?compare:text(a['name']).compareTo(text(b['name']));
    });
    return _scroll([
      _title('Rankingi frakcji',sub:'Porównania orientacyjne na podstawie ocen redakcyjnych 1–5, a nie symulacji walk.'),
      Wrap(spacing:7,runSpacing:6,children:[
        for(final choice in [('wojsko','Wojsko'),('gospodarka','Gospodarka'),('start','Łatwy start'),('mobilnosc','Mobilność')])
          ChoiceChip(label:Text(choice.$2),selected:rankingMetric==choice.$1,onSelected:(_)=>setState(()=>rankingMetric=choice.$1)),
      ]),
      SwitchListTile(title:const Text('Uwzględnij frakcje specjalne'),value:showSpecial,onChanged:(v)=>setState(()=>showSpecial=v)),
      for(var i=0;i<values.length;i++) Card(child:ListTile(
        leading:SizedBox(width:77,child:Row(children:[Text('${i+1}',style:const TextStyle(color:gold,fontWeight:FontWeight.bold)),const SizedBox(width:3),_factionBadge(values[i],size:43)])),
        title:Text(text(values[i]['name'])),
        subtitle:Text(text(values[i]['strength']),maxLines:2,overflow:TextOverflow.ellipsis),
        trailing:Text('${(values[i]['scores'] as Map)[rankingMetric]}/5',style:const TextStyle(color:gold,fontSize:17,fontWeight:FontWeight.bold)),
        onTap:()=>_showFaction(values[i]),
      )),
      const Padding(padding:EdgeInsets.all(8),child:Text('Remisy uporządkowane alfabetycznie. Interpretuj jako inspirację do gry, a nie bezsporną hierarchię; mody potrafią istotnie zmienić balans.',style:TextStyle(color:muted,fontSize:12))),
    ]);
  }

  Widget _unitAtlas() {
    final units=rows(report['units']);
    final shown=units.where((u)=>'${u['name']} ${u['role']} ${u['owners']}'.toLowerCase().contains(unitFilter.toLowerCase())).toList();
    return _scroll([
      _title('Atlas jednostek',sub:'Statystyki z importowanego raportu EDU. Dane startowe są tylko demonstracyjne.'),
      _tile('Importuj pełny raport z Windows','Odczytaj własne jednostki, koszty, frakcje i role',Icons.file_open,_import),
      TextField(decoration:const InputDecoration(prefixIcon:Icon(Icons.search),labelText:'Szukaj jednostki'),onChanged:(v)=>setState(()=>unitFilter=v)),
      const SizedBox(height:8),
      Text('Znaleziono ${shown.length} jednostek • źródło: ${report['mod']}',style:const TextStyle(color:muted,fontSize:12)),
      for(final u in shown.take(150)) Card(child:ExpansionTile(
        leading:const Icon(Icons.shield_outlined,color:gold),
        title:Text(text(u['name'])),subtitle:Text('${u['role']} • ${fmt(number(u['cost']))} fl.'),
        childrenPadding:const EdgeInsets.fromLTRB(16,0,16,16),
        children:[Text('Utrzymanie: ${fmt(number(u['upkeep']))} fl./turę'),
          Text('Frakcje: ${u['owners'] is List ? (u['owners'] as List).join(', ') : 'brak danych'}'),
          Text('Statystyki: ${u['attack'] ?? '—'} / ${u['defence'] ?? '—'} (jeśli dostępne w raporcie)'),
          const SizedBox(height:5),const Text('Dostępność do rekrutacji zależy także od budynków i warunków kampanii.',style:TextStyle(color:muted,fontSize:12))],
      )),
    ]);
  }


  Widget _mechanics() {
    final entries=rows(mechanics['articles']).where((e)=>
      ('${e['category']} ${e['title']} ${e['body']} ${e['tip']}').toLowerCase().contains(mechanicQuery.toLowerCase())).toList();
    return _scroll([
      _title('Wielka Księga Mechanik',sub:'32 praktyczne hasła • wersja offline • rozwijane artykuły z poradami.'),
      TextField(decoration:const InputDecoration(prefixIcon:Icon(Icons.search),labelText:'Szukaj mechaniki, np. papież, morale'),onChanged:(v)=>setState(()=>mechanicQuery=v)),
      const SizedBox(height:10),
      for(final e in entries) Card(child:ExpansionTile(
        leading:const Icon(Icons.auto_stories,color:gold),
        title:Text(text(e['title'])),
        subtitle:Text(text(e['category']),style:const TextStyle(color:muted)),
        childrenPadding:const EdgeInsets.fromLTRB(18,4,18,17),
        expandedCrossAxisAlignment:CrossAxisAlignment.start,
        children:[Text(text(e['body'])),const SizedBox(height:12),Text(text(e['tip']),style:const TextStyle(color:gold)),
          const SizedBox(height:8),Text(text(e['status']),style:const TextStyle(color:muted,fontSize:12))],
      )),
    ]);
  }

}
