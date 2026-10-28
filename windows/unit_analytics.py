"""Read-only, evidence-led EDU analytics for Medieval II mod files.
Scores are transparent heuristics, NOT battle simulations. Never edits source files.
"""
from pathlib import Path
from collections import defaultdict
import re, math

def _field(body, name):
    m=re.search(r"^\s*"+re.escape(name)+r"\s+([^;\r\n]+)",body,re.M|re.I)
    return m.group(1).strip() if m else ''

def _parts(text):return [x.strip() for x in text.split(',')]
def _num(s,default=0.0):
    try:return float(s.strip())
    except (TypeError,ValueError,AttributeError):return default

def parse_units(text):
    # Split at genuine EDU type declarations; skip commented declarations.
    matches=list(re.finditer(r"^\s*type[ \t]+([^;\r\n]+)",text,re.M|re.I))
    units=[]
    for i,m in enumerate(matches):
        block=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
        name=m.group(1).strip()
        if not name or name.lower()=='generic':continue
        a=_parts(_field(block,'stat_pri')); b=_parts(_field(block,'stat_sec'))
        arm=_parts(_field(block,'stat_pri_armour')); mental=_parts(_field(block,'stat_mental'))
        cost=_parts(_field(block,'stat_cost')); soldiers=_parts(_field(block,'soldier'))
        cat=_field(block,'category').lower(); cl=_field(block,'class').lower()
        owners=[x.strip() for x in _field(block,'ownership').split(',') if x.strip()]
        stats={
            'name':name,'category':cat,'class':cl,'owners':owners,
            'attack':_num(a[0]) if a else 0,'charge':_num(a[1]) if len(a)>1 else 0,
            'secondary_attack':_num(b[0]) if b else 0,
            'defence':sum(_num(x) for x in arm[:3]),
            'morale':_num(mental[0]) if mental else 0,
            'health':_num(_parts(_field(block,'stat_health'))[0]),
            'range':_num(a[3]) if len(a)>3 else 0,
            'ammo':_num(a[4]) if len(a)>4 else 0,
            'cost':_num(cost[1]) if len(cost)>1 else 0,
            'upkeep':_num(cost[2]) if len(cost)>2 else 0,
            'size':_num(soldiers[1]) if len(soldiers)>1 else 0,
            'projectile':a[2].lower() if len(a)>2 else 'no',
            'armour_piercing': 'ap' in _parts(_field(block,'stat_pri_attr')),
            'second_ap': 'ap' in _parts(_field(block,'stat_sec_attr')),
            'attributes':_field(block,'attributes'),
        }
        # Unit role determined from category & projectile / flags; exclude generals when reporting ordinary troops.
        if cat=='ship':role='Okręty'
        elif cat=='siege':role='Oblężnicze'
        elif cat=='cavalry':role='Kawaleria strzelecka' if cl=='missile' else 'Kawaleria wręcz'
        elif cat=='infantry':role='Piechota strzelecka' if cl=='missile' else 'Piechota wręcz'
        else:role='Pozostałe'
        stats['role']=role
        stats['general']= 'general_unit' in stats['attributes'].split(', ') or 'bodyguard' in name.lower()
        stats['score']=round(score(stats),1)
        units.append(stats)
    return units

def score(u):
    """Heuristic within a tactical role. Scale intentionally not called a percentage."""
    role=u['role']; health=min(u['health'],4)
    defence=u['defence']; attack=u['attack']; charge=u['charge']; morale=u['morale']
    ap=3.0 if u['armour_piercing'] else 0.0
    if role in ('Piechota wręcz','Kawaleria wręcz'):
        return attack*1.7+charge*(1.45 if role=='Kawaleria wręcz' else .7)+defence*1.25+morale*.9+health*3.0+ap
    if role in ('Piechota strzelecka','Kawaleria strzelecka'):
        return attack*2.0 + min(u['range'],250)*.085 + min(u['ammo'],50)*.13 + defence*.65 + morale*.85 + health*2 + ap + u['secondary_attack']*.35
    if role=='Okręty':return attack*1.6+charge*.3+defence+health*3+morale*.8+u['secondary_attack']*.7
    if role=='Oblężnicze':return attack*1.9+min(u['range'],450)*.065+min(u['ammo'],80)*.08 + defence*.25
    return attack+defence+morale

def parse_resources(text):
    result=[]
    blocks=re.split(r'(?=^\s*type[ \t]+)',text,flags=re.M)
    for b in blocks:
        m=re.match(r'\s*type[ \t]+(\w+)',b)
        if m:result.append({'name':m.group(1),'value':_num(_field(b,'trade_value'))})
    return sorted(result,key=lambda x:-x['value'])

def faction_ranking(units):
    by=defaultdict(list)
    for u in units:
        if u['category'] in ('ship','siege') or u['general']:continue
        for owner in u['owners']:
            if owner!='slave':by[owner].append(u)
    output=[]
    roles=['Piechota wręcz','Kawaleria wręcz','Piechota strzelecka','Kawaleria strzelecka']
    for name,roster in by.items():
        role_scores={r:sorted([u['score'] for u in roster if u['role']==r],reverse=True)[:3] for r in roles}
        active=[sum(s)/len(s) for s in role_scores.values() if s]
        if not active:continue
        # Average of role-leading strength; penalize missing categories lightly, no initial economy claim.
        strength=round(sum(active)/len(active)+min(len(active),4)*1.5,1)
        best=sorted(roster,key=lambda u:-u['score'])[:3]
        output.append({'name':name,'score':strength,'count':len(roster),'roles':len(active),'best':best})
    return sorted(output,key=lambda u:(-u['score'],u['name']))

def scan_mod(path):
    p=Path(path).expanduser().resolve()
    if p.is_file():
        if p.name.lower()=='export_descr_unit.txt':return p,p.parent
        raise ValueError('Wybierz export_descr_unit.txt lub folder moda/data.')
    candidates=[p/'export_descr_unit.txt',p/'data'/'export_descr_unit.txt']
    candidates += list(p.glob('mods/*/data/export_descr_unit.txt'))[:50]
    hits=[c for c in candidates if c.is_file()]
    if len(hits)==1:return hits[0],hits[0].parent
    if len(hits)>1:raise ValueError('Znaleziono wiele plików EDU. Wskaż konkretny export_descr_unit.txt.')
    raise FileNotFoundError('Nie znaleziono export_descr_unit.txt. Wskaż plik EDU ręcznie; może być zapakowany w .pack.')

def decode(path):
    data=Path(path).read_bytes()
    for enc in ('utf-8-sig','cp1250','latin-1'):
        try:return data.decode(enc)
        except UnicodeDecodeError:continue
    return data.decode('latin-1')
