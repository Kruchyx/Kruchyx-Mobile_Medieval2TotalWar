"""Evidence-focused read-only campaign economy, opportunities and mod quality.

No inference from initial campaign configuration is represented as live save state.
No game-file writes are performed by this module.
"""
from __future__ import annotations
import re
from pathlib import Path
from collections import Counter
from unit_analytics import decode

FACTION = re.compile(r'^\s*faction\s+([A-Za-z][\w]*)\s*,[^\n\r]*',re.M | re.I)
SETTLEMENT = re.compile(r'^\s*settlement(?:_castle|\s+castle)?\s*\{',re.M | re.I)


def extract_block(s, openpos):
    """Balanced braces; ignore brace-shaped strings in comment-only lines."""
    level=0
    for i in range(openpos,len(s)):
        if s[i]=='{':level+=1
        elif s[i]=='}':
            level-=1
            if level==0:return s[openpos:i+1]
    return s[openpos:]


def inspect_campaign(path):
    if not path:return {'factions':{},'empty_rebel_candidates':[]}
    s=decode(path)
    heads=list(FACTION.finditer(s))
    output={}
    for ix,m in enumerate(heads):
        faction=m.group(1).lower()
        chunk=s[m.end():heads[ix+1].start() if ix+1<len(heads) else len(s)]
        cash=re.search(r'^\s*denari\s+(-?\d+)',chunk,re.M|re.I)
        purse=re.search(r'^\s*denari_kings_purse\s+(-?\d+)',chunk,re.M|re.I)
        settlements=[]
        for hit in SETTLEMENT.finditer(chunk):
            block=extract_block(chunk,hit.end()-1)
            region=re.search(r'^\s*region\s+([\w-]+)',block,re.M|re.I)
            level=re.search(r'^\s*level\s+([\w-]+)',block,re.M|re.I)
            pop=re.search(r'^\s*population\s+(\d+)',block,re.M|re.I)
            buildings=re.findall(r'\btype\s+([\w-]+)\s+([\w-]+)',block,re.I)
            settlements.append({'name':region.group(1) if region else '?',
                'kind':'castle' if re.search(r'settlement(?:_castle|\s+castle)',hit.group(0),re.I) else 'city',
                'level':level.group(1) if level else '?',
                'population':int(pop.group(1)) if pop else None,
                'buildings':buildings})
        # An army in the faction block may be a roaming stack, not an actual garrison.
        armies=len(re.findall(r'^\s*army\s*$',chunk,re.M|re.I))
        output[faction]={'money':int(cash.group(1)) if cash else None,
            'kings_purse':int(purse.group(1)) if purse else None,
            'settlements':settlements,'armies':armies,
            'total_population':sum(x['population'] or 0 for x in settlements),
            'city_count':sum(x['kind']=='city' for x in settlements),
            'castle_count':sum(x['kind']=='castle' for x in settlements)}
    # Initial diplomacy only: faction_standings and faction_relationships.
    # They are NOT guarantees of future alliances or current save-game relations.
    for hit in re.finditer(r'^\s*faction_standings\s+([\w]+)\s*,\s*(-?\d+(?:\.\d+)?)\s+([^;\r\n]+)',s,re.M|re.I):
        faction=hit.group(1).lower();score=float(hit.group(2))
        if faction not in output:continue
        output[faction].setdefault('standings',{})
        for dest in [z.strip().lower() for z in hit.group(3).split(',')]:
            if dest and dest!=faction:output[faction]['standings'][dest]=score
    for hit in re.finditer(r'^\s*faction_relationships\s+([\w]+)\s*,\s*(allied_to|at_war_with)\s+([^;\r\n]+)',s,re.M|re.I):
        faction=hit.group(1).lower();rel=hit.group(2).lower()
        if faction not in output:continue
        output[faction].setdefault('relationships',{}).setdefault(rel,[])
        for dest in [z.strip().lower() for z in hit.group(3).split(',')]:
            if dest and dest!=faction and dest not in output[faction]['relationships'][rel]:
                output[faction]['relationships'][rel].append(dest)
    # Do NOT claim an empty rebel settlement from lack of an army entry.
    rebel=output.get('slave',{})
    maybe=[s['name'] for s in rebel.get('settlements',[])] if rebel else []
    return {'factions':output,'empty_rebel_candidates':maybe}


def _ratio(v,maxval):
    return min(1, max(0,v)/maxval) if maxval else 0


def economy_ranking(data):
    """Comparison index, not game-calculated income. Missing money -> incomparable."""
    fs=data.get('factions',{})
    use=[(name,x) for name,x in fs.items() if name not in ('slave','pirates') and x['settlements'] and x['money'] is not None]
    if not use:return []
    maxmoney=max(max(x['money'],0) for _,x in use) or 1
    maxsett=max(len(x['settlements']) for _,x in use) or 1
    maxpop=max(x['total_population'] for _,x in use) or 1
    ranked=[]
    for name,x in use:
        # Explicit and inspectable weighted starting-potential heuristic.
        score=round(100*(.30*_ratio(x['money'],maxmoney)+.30*_ratio(len(x['settlements']),maxsett)+
            .25*_ratio(x['total_population'],maxpop)+.15*_ratio(x['city_count'],maxsett)),1)
        ranked.append({'name':name,'score':score,**x,'methods':'30% treasury, 30% settlements, 25% population, 15% city count'})
    ranked.sort(key=lambda x:(-x['score'],x['name']))
    return ranked


def _source(found,kind):
    f=found.get(kind)
    return str(f) if f else None


def detect_findings(context,analysis=None):
    """Each finding has source, confidence and scope; never claim an exploit has been proven."""
    files=context['files']
    campaign=analysis or inspect_campaign(files.get('campaign'))
    findings=[]
    def add(kind,title_pl,title_en,body_pl,body_en,source,confidence,priority='low'):
        findings.append({'kind':kind,'title':(title_pl,title_en),'body':(body_pl,body_en),
                         'source':str(source) if source else '', 'confidence':confidence,'priority':priority})
    if files.get('campaign'):
        rebel=campaign['factions'].get('slave',{})
        settlements=rebel.get('settlements',[])
        if settlements:
            names=', '.join(s['name'] for s in settlements[:9])
            add('opportunity','Osady rebelianckie wymagają zwiadu','Rebel settlements worth scouting',
                f'W pliku startowym znaleziono {len(settlements)} osad rebelianckich ({names}). Sprawdź obrońców szpiegiem w grze. Brak armii w bloku osady nie dowodzi braku automatycznego garnizonu.',
                f'{len(settlements)} rebel settlements are defined ({names}). Scout defenses in game. Lack of a listed army does not rule out engine-generated garrisons.',
                files['campaign'],'potential')
        for name,f in campaign['factions'].items():
            if name in ('slave','pirates'):continue
            if f['money'] is not None and f['money']<0:
                add('config','Ujemny skarbiec frakcji','Faction starts with negative treasury',
                    f'{name}: w descr_strat zapisano {f["money"]} florenów; może to być zamierzone przez autora moda.',
                    f'{name}: descr_strat has {f["money"]} florins. This may be intentional balancing.',
                    files['campaign'],'confirmed')
        if not campaign['factions']:
            add('config','Nie rozpoznano frakcji','No campaign factions recognized',
                'Plik istnieje, lecz parser nie wykrył bloków faction.',
                'The file exists, but no faction records were recognized.',files['campaign'],'confirmed','high')
    else:
        add('limitation','Brak danych kampanii','Missing campaign data',
            'Bez descr_strat nie da się wiarygodnie ocenić skarbca ani osad na starcie.',
            'Without descr_strat, start treasury and settlements cannot be evaluated.',context['folder'],'confirmed')
    if not files.get('buildings'):
        add('limitation','Rekrutacja elit niezweryfikowana','Elite recruitment not verified',
            'Brak export_descr_buildings.txt. Nie można potwierdzić kiedy i gdzie wyprodukujesz dane jednostki.',
            'Missing export_descr_buildings.txt. Elite recruitment conditions are unverified.',context['folder'],'confirmed')
    if not files.get('edu'):
        add('limitation','Nie znaleziono EDU','EDU not found',
            'Ranking wojsk i kontrola rekrutacji wymagają export_descr_unit.txt.',
            'Unit rankings and recruitment checks require export_descr_unit.txt.',context['folder'],'confirmed')
    # Grep recruit_pool references for missing EDU: possible file-layer issues, not automatically errors.
    if files.get('buildings') and files.get('edu'):
        edb=decode(files['buildings']);edu=decode(files['edu'])
        types={s.lower() for s in re.findall(r'^\s*type\s+([^\r\n;]+)',edu,re.M|re.I)}
        referrals=re.findall(r'\brecruit_pool\s+"([^"]+)"',edb,re.I)
        missing=sorted({s for s in referrals if s.lower() not in types})
        if missing:
            add('config','Jednostki z budynków spoza wczytanego EDU','Recruitment units absent from loaded EDU',
                f'Znaleziono {len(missing)} ID jednostek w EDB bez odpowiadającego wpisu w bieżącym EDU, np.: '+', '.join(missing[:8])+'. Mogą pochodzić z archiwum, dodatku silnika lub innej warstwy.',
                f'{len(missing)} IDs in EDB are absent from current EDU, e.g. '+', '.join(missing[:8])+'. They may be defined in packed or engine-added data.',
                files['buildings'],'potential')
    # Merchants option: find in nearby mod config, without blanket recursion.
    data=context['folder']
    merchant_cfg=None
    for p in [data/'descr_campaign_db.xml',data/'world'/'maps'/'campaign'/'imperial_campaign'/'descr_campaign_db.xml']:
        if p.is_file():merchant_cfg=p;break
    if merchant_cfg:
        txt=decode(merchant_cfg)
        hit=re.search(r'allow_resource_forts\s*=\s*["\']?(true|false|0|1)["\']?',txt,re.I)
        if hit:
            add('merchant','Ustawienie resource forts','Resource forts setting',
                f'W konfiguracji wykryto allow_resource_forts={hit.group(1)}. To wskazówka do testu mechaniki kupców, a nie potwierdzenie exploitu.',
                f'Configuration includes allow_resource_forts={hit.group(1)}. This is a merchant mechanics lead, not proof of an exploit.',
                merchant_cfg,'confirmed')
        else:
            add('merchant','Konfiguracja kampanii dostępna','Campaign configuration available',
                'Znaleziono descr_campaign_db.xml. Mechaniki kupców mogą się różnić w zależności od moda i silnika.',
                'Found descr_campaign_db.xml. Merchant mechanics depend on mod and engine settings.',
                merchant_cfg,'confirmed')
    return findings


def merchant_insights(resources,lang='pl'):
    if not resources:
        return [('No resource definitions available; load descr_sm_resources.txt.' if lang=='en' else 'Brak definicji zasobów: wczytaj descr_sm_resources.txt.','missing')]
    top=sorted((x for x in resources if x.get('value',0)>0),key=lambda x:-x['value'])[:8]
    return [(f"{x['name']}: trade_value {x['value']:g} — not florins/turn" if lang=='en' else
            f"{x['name']}: trade_value {x['value']:g} — to nie floreny/turę",'descr_sm_resources') for x in top]


def diplomacy_advice(data,faction,lang='pl'):
    """Give named recommendations only when start-of-campaign evidence supports them."""
    f=data.get('factions',{}).get(faction)
    if not f:return []
    relations=f.get('relationships',{});standings=f.get('standings',{})
    allied=set(relations.get('allied_to',[]));war=set(relations.get('at_war_with',[]))
    results=[]
    for name in sorted(allied):
        results.append((('Initial alliance with '+name+' — useful as an opening diplomatic fact, not a guarantee of loyalty.' if lang=='en' else
                         'Sojusz początkowy z '+name+' — fakt z kampanii, nie gwarancja lojalności.'),'descr_strat'))
    candidates=sorted(((score,name) for name,score in standings.items()
                        if score>0 and name not in allied and name not in war and name not in ('slave','pirates')),reverse=True)
    for score,name in candidates[:3]:
        results.append((('Potential trade/peace contact: '+name+f' (starting standing {score:+.2f}). Alliance is not guaranteed.' if lang=='en' else
                         'Możliwy partner handlowy: '+name+f' (stosunki początkowe {score:+.2f}). Sojusz nie jest gwarantowany.'),'descr_strat'))
    enemies=[n for n in sorted(war) if n not in ('slave','pirates')]
    for name in enemies[:3]:
        results.append((('Starts at war with '+name+'; consider defenses and a realistic campaign plan.' if lang=='en' else
                         'Wojna na starcie z '+name+' — zaplanuj obronę i realistyczny kierunek ekspansji.'),'descr_strat'))
    negative=sorted((score,name) for name,score in standings.items() if score<0 and name not in war and name!='slave')
    for score,name in negative[:2]:
        results.append((('Poor starting standing with '+name+f' ({score:+.2f}) — diplomatic risk, not automatic war.' if lang=='en' else
                         'Niskie stosunki z '+name+f' ({score:+.2f}) — ryzyko dyplomatyczne, nie automatyczna wojna.'),'descr_strat'))
    return results
