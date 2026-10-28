"""Mod data inspection and explainable, offline strategy recommendations.
All operations are read-only. No claims about battle outcomes or recruitability without EDB.
"""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict
import re
from unit_analytics import parse_units, faction_ranking, parse_resources, decode
from vanilla_support import find_game_root, cache_data_dir, vanilla_cache_root

ROLES = ('Piechota wręcz','Kawaleria wręcz','Piechota strzelecka','Kawaleria strzelecka')
ROLE_SHORT = {'Piechota wręcz':'Piechota','Kawaleria wręcz':'Kawaleria','Piechota strzelecka':'Strzelcy','Kawaleria strzelecka':'Strzelcy konni'}
FR_NAMES = {'england':'Anglia','france':'Francja','portugal':'Portugalia','hre':'Święte Cesarstwo','poland':'Polska','hungary':'Węgry','byzantium':'Bizancjum','lithuania':'Litwa','denmark':'Dania','spain':'Hiszpania','russia':'Ruś / Rosja','novgorod':'Nowogród','egypt':'Egipt','turks':'Turcy','moors':'Maurowie','venice':'Wenecja','milan':'Mediolan','scotland':'Szkocja','sicily':'Sycylia','jerusalem':'Jerozolima','antioch':'Antiochia','teutonic_order':'Zakon Krzyżacki','mongols':'Mongołowie','timurids':'Timurydzi','papal_states':'Państwo Papieskie','norway':'Norwegia','ireland':'Irlandia','wales':'Walia','karaman':'Karaman','berbers':'Berberowie','makuria':'Makuria','persians':'Persowie','aztecs':'Aztekowie','timurids':'Timurydzi','cumans':'Kumanowie','apachean':'Apacze','miskito':'Miskito','tlaxcalans':'Tlaxcalanie','vladimir':'Włodzimierz','moscow':'Moskwa','chichimeca':'Chichimekowie','tarascans':'Taraskowie','utes':'Utowie','mayans':'Majowie'}

def pretty(name):return FR_NAMES.get(name, name.replace('_',' ').title())


FR_NAMES_EN = {
 'england':'England','france':'France','portugal':'Portugal','hre':'Holy Roman Empire',
 'poland':'Poland','hungary':'Hungary','byzantium':'Byzantine Empire','lithuania':'Lithuania',
 'denmark':'Denmark','spain':'Spain','russia':'Russia','novgorod':'Novgorod','egypt':'Egypt',
 'turks':'Turks','moors':'Moors','venice':'Venice','milan':'Milan','scotland':'Scotland',
 'sicily':'Sicily','jerusalem':'Jerusalem','antioch':'Antioch','teutonic_order':'Teutonic Order',
 'mongols':'Mongols','timurids':'Timurids','papal_states':'Papal States','norway':'Norway',
 'ireland':'Ireland','wales':'Wales','karaman':'Karaman','berbers':'Berbers','makuria':'Makuria',
 'persians':'Persia','aztecs':'Aztecs','cumans':'Cumans','apachean':'Apache','miskito':'Miskito',
 'tlaxcalans':'Tlaxcalans','vladimir':'Vladimir','moscow':'Moscow','chichimeca':'Chichimeca',
 'tarascans':'Tarascans','utes':'Utes','mayans':'Mayans', 'slave':'Rebels','pirates':'Pirates'
}

def pretty_lang(name,lang='pl'):
    return FR_NAMES_EN.get(name,name.replace('_',' ').title()) if lang=='en' else pretty(name)

def file_capabilities(folder):
    """Loose mod overrides > loose base game > dedicated external vanilla cache.

    The chosen campaign remains tied to its true provenance. Never imply a packed
    game is fully decoded, nor silently reuse the bundled demonstration EDU.
    """
    p=Path(folder).expanduser().resolve()
    if p.is_file():
        data=p.parent;mod=data.parent if data.name.lower()=='data' else data
    else:
        data=p/'data' if (p/'data').is_dir() else p
        mod=p if (p/'data').is_dir() else p.parent if p.name.lower()=='data' else p
    game=find_game_root(p)
    base=(game/'data') if game else None
    cache=cache_data_dir(vanilla_cache_root(game)) if game else None
    is_vanilla=bool(game and p in (game,game/'data'))
    layers=[('selected',data)]
    if game:
        if base and base!=data:layers.append(('base_game',base))
        if cache and cache!=data:layers.append(('extracted_cache',cache))
    candidate_rel={
      'edu':Path('export_descr_unit.txt'),
      'buildings':Path('export_descr_buildings.txt'),
      'resources':Path('descr_sm_resources.txt'),
      'regions':Path('world/maps/base/descr_regions.txt'),
      'traits':Path('export_descr_character_traits.txt'),
    }
    found={}; origins={}
    for key,rel in candidate_rel.items():
        found[key]=None
        for origin,layer in layers:
            candidate=layer/rel
            if not candidate.is_file() and origin=='extracted_cache' and layer.is_dir():
                candidate=next((q for q in layer.rglob(rel.name) if q.is_file()),candidate)
            if candidate.is_file():found[key]=candidate;origins[key]=origin;break
    campaigns=[]
    for origin,layer in layers:
        d=layer/'world/maps/campaign'
        if not d.is_dir():continue
        for path in sorted(d.glob('*/descr_strat.txt')):
            if not any(q.parent.name==path.parent.name for q in campaigns):campaigns.append(path)
    # Include files unpacked under different base prefixes, but never arbitrary mod files.
    if cache and cache.is_dir():
        for candidate in cache.rglob('descr_strat.txt'):
            if candidate.parent.name=='imperial_campaign' and candidate.is_file() and not any(q.parent.name==candidate.parent.name for q in campaigns):
                campaigns.append(candidate)
    campaigns.sort(key=lambda x:(x.parent.name.lower()!='imperial_campaign',x.parent.name))
    found['campaign']=campaigns[0] if campaigns else None
    if found['campaign']:
        origins['campaign']=next((name for name,layer in layers if found['campaign'].is_relative_to(layer)), 'selected')
    if p.is_file() and p.name.lower()=='export_descr_unit.txt':
        found['edu']=p; origins['edu']='selected'
    return {'folder':data,'mod':mod,'files':found,'campaigns':campaigns,
            'game_root':game,'vanilla':is_vanilla,'origins':origins,
            'packed_base':bool(game and not found.get('edu') and (game/'packs').is_dir())}

def _playability(raw):
    result=[]
    for key in ('playable','unlockable'):
        found=re.search(r'(?im)^\s*'+key+r'\s*\n(.*?)(?=^\s*(?:playable|unlockable|nonplayable|start_date|faction|end)\b)',raw,re.S|re.M)
        if found:
            result.extend(re.findall(r'(?m)^\s*([a-z][\w]*)\s*$',found.group(1)))
    return list(dict.fromkeys(result))

def campaign_info(path):
    if not path:return {'playable':[], 'factions':{},'start_date':None}
    text=decode(path)
    heads=list(re.finditer(r'(?im)^\s*faction\s+([a-z][\w]*)\s*,[^\r\n]*',text))
    factions={}
    for i,h in enumerate(heads):
        chunk=text[h.end():heads[i+1].start() if i+1<len(heads) else len(text)]
        money=re.search(r'(?im)^\s*denari\s+(-?\d+)',chunk)
        settlements=len(re.findall(r'(?im)^\s*settlement(?:_castle|\s+castle)?\s*\{',chunk))
        factions[h.group(1).lower()]={'money':int(money.group(1)) if money else None,'settlements':settlements}
    start=re.search(r'(?im)^\s*start_date\s+(-?\d+)',text)
    return {'playable':_playability(text),'factions':factions,'start_date':int(start.group(1)) if start else None}

def analyze(path,campaign_override=None):
    context=file_capabilities(path)
    if campaign_override is not None:
        selected=Path(campaign_override)
        if selected in context['campaigns']:
            context['files']['campaign']=selected
    f=context['files'];units=parse_units(decode(f['edu'])) if f['edu'] else []
    facts=faction_ranking(units) if units else []
    resources=parse_resources(decode(f['resources'])) if f['resources'] else []
    camp=campaign_info(f['campaign'])
    enriched=[]
    for frac in facts:
        roster=[u for u in units if frac['name'] in u['owners'] and not u['general']]
        role_best={}
        for r in ROLES:
            group=sorted((u for u in roster if u['role']==r),key=lambda x:-x['score'])
            if group:role_best[r]=group[:3]
        strengths=sorted(((r,round(sum(u['score'] for u in top)/len(top),1)) for r,top in role_best.items()), key=lambda x:-x[1])
        weak=[ROLE_SHORT[r] for r in ROLES if r not in role_best]
        best_role=strengths[0][0] if strengths else ''
        style={'Piechota wręcz':'walkę piechoty i przełamywanie linii','Kawaleria wręcz':'szarże i oskrzydlanie','Piechota strzelecka':'ostrzał i obronę pozycji','Kawaleria strzelecka':'mobilność, nękanie i unikanie zwarcia'}.get(best_role,'różnorodna armia')
        info=camp['factions'].get(frac['name'],{})
        enriched.append({**frac,'display':pretty(frac['name']),'roster':roster,'role_best':role_best,'strengths':strengths,
                         'weak':weak,'style':style,'start_money':info.get('money'),'start_settlements':info.get('settlements'),
                         'playable':frac['name'] in camp['playable'] if camp['playable'] else None})
    return {'context':context,'units':units,'factions':enriched,'resources':resources,'campaign':camp}

def explanation(f):
    strengths=', '.join(ROLE_SHORT[r].lower() for r,_ in f['strengths'][:2]) or 'zróżnicowany roster'
    missing=(' Uwaga: w EDU brak oddziałów w rolach: '+', '.join(f['weak'])+'.') if f['weak'] else ' Frakcja ma jednostki we wszystkich czterech głównych rolach.'
    sample=', '.join(u['name'] for u in f['best'][:3])
    return (f"{f['display']} jest interesującym wyborem, jeśli cenisz {f['style']}. "
            f"Jej przewagi w danych jednostek to: {strengths}. Przykładowe mocne jednostki: {sample}."+missing)

def report(model, limit=8):
    f=model['factions']; u=model['units']; files=model['context']['files'];c=model['campaign']
    lines=['KRUCHYX MEDIEVAL MOD STUDIOS  |  Raport stratega  |  v0.9.5','='*70]
    lines.append('Źródło: '+str(model['context']['folder']))
    lines.append('Wczytane pliki: '+', '.join(k for k,v in files.items() if v))
    lines.append(f'Jednostki: {len(u)} | Frakcje w EDU: {len(f)} | Okręty: {sum(x["role"]=="Okręty" for x in u)}')
    lines.append('')
    lines.append('WAŻNE: ranking potencjału ROSTERU, nie siły startowej ani test bojowy.')
    if not files['buildings']:lines.append('Brak EDB: niezweryfikowana możliwość i moment rekrutacji elitarnych jednostek.')
    if not files['campaign']:lines.append('Brak descr_strat: niezweryfikowana grywalność, pieniądze i armie startowe.')
    lines.append('')
    if f:
        lines.append('TOP FRAKCJI — OCENA POTENCJAŁU JEDNOSTEK:')
        for i,x in enumerate(f[:limit],1):
            lines.append(f"{i}. {x['display']}: {x['score']:.1f} pkt | {x['count']} jednostek")
            lines.append('   '+explanation(x))
            if x['start_money'] is not None:lines.append('   Skarbiec startowy z kampanii: '+str(x['start_money']))
    else:lines.append('BRAK EDU: nie można przygotować rankingu jednostek.')
    lines.append('')
    for role in ('Piechota wręcz','Kawaleria wręcz','Piechota strzelecka','Kawaleria strzelecka','Okręty','Oblężnicze'):
        ranked=sorted((x for x in u if x['role']==role and not x['general']),key=lambda x:-x['score'])
        if ranked:lines.append(role.upper()+': '+', '.join(f"{x['name']} ({x['score']:.1f})" for x in ranked[:5]))
    if model['resources']:
        lines.extend(['','ZASOBY (trade_value, to nie dochód/turę): '+', '.join(f"{x['name']}: {x['value']:g}" for x in model['resources'][:8])])
    # New v0.9.2 sections use only the selected campaign, and label every inference.
    from campaign_intelligence import inspect_campaign, economy_ranking, detect_findings
    if files.get('campaign'):
        econ=economy_ranking(inspect_campaign(files['campaign']))
        lines.extend(['', 'POTENCJAŁ GOSPODARCZY NA STARCIE (heurystyka, nie dochód/turę):'])
        for i,x in enumerate(econ[:limit],1):
            lines.append(f"{i}. {pretty(x['name'])}: {x['score']:.1f}/100 — skarbiec {x['money']}, osady {len(x['settlements'])}, populacja {x['total_population']}")
    lines.extend(['', 'ŁOWCA OKAZJI — źródło i poziom pewności:'])
    for v in detect_findings(model['context'])[:12]:
        lines.append(f"- {v['title'][0]} [{v['confidence']}] | {v['source']}: {v['body'][0]}")
    lines.extend(['','Uwaga: rekomendacje są wyjaśnialnymi regułami offline, a nie modelem AI i nie symulują bitew.','Wykonane przez Kruchyx'])
    return '\n'.join(lines)+'\n'


def leaders_by_role(model, role, limit=3):
    """Rank faction specialists within one role only (scores not compared across roles)."""
    out=[]
    for f in model['factions']:
        top=f['role_best'].get(role)
        if top:
            rating=sum(u['score'] for u in top)/len(top)
            out.append((round(rating,1),f))
    return sorted(out,key=lambda x:(-x[0],x[1]['name']))[:limit]

def mod_summary(model):
    u=model['units'];f=model['factions']
    if not u:return 'Nie znaleziono EDU, dlatego nie można jeszcze określić charakteru militarnego tego moda.'
    counts={role:sum(x['role']==role for x in u) for role in ('Piechota wręcz','Kawaleria wręcz','Piechota strzelecka','Kawaleria strzelecka','Okręty','Oblężnicze')}
    top=sorted(counts.items(),key=lambda p:-p[1])[:2]
    first=f'Zbadano {len(u)} typów jednostek i {len(f)} identyfikatory frakcji w EDU.'
    second=' Najliczniejsze kategorie to '+ ' oraz '.join(f'{k.lower()} ({v})' for k,v in top)+'.'
    third=' Występują też '+str(counts['Okręty'])+' typów jednostek morskich.'
    caution=' Ten opis opiera się na składzie pliku EDU, nie na porównaniu ze zwykłą grą ani danych kampanii.'
    return first+second+third+caution


def explanation_en(f):
    roles={'Piechota wręcz':'melee infantry','Kawaleria wręcz':'melee cavalry',
           'Piechota strzelecka':'missile infantry','Kawaleria strzelecka':'missile cavalry'}
    strengths=', '.join(roles.get(r,r) for r,_ in f['strengths'][:2]) or 'diverse roster'
    weak=', '.join(f['weak'])
    note=(' EDU contains no units for some major roles: '+weak+'.' if weak else
          ' The faction has units in all four main roles.')
    sample=', '.join(u['name'] for u in f['best'][:3])
    best_role=f['strengths'][0][0] if f['strengths'] else ''
    style={'Piechota wręcz':'holding and breaking infantry lines',
           'Kawaleria wręcz':'heavy charges and flanking',
           'Piechota strzelecka':'missile fire and defensive formations',
           'Kawaleria strzelecka':'skirmishing and mobile tactics'}.get(best_role,'balanced warfare')
    return (f"{f['display']} may suit players who enjoy {style}. "
            f"Its EDU strengths include {strengths}. Examples: {sample}.{note} "
            'Recruitability and start strength must be checked separately.')

def mod_summary_en(model):
    units=model['units']; factions=model['factions']
    if not units:return 'No EDU found yet: military character cannot be assessed.'
    roles=['Piechota wręcz','Kawaleria wręcz','Piechota strzelecka','Kawaleria strzelecka','Okręty','Oblężnicze']
    names={'Piechota wręcz':'melee infantry','Kawaleria wręcz':'melee cavalry',
           'Piechota strzelecka':'missile infantry','Kawaleria strzelecka':'missile cavalry','Okręty':'ships','Oblężnicze':'siege'}
    top=sorted(((r,sum(x['role']==r for x in units)) for r in roles),key=lambda x:-x[1])[:2]
    return (f"Inspected {len(units)} unit types and {len(factions)} faction identifiers in the EDU. "
            + 'Largest categories: '+', '.join(f'{names[r]} ({n})' for r,n in top)+'. '
            + f"Includes {sum(x['role']=='Okręty' for x in units)} types of ships. "
            + 'These findings describe EDU content, not starting armies or guaranteed recruitment.')
