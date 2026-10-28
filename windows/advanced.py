"""Focused edits to Medieval II campaign/EDU. No regex substitution outside matched records."""
import re

HEAD = re.compile(r'(?im)^[ \t]*faction[ \t]+([a-z_][\w]*)[ \t]*,[^\r\n]*')
SETTLEMENT = re.compile(r'(?im)^[ \t]*settlement(?:[ \t]+castle)?[ \t]*(?:\r?\n[ \t]*)?\{')
CHARS = re.compile(r'(?im)^[ \t]*character[ \t]+([^,\r\n]+),([^\r\n]*)')
TYPES = re.compile(r'(?im)^type[ \t]+([^\r\n;]+)')

def replace_span(text, start, end, value):
    return text[:start] + str(value) + text[end:]

def faction_blocks(text):
    matches=list(HEAD.finditer(text))
    return [(m.group(1),m.start(), matches[i+1].start() if i+1<len(matches) else len(text)) for i,m in enumerate(matches)]

def settlements(text):
    records=[]
    for faction,begin,end in faction_blocks(text):
        part=text[begin:end]
        for m in SETTLEMENT.finditer(part):
            st=begin+m.start(); brace=begin+m.end()-1
            depth=0; close=None
            for i in range(brace,end):
                if text[i]=='{':depth+=1
                elif text[i]=='}':
                    depth-=1
                    if depth==0:close=i+1;break
            if close is None: continue
            chunk=text[st:close]
            region=re.search(r'(?im)^[ \t]*region[ \t]+([^\s;]+)',chunk)
            pop=re.search(r'(?im)^[ \t]*population[ \t]+(\d+)',chunk)
            level=re.search(r'(?im)^[ \t]*level[ \t]+([\w]+)',chunk)
            if region:
                records.append(dict(region=region.group(1),faction=faction, start=st,end=close,
                                    pop=pop.group(1) if pop else '',level=level.group(1) if level else '',
                                    buildings=re.findall(r'(?im)^[ \t]*type[ \t]+([^\r\n]+)',chunk)))
    return records

def edit_settlement(text, region, field, value):
    matches=[x for x in settlements(text) if x['region']==region]
    if len(matches)!=1:raise ValueError('Region nie znaleziony lub występuje wiele razy: '+region)
    rec=matches[0]
    if field=='owner':
        if value==rec['faction']:return text
        blocks=faction_blocks(text)
        dest=next((x for x in blocks if x[0]==value),None)
        if not dest:raise ValueError('Nieznana frakcja docelowa.')
        if value=='slave':raise ValueError('Przekazanie buntownikom zablokowane w formularzu.')
        chunk=text[rec['start']:rec['end']]
        without=text[:rec['start']]+text[rec['end']:]
        destpos=next((s for n,s,e in faction_blocks(without) if n==value),None)
        if destpos is None:raise ValueError('Nie znaleziono sekcji frakcji.')
        # Insert immediately after target faction header and finance entries, before target settlements.
        header=re.search(r'(?im)^[ \t]*faction[ \t]+[^\r\n]+', without[destpos:])
        nextline=destpos+header.end()
        tail=without[nextline:]
        lines=list(re.finditer(r'[^\r\n]*(?:\r\n|\n|\r|$)',tail))
        insertion=nextline
        for line in lines:
            if not line.group(0).strip():insertion+=len(line.group(0));continue
            if re.match(r'\s*(?:ai_label|denari|denari_kings_purse)\b',line.group(0)):
                insertion+=len(line.group(0));continue
            break
        newline='\r\n' if '\r\n' in text else '\n'
        return without[:insertion]+newline+chunk.rstrip('\r\n')+newline+without[insertion:]
    fields={'population':r'population','level':r'level','building':r'type'}
    if field not in fields:raise ValueError('Nieobsługiwane pole osady.')
    part=text[rec['start']:rec['end']]
    if field=='building':
        # Edit first listed building only; preserve all other attributes.
        pattern=r'(?im)^([ \t]*type[ \t]+)([^\r\n]+)'
    else:pattern=r'(?im)^([ \t]*'+fields[field]+r'[ \t]+)([^\r\n;]+)'
    m=re.search(pattern,part)
    if not m:raise ValueError('Osada nie ma pola '+field)
    if field=='population' and (not str(value).isdigit() or not 1<=int(value)<=2000000):raise ValueError('Populacja 1–2 000 000.')
    if field=='level' and not re.fullmatch(r'[a-z_]+',value):raise ValueError('Nieprawidłowy poziom osady.')
    if field=='building' and not re.fullmatch(r'[A-Za-z0-9_]+[ \t]+[A-Za-z0-9_]+',value):raise ValueError('Podaj kategorię i poziom budynku.')
    return replace_span(text,rec['start']+m.start(2),rec['start']+m.end(2),value)

def characters(text):
    rec=[]
    for faction,start,end in faction_blocks(text):
        segment=text[start:end]
        matches=list(CHARS.finditer(segment))
        for i,m in enumerate(matches):
            pos=start+m.start();last=start+(matches[i+1].start() if i+1<len(matches) else len(segment))
            attrs=m.group(2)
            age=re.search(r'\bage[ \t]+(\d+)',attrs)
            units=[]
            for um in re.finditer(r'(?im)^[ \t]*unit[ \t]+([^\r\n]+)',text[pos:last]):
                line=um.group(1); exp=re.search(r'\bexp[ \t]+(\d+)',line)
                name=line.split(' exp ')[0].strip()
                units.append((name, exp.group(1) if exp else ''))
            rec.append(dict(faction=faction,name=m.group(1).strip(),age=age.group(1) if age else '',start=pos,end=last,units=units))
    return rec

def edit_character(text,faction,name,field,value,unit_index=0):
    found=[x for x in characters(text) if x['faction']==faction and x['name']==name]
    if len(found)!=1:raise ValueError('Nie znaleziono unikalnego generała/agenta.')
    rec=found[0];part=text[rec['start']:rec['end']]
    if field=='age':
        if not str(value).isdigit() or not 1<=int(value)<=120:raise ValueError('Wiek 1–120.')
        m=re.search(r'\bage[ \t]+(\d+)',part.splitlines()[0])
        if not m:raise ValueError('Postać nie ma pola age.')
        return replace_span(text,rec['start']+m.start(1),rec['start']+m.end(1),value)
    if field=='exp':
        if not str(value).isdigit() or not 0<=int(value)<=9:raise ValueError('Doświadczenie 0–9.')
        matches=list(re.finditer(r'(?im)^[ \t]*unit[ \t]+([^\r\n]+)',part))
        if not 0<=unit_index<len(matches):raise ValueError('Brak oddziału o tym numerze.')
        line=matches[unit_index]
        exp=re.search(r'\bexp[ \t]+(\d+)',line.group(1))
        if not exp:raise ValueError('Oddział bez pola exp.')
        off=rec['start']+line.start(1)
        return replace_span(text,off+exp.start(1),off+exp.end(1),value)
    raise ValueError('Nieobsługiwane pole postaci.')

def playable_factions(text):
    result={}
    for label in ('playable','unlockable','nonplayable'):
        m=re.search(r'(?im)^[ \t]*'+label+r'[ \t]*\r?\n(.*?)^[ \t]*end[ \t]*\r?$',text,re.S|re.M)
        if m:
            for f in re.findall(r'(?m)^[ \t]*([a-z_]+)[ \t]*\r?$',m.group(1)):result[f]=label
    return result

def edit_playability(text,faction,destination):
    if destination not in ('playable','unlockable','nonplayable'):raise ValueError('Nieznany typ grywalności.')
    if faction not in playable_factions(text):raise ValueError('Frakcja nie znajduje się na listach grywalności.')
    if faction=='slave':raise ValueError('Buntownicy nie są typową frakcją grywalną.')
    newline='\r\n' if '\r\n' in text else '\n'
    source=playable_factions(text)[faction]
    if source==destination:return text
    def block_match(txt,label):
        return re.search(r'(?im)^[ \t]*'+label+r'[ \t]*\r?\n(.*?)^[ \t]*end[ \t]*\r?$',txt,re.S|re.M)
    m=block_match(text,source)
    lines=m.group(1).splitlines(keepends=True)
    lines=[line for line in lines if line.strip()!=faction]
    text=replace_span(text,m.start(1),m.end(1),''.join(lines))
    m=block_match(text,destination)
    return replace_span(text,m.end(1),m.end(1),'\t'+faction+newline)

def relationships(text):
    return [(m.group(1),m.group(2),m.group(3)) for m in re.finditer(r'(?im)^[ \t]*faction_relationships[ \t]+([a-z_]+)[ \t]*,[ \t]*(at_war_with|allied_to)[ \t]+([^\r\n;]+)',text)]

def edit_relationship(text,source,target,kind):
    if source==target:raise ValueError('Nie można ustalić relacji frakcji z samą sobą.')
    if kind not in ('at_war_with','allied_to'):raise ValueError('Dozwolone: wojna lub sojusz.')
    if source not in dict((x[0],1) for x in faction_blocks(text)) or target not in dict((x[0],1) for x in faction_blocks(text)):
        raise ValueError('Nieznana frakcja.')
    # Only replace relationship if target occurs as a sole element, to avoid damaging lists.
    pat=r'(?im)^([ \t]*faction_relationships[ \t]+'+re.escape(source)+r'[ \t]*,[ \t]*)(at_war_with|allied_to)([ \t]+)('+re.escape(target)+r')([ \t]*)(?=\r?$)'
    m=re.search(pat,text)
    if m:return replace_span(text,m.start(2),m.end(2),kind)
    newline='\r\n' if '\r\n' in text else '\n'
    return text.rstrip('\r\n')+newline+f'faction_relationships\t{source}, {kind}\t{target}'+newline

def unit_stats(text):
    matches=list(TYPES.finditer(text));out=[]
    for i,m in enumerate(matches):
        block=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
        stats={}
        for key in ('stat_cost','stat_pri','stat_sec','stat_mental','stat_ownership'):
            mm=re.search(r'(?im)^'+key+r'[ \t]+([^\r\n;]+)',block)
            if mm:stats[key]=mm.group(1).strip()
        out.append((m.group(1).strip(),stats))
    return out

def edit_unit_stat(text,unit,field,index,value):
    if field not in ('stat_cost','stat_pri','stat_sec','stat_mental'):
        raise ValueError('Nieobsługiwane pole EDU.')
    if not str(value).isdigit() or not 0<=int(value)<=10000000:raise ValueError('Oczekiwana liczba 0–10 000 000.')
    matches=list(TYPES.finditer(text));hit=None;end=None
    for i,m in enumerate(matches):
        if m.group(1).strip()==unit:
            hit=m;end=matches[i+1].start() if i+1<len(matches) else len(text);break
    if hit is None:raise ValueError('Nie znaleziono jednostki.')
    m=re.search(r'(?im)^([ \t]*'+field+r'[ \t]+)([^\r\n;]+)',text[hit.end():end])
    if not m:raise ValueError('Brak statystyki '+field)
    fields=m.group(2).split(',')
    if not 0<=index<len(fields):raise ValueError('Nie ma takiego indeksu pola.')
    fields[index]=re.match(r'\s*',fields[index]).group()+str(value)
    return replace_span(text,hit.end()+m.start(2),hit.end()+m.end(2),','.join(fields))
