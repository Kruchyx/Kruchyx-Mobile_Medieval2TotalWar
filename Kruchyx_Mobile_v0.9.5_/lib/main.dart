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

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final a = jsonDecode(await rootBundle.loadString('assets/knowledge_v095.json')) as Map;
      final b = jsonDecode(await rootBundle.loadString('assets/demo_report.json')) as Map;
      final loaded = Map<String, dynamic>.from(b);
      if (loaded['schema'] != 'kruchyx-companion-v1') throw const FormatException('Nieobsługiwany format danych');
      if (!mounted) return;
      setState(() {
        knowledge = Map<String, dynamic>.from(a);
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
    final pages = ['Centrum dowodzenia', 'Kroniki', 'Exploity', 'Kreator armii', 'Kalkulator', 'Akademia', 'Szukaj', 'Raport'];
    return Scaffold(
      appBar: AppBar(
        title: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('KRUCHYX', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 2, color: gold, fontSize: 18)),
          Text('${pages[page]}  •  v0.9.5', style: const TextStyle(color: muted, fontSize: 12)),
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
              leading: Icon([Icons.home, Icons.event, Icons.auto_stories, Icons.shield, Icons.calculate, Icons.school, Icons.search, Icons.import_export][i]),
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
        selectedIndex: page <= 3 ? page : 0,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Start'),
          NavigationDestination(icon: Icon(Icons.event), label: 'Kroniki'),
          NavigationDestination(icon: Icon(Icons.auto_stories), label: 'Exploity'),
          NavigationDestination(icon: Icon(Icons.shield), label: 'Armia'),
        ],
        onDestinationSelected: (v) => setState(() => page = v),
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
        _ => _report(),
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
      _title('Twoje centrum dowodzenia', sub: 'Jedna aplikacja mobilna na Androida i iOS. Działa offline.'),
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
      const Text('Wykonane przez Kruchyx • v0.9.5', textAlign: TextAlign.center, style: TextStyle(color: muted)),
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
          isThreeLine: true,
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
      _title('Kreator armii', sub: 'Do 20 slotów. Ceny z EDU, bez dynamicznych premii i bez analizy dostępności budynków.'),
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
    final gift = int.tryParse(giftController.text) ?? 0;
    final per = int.tryParse(tributeController.text) ?? 0;
    final turns = int.tryParse(turnsController.text) ?? 0;
    final valid = gift >= 0 && per >= 0 && turns >= 0 && gift <= 2147483647 && per <= 2147483647 && turns <= 99999999;
    return _scroll([
      _title('Kalkulator trybutu', sub: 'Teoretyczne obliczenia, nie prognoza akceptacji AI ani gwarancja płatności.'),
      TextField(controller: giftController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Jednorazowy prezent (fl.)'), onChanged: (_) => setState(() {})),
      const SizedBox(height: 12),
      TextField(controller: tributeController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Trybut żądany na turę (fl.)'), onChanged: (_) => setState(() {})),
      const SizedBox(height: 12),
      TextField(controller: turnsController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Liczba tur'), onChanged: (_) => setState(() {})),
      const SizedBox(height: 15),
      Card(child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(valid ? 'Netto po 1 turze: ${fmt(per - gift)} fl.' : 'Nieprawidłowe kwoty', style: const TextStyle(fontSize: 17, color: gold, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Text(valid ? 'Suma teoretyczna: ${fmt(per * turns - gift)} fl.' : 'Wprowadź nieujemne liczby w bezpiecznym zakresie.'),
      ]))),
      const SizedBox(height: 8),
      const Text('Ważne: AI może odmówić, zerwać umowę lub nie mieć środków. To matematyczny scenariusz, nie cheat.', style: TextStyle(color: muted)),
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
    _tile('Importuj plik JSON', 'Plik wyeksportowany przez Kruchyx Windows v0.9.5', Icons.file_open, _import),
    Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text('Mod: ${text(report['mod'])}', style: const TextStyle(color: gold, fontWeight: FontWeight.bold)),
      const SizedBox(height: 10),
      Text('Jednostki: ${rows(report['units']).length}\nFrakcje: ${rows(report['factions']).length}\nŹródło kalendarza: ${text(report['events_source'])}\nWygenerowano: ${text(report['created_at'])}'),
      const SizedBox(height: 12),
      Text(text(report['disclaimer']), style: const TextStyle(color: muted)),
    ]))),
    _title('Najwyżej ocenione frakcje (indeks EDU)'),
    for (final e in (rows(report['factions'])..sort((a, b) => (number(b['score'])).compareTo(number(a['score'])))).take(20))
      Card(child: ListTile(title: Text(text(e['name'])), subtitle: Text('Indeks jednostek: ${e['score']} • liczba jednostek: ${e['unit_count']}'))),
  ]);
}
