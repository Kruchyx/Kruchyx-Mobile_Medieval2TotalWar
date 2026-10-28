"""Original bilingual beginner's guide for Medieval II. Offline and read-only.

Mechanics based on the Feral Interactive Medieval II manual and Steam's
original PC manual. Strategy is clearly marked as tips, not engine guarantees.
"""
from __future__ import annotations

SOURCES = [
    ('Official Medieval II manual · Feral Interactive', 'https://www.feralinteractive.com/en/manuals/medieval2/latest/steam/'),
    ('Original PC manual · Steam', 'https://steamcdn-a.akamaihd.net/steam/apps/4700/manuals/manual.pdf'),
    ('Medieval II console commands · Total War Center', 'https://wiki.twcenter.net/index.php?title=Medieval_II_cheats'),
    ('Campaign configuration reference · RTW-M2TW Editor', 'https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/main/docs/wiki/Campaign-rules-and-Add-ons.md'),
]

# Each entry: id, icon, titles {pl,en}, short summary, concrete numbered steps, traps.
LESSONS = [
 ('start','♛',('Pierwsza tura bez paniki','Your first turn without panic'),
  ('Co zrobić, zanim naciśniesz Koniec tury.','What to do before you press End Turn.'),
  [
   ('Otwórz zestawienie frakcji: sprawdź skarbiec, przewidywany bilans, wojsko i cele misji.','Open your faction overview: check treasury, projected balance, troops and missions.'),
   ('Otwórz każde miasto i zamek. Sprawdź porządek publiczny i to, czy rozpoczęto budowę.','Open every city and castle. Check public order and whether construction has started.'),
   ('Nie rekrutuj we wszystkich osadach jednocześnie: jednostki często pobierają koszt utrzymania co turę.','Do not recruit everywhere at once: most troops cost upkeep each turn.'),
   ('Wyślij dyplomatę z propozycją praw handlowych do bezpiecznego sąsiada.','Send a diplomat to a safe neighbor with a trade-rights proposal.'),
   ('Wybierz JEDEN sensowny cel ekspansji. Ustal, czy dysponujesz wojskiem i posiłkami.','Choose ONE realistic expansion target. Check your army and reinforcements.'),
   ('Przed końcem tury sprawdź bezczynne armie, kolejki, podatki i zagrożone granice.','Before ending the turn, review idle troops, queues, taxes and vulnerable borders.'),
  ],
  ('Nie wydawaj całego skarbca na żołnierzy w pierwszej turze.','Do not spend your whole treasury on troops on turn one.'),
  'manual'),
 ('economy','♜',('Ekonomia i zarabianie florenów','Economy and making florins'),
  ('Zarabiaj więcej, niż kosztują twoje armie.','Earn more than your armies cost.'),
  [
   ('Sprawdź bilans, nie tylko stan skarbca — 20 000 florenów przy stracie 3 000 na turę szybko zniknie.','Check your balance, not just treasury: 20,000 florins with a 3,000-per-turn loss disappears quickly.'),
   ('W miastach rozważ rynki, drogi, porty i farmy; rzeczywista opłacalność zależy od prowincji.','In cities, consider markets, roads, ports and farms; actual returns depend on the province.'),
   ('Drogi poprawiają handel i przyspieszają przemieszczanie armii oraz agentów.','Roads improve trade and movement for armies and agents.'),
   ('Porty pozwalają na handel morski, ale wymagają dostępu do wybrzeża.','Ports enable sea trade, but require coastal access.'),
   ('Kopalnie pomagają, jeśli region ma odpowiednie zasoby; na mapie szukaj złota i srebra.','Mines help where the province has suitable deposits; look for gold and silver.'),
   ('Podnoś podatki tylko wtedy, gdy porządek publiczny pozostaje bezpieczny.','Increase taxes only while public order remains safe.'),
   ('Zawrzyj prawa handlowe i nie trzymaj nadmiarowych garnizonów bez celu.','Sign trade rights and avoid maintaining excess garrisons without a purpose.'),
  ],
  ('Wartość „trade_value” surowca nie jest bezpośrednim dochodem na turę.','A resource’s trade_value is NOT direct income per turn.'),
  'manual'),
 ('build','⚒',('Co budować w miastach i zamkach','What to build in cities and castles'),
  ('Pierwszeństwo gospodarki albo rekrutacji zależy od roli osady.','Economic versus military priorities depend on the settlement’s role.'),
  [
   ('Miasto na bezpiecznych tyłach: rozważ handel, drogi, farmy i porządek publiczny.','Safe rear city: consider trade, roads, farms and public order.'),
   ('Miasto portowe: rozważ port, gdy handel morski może działać.','Coastal city: consider a port when sea trade can function.'),
   ('Miasto blisko wroga: popraw bezpieczeństwo i zachowaj pieniądze na garnizon.','Frontier city: secure defenses and reserve money for a garrison.'),
   ('Zamek: rozwijaj dostęp do oddziałów, które naprawdę zamierzasz rekrutować.','Castle: invest in the troop types you actually plan to recruit.'),
   ('Przed budową porównaj koszt, liczbę tur i korzyść z opisu budynku.','Before building, compare price, construction time and tooltip benefits.'),
   ('Nie każda gospodarcza budowla przynosi identyczny zwrot w każdym regionie.','Economic buildings do not yield identical returns in every province.'),
  ],
  ('Nie buduj drogich koszar w każdym zamku — stwórz kilka wyspecjalizowanych ośrodków rekrutacyjnych.','Do not build expensive barracks everywhere; use a few specialist recruitment centers.'),
  'manual'),
 ('settlements','⌂',('Porządek publiczny i rozwój miast','Public order and settlement growth'),
  ('Jak nie stracić świeżo zdobytego miasta.','How to avoid losing a newly conquered city.'),
  [
   ('Po podboju sprawdź porządek publiczny, religię, podatki i uszkodzone budynki.','After conquest, check public order, religion, taxes and damaged buildings.'),
   ('Przy niskim porządku obniż podatki i zostaw garnizon, zanim wyślesz armię dalej.','With low public order, lower taxes and keep a garrison before advancing.'),
   ('Gubernator z korzystnymi cechami może poprawić sytuację w osadzie.','A governor with suitable traits can improve settlement conditions.'),
   ('Kapłani pomagają w nawracaniu prowincji o innej religii.','Priests help convert a province with a different religion.'),
   ('Odróżniaj miasta nastawione na ludność i handel od silniej ufortyfikowanych zamków.','Distinguish population-and-trade-focused cities from better-defended castles.'),
  ],
  ('Wysokie podatki zwiększają przychód, ale obniżają porządek publiczny.','High taxes boost revenue but reduce public order.'),
  'manual'),
 ('army','⚔',('Budowanie armii i rekrutacja','Building and recruiting an army'),
  ('Zwycięża współpraca oddziałów, nie jedna najwyższa statystyka.','Unit cooperation matters more than one big stat.'),
  [
   ('Zbuduj linię piechoty, która utrzyma pozycję podczas ostrzału i szarż.','Build an infantry line that can hold through missile fire and charges.'),
   ('Dodaj jednostki strzeleckie do osłabiania przeciwnika przed zwarciem.','Add missile units to weaken enemies before contact.'),
   ('Kawalerię trzymaj na skrzydłach; wykorzystuj przestrzeń i moment szarży.','Keep cavalry on the flanks; exploit room and charge timing.'),
   ('W razie potrzeby dodaj włóczników lub pikinierów do ochrony przed jazdą.','Use spearmen or pikemen to protect against enemy horsemen where appropriate.'),
   ('Sprawdź morale, pancerz, przebijanie pancerza, koszt i utrzymanie jednostki.','Check morale, armor, armor-piercing, recruitment cost and upkeep.'),
   ('Uzupełniaj straty i ulepszaj uzbrojenie, gdy właściwe budynki pozwalają.','Retrain and upgrade equipment when the required buildings are present.'),
  ],
  ('Nie opieraj całej armii na jednym typie wojsk bez planu na jego kontry.','Avoid building an entire army around one unit type with no counterplay plan.'),
  'strategy'),
 ('offense','♞',('Ofensywa: jak wygrywać bitwy','Offense: how to win battles'),
  ('Prosty plan walki w otwartym polu.','A simple field-battle plan.'),
  [
   ('Obejrzyj teren przed rozpoczęciem: pagórki, las, rzeki i przeszkody.','Inspect terrain before engagement: hills, woods, rivers and obstacles.'),
   ('Nie biegnij całą armią od razu. Utrzymaj linię i obserwuj zmęczenie.','Do not sprint the whole army immediately. Keep formation and watch fatigue.'),
   ('Zwiąż przeciwnika piechotą frontem, a kawalerią uderz z boku lub tyłu.','Pin the enemy with infantry from the front, then strike its flank or rear with cavalry.'),
   ('Wycofaj kawalerię po kontakcie, jeśli sytuacja pozwala, i przygotuj następną szarżę.','Pull cavalry away after contact when feasible and set up another charge.'),
   ('Broń strzelecka działa lepiej z czystym polem widzenia i bez własnych żołnierzy przed lufami/łukami.','Missile troops work better with a clear line of sight and fewer friendlies blocking shots.'),
   ('Gdy wróg zaczyna uciekać, nie narażaj generała na samotny pościg.','When enemies rout, avoid putting your general at risk in a lone pursuit.'),
  ],
  ('Nie szarżuj ciężką jazdą czołowo w przygotowaną ścianę włóczni.','Do not charge heavy cavalry head-on into a prepared spear wall.'),
  'strategy'),
 ('defense','♜',('Obrona, zasadzki i oblężenia','Defense, ambushes and sieges'),
  ('Pozycja i morale bywają ważniejsze od liczebności.','Position and morale can matter more than numbers.'),
  [
   ('Na wzgórzu łatwiej utrzymać linię i kontrolować podejście przeciwnika.','Hills can help you maintain a line and control enemy approaches.'),
   ('Chroń strzelców piechotą; nie ustawiaj ich bez osłony przed kawalerią.','Screen missile troops with infantry; do not expose them to cavalry.'),
   ('W obronie murów trzymaj odwody w pobliżu punktów przełamania.','During wall defense, keep reserves near likely breaches.'),
   ('Podczas szturmu przygotuj drabiny, tarany lub sprzęt oblężniczy i rozważ kilka osi natarcia.','For an assault, bring ladders, rams or siege equipment and consider multiple approaches.'),
   ('Uważaj na ucieczkę oddziałów i efekt domina w morale.','Watch for routs and the resulting morale collapse.'),
  ],
  ('Nie stój całą armią pod ostrzałem wież i łuczników bez planu ataku.','Do not leave your entire army under tower and arrow fire without an assault plan.'),
  'strategy'),
 ('diplomacy','✉',('Dyplomacja i sojusze','Diplomacy and alliances'),
  ('Jak dobrać sojuszników i ograniczyć liczbę wrogów.','How to choose allies and avoid too many enemies.'),
  [
   ('Na początku szukaj praw handlowych z państwami, które nie są bezpośrednim celem ekspansji.','Start with trade rights from factions you do not intend to conquer immediately.'),
   ('Sojusz bywa użyteczny na spokojnej granicy, ale nie zakładaj, że AI zawsze go dotrzyma.','An alliance can secure a quiet border, but never assume the AI will always honor it.'),
   ('Unikaj rozpoczynania wielu wojen jednocześnie — masz ograniczoną liczbę armii i pieniędzy.','Avoid opening several wars at once; armies and money are limited.'),
   ('Sprawdzaj sąsiadów i wrogość religijną; państwa katolickie muszą też uważać na relacje z papiestwem.','Monitor neighbors and religious conflicts; Catholic factions must also mind papal relations.'),
   ('Prośby o dostęp wojskowy traktuj osobno od sojuszu: nie każdy przyjazny kraj otworzy swoje granice.','Treat military access separately from alliance: not every friendly faction will open its borders.'),
   ('Sojusz warto weryfikować co kilka tur, gdy zmieniają się wojny i sąsiedztwo.','Reassess alliances every few turns as wars and borders change.'),
  ],
  ('Nie polecaj „zawsze sojuszu z konkretną frakcją” bez informacji o aktualnych granicach i wojnach.','Do not assume a specific faction is always an ideal ally without current border and war data.'),
  'manual'),
 ('agents','♟',('Agenci, kapłani, szpiedzy i kupcy','Agents, priests, spies and merchants'),
  ('Małe postacie, duży wpływ na kampanię.','Small characters, big campaign effects.'),
  [
   ('Dyplomata otwiera handel, sojusze i negocjacje — wyślij go do państw neutralnych.','Diplomats unlock trade, alliances and negotiations — send them to neutral factions.'),
   ('Kupiec stojący na zasobie może przynosić dodatkowy dochód.','A merchant standing on a resource may generate additional income.'),
   ('Dochód kupca zależy między innymi od jego finansów, odległości, zasobu i praw handlowych.','Merchant income depends on finance skill, distance, resource and trade rights, among other things.'),
   ('Kapłan pomaga w konwersji religijnej oraz porządku na trudnych terenach.','A priest helps religious conversion and stability in difficult regions.'),
   ('Szpieg może badać siłę garnizonu; nie wysyłaj armii na ślepo przeciw murom.','A spy can scout garrisons; avoid blindly assaulting defended walls.'),
   ('Zabójca jest narzędziem ryzyka — oceniając szanse, pamiętaj o możliwej porażce.','Assassins are risky; assess chances and expect possible failure.'),
  ],
  ('Kupcy innych frakcji mogą próbować przejąć twoje aktywa handlowe.','Rival merchants can attempt to acquire your trade assets.'),
  'manual'),
 ('religion','✝',('Religia, papież i bunty','Religion, the Pope and rebellions'),
  ('Uważaj, by podbój nie skończył się powstaniem.','Keep conquests from ending in revolt.'),
  [
   ('Po zdobyciu miasta innej wiary sprawdzaj udział religii i porządek publiczny.','After conquering another faith’s city, monitor religion and public order.'),
   ('Rozważ świątynię i kapłana, jeśli mieszkańcy nie wyznają wiary twojej frakcji.','Consider a religious building and priest if locals follow a different faith.'),
   ('Władcy katoliccy powinni uważać na ekskomunikę i wezwania papieża.','Catholic rulers should watch for excommunication and papal demands.'),
   ('Nie zostawiaj zbyt dużej liczby niepewnych osad bez garnizonów.','Do not leave too many unstable settlements without garrisons.'),
  ],
  ('Święta wojna i krucjaty zależą od religii, wydarzeń i konkretnego moda.','Holy wars and crusades depend on religion, events and the particular mod.'),
  'manual'),
 ('navy','⚓',('Flota, porty i transport','Fleets, ports and transport'),
  ('Wojna morska i handlowe połączenia.','Naval warfare and trade links.'),
  [
   ('Porty zwiększają możliwości handlu i pozwalają budować flotę w regionach nadmorskich.','Ports improve sea trade and allow naval construction in coastal regions.'),
   ('Chroń morskie szlaki handlowe; blokady mogą obniżyć dochód.','Protect trade routes; naval blockades may reduce income.'),
   ('Nie wysyłaj ważnej armii transportowej bez sprawdzenia wrogich flot.','Do not send an important transport army without checking enemy fleets.'),
   ('W rankingu okrętów z EDU porównuj role, nie tylko jedną liczbę statystyk.','When reading EDU naval rankings, compare roles rather than one stat alone.'),
  ],
  ('Silny okręt w EDU może być późno dostępny — sprawdź ścieżkę rekrutacji.','A strong ship in EDU might be available late — check recruitment requirements.'),
  'strategy'),
 ('cheats','⚡',('Cheaty i bezpieczny trainer','Cheats and safe trainer use'),
  ('Pomoc w nauce, bez udawania integracji z pamięcią.','Learning aid without pretending to modify live memory.'),
  [
   ('W Kruchyx otwórz Trainer i pakiety MAX i wybierz rodzaj działania.','In Kruchyx, open Trainer & MAX packs and select an action.'),
   ('Dodaj pieniądze: wpisz kwotę, a program przygotuje zgodne z limitem polecenia add_money.','Add money: enter an amount, and Kruchyx prepares add_money commands respecting the per-call limit.'),
   ('Zaznacz postać przed korzystaniem z „this” i sprawdź dokładny identyfikator cechy.','Select the character before using “this” and verify the exact trait identifier.'),
   ('Wklej komendy do konsoli (~) i sprawdź efekt. Nie wszystkie kody działają identycznie w modach.','Paste commands into the (~) console and verify the effect. Not all codes work identically in mods.'),
   ('Zrób zapasowy zapis kampanii przed testowaniem nowych cheatów.','Make a backup save before experimenting with new cheats.'),
   ('Nielimitowany ruch ON/OFF nie jest jeszcze połączony z pamięcią gry — przycisk pozostaje wyłączony.','Unlimited movement ON/OFF is not yet connected to game memory — its control stays disabled.'),
  ],
  ('Nie myl generatora komend z trainerem, który automatycznie edytuje proces gry.','Do not confuse a command generator with a live process-editing trainer.'),
  'cheats'),
 ('mods','◇',('Mody, błędy i okazje','Mods, bugs and opportunities'),
  ('Jak korzystać z Kruchyx bez psucia kampanii.','How to use Kruchyx without damaging a campaign.'),
  [
   ('Najpierw wybierz właściwy folder moda. Sprawdź, jakie źródła aplikacja znalazła.','Select the correct mod folder first. Review the files Kruchyx has found.'),
   ('Ocena siły jednostek w EDU nie mówi automatycznie, kiedy można je zrekrutować.','Unit strength in EDU does not automatically tell you when troops can be recruited.'),
   ('Potencjalnie pusta osada rebeliancka to wskazówka, nie potwierdzenie darmowego podboju.','A potentially ungarrisoned rebel settlement is a lead, not proof of a free conquest.'),
   ('Porównuj możliwości frakcji z plikiem kampanii, budynkami i dostępnymi surowcami.','Compare faction potential with campaign, building and resource data.'),
   ('Błędy struktury plików oznaczają problemy techniczne; słaby garnizon jest zwykle okazją taktyczną.','File inconsistencies are technical issues; a weak garrison is usually a tactical opportunity.'),
  ],
  ('Wyniki analizy plików nie są odczytem obecnego stanu zapisanej kampanii.','File analysis does not reveal the current state of a saved campaign.'),
  'modding'),
]

FIRST_TURNS = [
 ('Sprawdź bilans florenów','Check your florin balance'),('Sprawdź porządek publiczny','Review public order'),
 ('Ustaw budowę w najważniejszych miastach','Queue construction in key towns'),
 ('Wyznacz jedno miasto handlowe','Pick one economic center'),
 ('Wyślij dyplomatę po prawa handlowe','Send a diplomat for trade rights'),
 ('Zbadaj najbliższy cel zwiadem','Scout the nearest target'),
 ('Zbierz armię z piechotą i jazdą','Assemble infantry and cavalry'),
 ('Zabezpiecz granicę i garnizon','Secure border and garrison'),
 ('Zrób zapis przed większą wojną','Save before a major war'),
 ('Sprawdź podatki i kolejki przed końcem tury','Review taxes and queues before ending turn'),
]

GLOSSARY = [
 ('EDU',('Definicje jednostek: statystyki, koszty, frakcje i role.','Unit definition file: stats, costs, faction ownership and roles.')),
 ('EDB',('Definicje budynków i zasad rekrutacji.','Building definitions and recruitment rules.')),
 ('Skarbiec / Treasury',('Stan pieniędzy teraz, a nie dochód w następnej turze.','Cash you own now, not projected income next turn.')),
 ('Morale',('Wola walki jednostki; słabe morale zwiększa ryzyko ucieczki.','A unit’s willingness to fight; low morale increases routing risk.')),
 ('Szarża / Charge',('Korzyść z uderzenia jednostki w ruchu.','Impact from an attacking unit moving into contact.')),
 ('AP / Armor Piercing',('Cecha ataku ograniczającego skuteczność pancerza przeciwnika.','Attack type reducing the effectiveness of enemy armor.')),
 ('Upkeep',('Koszt utrzymania żołnierzy lub okrętów co turę.','Recurring troop or ship cost per turn.')),
 ('Porządek / Public order',('Wskaźnik stabilności osady; bardzo niski grozi zamieszkami.','Settlement stability; very low order risks riots.')),
 ('Przejęcie kupca / Acquisition',('Akcja kupca przeciw konkurencji z możliwością utraty agenta.','Merchant action against a rival with risk of losing your agent.')),
 ('SAV',('Zapis kampanii; jego edycja wymaga poznania i walidacji formatu.','Campaign save; safe edits require validated file parsing.')),
]

def L(pair, lang='pl'):
    return pair[1] if lang == 'en' else pair[0]

def pick(lesson_id):
    return next((x for x in LESSONS if x[0]==lesson_id),None)

def advice_for_faction(model,faction,lang='pl'):
    """Truly file-derived roster/campaign facts + clearly conditional advice."""
    if not model or not faction:return []
    f=next((x for x in model.get('factions',[]) if x['name']==faction),None)
    if not f:return []
    output=[]
    tops=f.get('strengths',[])
    if tops:
        role=tops[0][0]
        topunits=[u['name'] for u in f.get('role_best',{}).get(role,[])[:2]]
        msg_pl=f'W EDU frakcja ma silną kategorię „{role}”; zwróć uwagę na {", ".join(topunits)}. Sprawdź budynki rekrutacyjne, zanim oprzesz na nich plan.'
        msg_en=f'EDU suggests a strong {role} roster; examples: {", ".join(topunits)}. Verify recruitment buildings before relying on them.'
        output.append((msg_en if lang=='en' else msg_pl,'EDU'))
    m=f.get('start_money');s=f.get('start_settlements')
    if m is not None:
        output.append((f'Starting treasury recorded in campaign: {m:,} florins.' if lang=='en' else f'Skarbiec zapisany na starcie: {m:,} florenów.','descr_strat'))
    if s is not None:
        output.append((f'Settlements recorded at start: {s}; consider where trade development makes sense.' if lang=='en' else f'Osad na starcie: {s}. Oceń, które rozwijać gospodarczo.','descr_strat'))
    if tops:
        output.append((L(OFFENSE_ROLE.get(tops[0][0],OFFENSE_ROLE['Piechota wręcz']),lang),'strategy'))
    output.append((('Diplomacy: prioritize trade rights with non-hostile neighbors; allies require checking borders and wars in game.' if lang=='en' else 'Dyplomacja: szukaj praw handlowych z neutralnymi sąsiadami; sojusze dobieraj po sprawdzeniu granic i wojen w grze.'),'general'))
    return output


def building_tip(location, goal, lang='pl'):
    if location=='castle':
        return ('Castle: favor the military buildings needed for your actual army. Budget for troop upkeep and do not expect city-level trade options.' if lang=='en' else 'Zamek: rozwijaj te budynki wojskowe, które odblokowują planowaną armię. Zostaw budżet na utrzymanie i nie oczekuj handlu na poziomie miasta.')
    tips={
      'income':('Rozważ rynek, drogi i port (jeśli osada ma wybrzeże). Oceń lokalne szlaki handlowe.','Consider market, roads and port (if coastal). Evaluate the local trade routes.'),
      'growth':('Rozważ farmy i budynki wspierające rozwój, zachowując stabilny porządek publiczny.','Consider farming and growth-supporting buildings while protecting public order.'),
      'defense':('Najpierw mury, porządek publiczny i wykonalny garnizon, zanim wydasz dużo na handel.','Prioritize walls, public order and a viable garrison before expensive trade upgrades.'),
    }
    return L(tips.get(goal,tips['income']),lang)


def battle_tip(enemy,lang='pl'):
    tips={
     'cavalry':('Użyj włóczników/pikinierów i osłoń strzelców; nie goń jazdy powolną piechotą.','Use spears/pikes and protect missile troops; avoid chasing horsemen with slow infantry.'),
     'infantry':('Zwiąż linię piechotą, atakuj odsłonięte flanki i unikaj szarży na przygotowane włócznie.','Pin their line, target exposed flanks and keep cavalry away from prepared spears.'),
     'missiles':('Wykorzystaj teren do podejścia, nie skupiaj oddziałów i atakuj strzelców odpowiednio szybkimi wojskami.','Advance using terrain and spread your approach; engage their shooters with suitable fast units.'),
     'siege':('Rozpoznaj garnizon, zabierz sprzęt oblężniczy, zachowaj odwody i unikaj zbędnego ostrzału wież.','Scout the garrison, bring siege equipment, keep reserves and avoid needless tower fire.'),
    }
    return L(tips.get(enemy,tips['infantry']),lang)

TURN_PLAN = [
 ('Tury 1–3', 'Turns 1–3',
  'Sprawdź bilans, wybierz priorytet budowlany, podpisz prawa handlowe i zrób zwiad najbliższego celu.',
  'Check balance, start a useful building, seek trade rights and scout your first target.'),
 ('Tury 4–8', 'Turns 4–8',
  'Przygotuj jedną zrównoważoną armię, pilnuj granic i nie dopuszczaj do buntu świeżo zdobytych osad.',
  'Build one balanced field army, protect borders and keep recently captured towns stable.'),
 ('Tury 9–15', 'Turns 9–15',
  'Rozwijaj wybrane centra handlowe i wojskowe. Nie atakuj kilku sąsiadów jednocześnie bez rezerw.',
  'Develop a few trade and recruitment hubs. Avoid multiple simultaneous wars without reserves.'),
 ('Tury 16–20', 'Turns 16–20',
  'Zweryfikuj bilans, utrzymanie wojsk, stosunki dyplomatyczne i kierunek dalszej ekspansji.',
  'Reassess treasury trend, upkeep, diplomacy and your next expansion direction.'),
]

# Strategical advice is original heuristic reasoning, not a game-engine measurement.
OFFENSE_ROLE = {
 'Piechota wręcz':(
   'Ofensywa: broń mocny środek, wiąż wroga piechotą i nie wystawiaj elitarnych oddziałów na oskrzydlenie.',
   'Offense: keep a strong center, pin enemies with infantry and protect elite units from flanking.'),
 'Kawaleria wręcz':(
   'Ofensywa: szukaj otwartego terenu; zwiąż linię piechotą i wykonuj szarże na skrzydła zamiast na włócznie.',
   'Offense: favor open ground; pin enemy infantry and charge flanks rather than prepared spears.'),
 'Piechota strzelecka':(
   'Ofensywa: zabezpiecz pole widzenia strzelcom i osłoń ich przed kawalerią; przeciwnika zmuszaj do podejścia.',
   'Offense: protect your shooters and their line of sight, forcing enemies to close under fire.'),
 'Kawaleria strzelecka':(
   'Ofensywa: wykorzystuj ruchliwość do nękania przeciwnika, pilnuj amunicji i unikaj długiego zwarcia.',
   'Offense: use mobility to harass enemies, manage ammunition and avoid prolonged melee.'),
}
