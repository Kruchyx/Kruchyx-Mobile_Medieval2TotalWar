# -*- coding: utf-8 -*-
"""Kruchyx v0.9.5: offline companion data, event scanner and Tkinter pages.
No game process manipulation and no modifications of mod files.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
import json,re,tkinter as tk
from tkinter import ttk,filedialog,messagebox
from mod_insights import pretty_lang

ROOT=Path(__file__).resolve().parent
KNOWLEDGE=ROOT/'shared'/'knowledge_v095.json'
GOLD='#d4af72';INK='#efeadf';MUTED='#a3b2b8';PANEL='#172129';BG='#0c1116'

def knowledge():
    data=json.loads(KNOWLEDGE.read_text(encoding='utf-8'))
    if data.get('schema')!='kruchyx-knowledge-v1':raise ValueError('Nieprawidłowa baza wiedzy')
    return data

def read_event_ranges(text):
    """Parse 'event ... id' followed by 'date N [M]' ignoring comments.
    Values are *in-game years from campaign start*, not turn indices.
    """
    blocks=[];current=None
    for line in text.splitlines():
        line=line.split(';',1)[0].strip()
        if not line:continue
        match=re.match(r'^event\s+\w+\s+([\w.-]+)(?:\s|$)',line,re.I)
        if match:
            current=match.group(1).lower();continue
        date=re.match(r'^date\s+(-?\d+)(?:\s+(-?\d+))?(?:\s|$)',line,re.I)
        if current and date:
            a=int(date.group(1)); b=int(date.group(2) or date.group(1))
            blocks.append((current,min(a,b),max(a,b)))
            current=None
    return {key:(a,b) for key,a,b in blocks}

def find_descr_events(folder):
    if folder is None:return None
    p=Path(folder)
    if p.is_file():p=p.parent
    look=[p/'descr_events.txt',p/'data'/'world'/'maps'/'campaign'/'imperial_campaign'/'descr_events.txt',
          p/'world'/'maps'/'campaign'/'imperial_campaign'/'descr_events.txt',
          p/'data'/'world'/'maps'/'campaign'/'descr_events.txt',p.parent/'descr_events.txt']
    for prefix in (p/'data'/'world'/'maps'/'campaign',p/'world'/'maps'/'campaign'):
        if prefix.is_dir():look.extend(sorted(prefix.glob('*/descr_events.txt'))[:25])
    return next((x for x in look if x.is_file()),None)

def derived_events(folder=None, years_per_turn=2):
    """Returns (rows, source, from_file). Date offsets converted conservatively.
    No invasion spawn dates are invented from warning events.
    """
    rows=[dict(item) for item in knowledge()['events']]
    source=find_descr_events(folder)
    if source:
        try:
            raw=source.read_bytes()
            try:txt=raw.decode('utf-8-sig')
            except UnicodeDecodeError:txt=raw.decode('cp1250',errors='replace')
            ranges=read_event_ranges(txt)
            for row in rows:
                if row['id'] in ranges:
                    first,last=ranges[row['id']]
                    row['turn_from']=max(0,first//years_per_turn)
                    row['turn_to']=max(0,(last+years_per_turn-1)//years_per_turn)
                    row['confidence']='file'
                else:
                    row['confidence']='not_found'
        except OSError:
            source=None
    return rows,str(source) if source else 'Vanilla: wartości orientacyjne',bool(source)

def companion_report(model,mod_label,folder=None):
    data=knowledge()
    events,source,_=derived_events(folder)
    units=[];factions=[]
    if model:
        for u in model.get('units',[]):
            if u.get('general'):continue
            units.append({k:u.get(k) for k in ['name','role','owners','attack','defence','charge','morale','cost','upkeep','score']})
        for f in model.get('factions',[]):
            factions.append({'name':f.get('name',''),'score':f.get('score',0),'unit_count':f.get('count',0)})
    return {
        'schema':'kruchyx-companion-v1','version':'0.9.5',
        'created_at':datetime.now(timezone.utc).isoformat(),
        'mod':str(mod_label),'source':'Analiza lokalnego EDU i plików kampanii; ranking heurystyczny',
        'events_source':source,'years_per_turn_assumed':2,
        'events':events,'units':units,'factions':factions,
        'disclaimer':data['disclaimer']}

def export_companion(app):
    label=(app.active_path.name if app.active_path else 'Vanilla - dane przykładowe')
    path=filedialog.asksaveasfilename(parent=app,title='Eksport raportu do Kruchyx Mobile',
         initialfile='Kruchyx_Mobile_Raport.json',defaultextension='.json',filetypes=[('Kruchyx JSON','*.json')])
    if not path:return
    try:
        report=companion_report(app.model,label,app.active_path)
        Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    except (OSError,ValueError,TypeError) as exc:messagebox.showerror('Eksport',str(exc),parent=app)
    else:messagebox.showinfo('Gotowe',f'Raport JSON gotowy:\n{path}\n\nMożesz skopiować plik na telefon i wczytać go w Kruchyx Mobile.',parent=app)

def _textbox(parent,rows=8):
    t=tk.Text(parent,height=rows,bg='#1d2a30',fg=INK,insertbackground=GOLD,relief='flat',
              padx=16,pady=12,wrap='word',font=('Segoe UI',11),state='disabled')
    t.pack(fill='x',pady=(6,13));return t

def _display(box,text):
    box.configure(state='normal');box.delete('1.0','end');box.insert('1.0',text);box.configure(state='disabled')

def page_chronicles(app,parent):
    app.heading(parent,'Kroniki v0.9.5' if app.lang=='pl' else 'Chronicles v0.9.5',
                'Kalendarz wydarzeń kampanii' if app.lang=='pl' else 'Campaign event calendar',
                'Odczyt z descr_events.txt; gdy brak pliku pokazujemy orientacyjne wartości Vanilla. Skala: 2 lata/tura.')
    rows,source,found=derived_events(app.active_path)
    app.lbl(parent,('Źródło: '+source),10,GOLD if found else MUTED,wraplength=900).pack(anchor='w',pady=(0,12))
    controls=tk.Frame(parent,bg=BG);controls.pack(fill='x',pady=5)
    app.lbl(controls,'Aktualna tura:',11,INK).pack(side='left',padx=(0,10))
    current=tk.IntVar(value=60)
    spin=tk.Spinbox(controls,from_=1,to=300,textvariable=current,width=7,bg='#1d2a30',fg=INK,
                   insertbackground=GOLD,buttonbackground='#304148',font=('Segoe UI',12))
    spin.pack(side='left',padx=(0,12))
    table=ttk.Treeview(parent,columns=('turns','distance','origin'),show='headings',height=6,style='Premium.Treeview')
    for name,label,width in [('turns','Tury',125),('distance','Względem obecnej tury',225),('origin','Źródło danych',205)]:
        table.heading(name,text=label);table.column(name,width=width,anchor='w')
    table.column('#1',width=120)
    table.configure(columns=('event','turns','distance','origin'))
    table.heading('event',text='Wydarzenie');table.column('event',width=260)
    table.pack(fill='x',pady=10)
    info=_textbox(parent,8)
    def refresh(*args):
        try:now=int(current.get())
        except (tk.TclError,ValueError):now=1
        table.delete(*table.get_children())
        for ix,e in enumerate(rows):
            first,last=e['turn_from'],e['turn_to']
            distance=(f'za {first-now}–{last-now} tur' if now<first else
                      'trwa przedział' if now<=last else 'przedział minął')
            source_label={'file':'plik moda','not_found':'brak wpisu w modzie','vanilla':'Vanilla – przykład'}.get(e['confidence'],'Vanilla')
            table.insert('', 'end',iid=str(ix),values=(e['title'],f'{first}–{last}',distance,source_label))
    def selected(evt=None):
        sel=table.selection()
        if not sel:return
        e=rows[int(sel[0])]
        _display(info,f"{e['title']}  |  okno tur: {e['turn_from']}–{e['turn_to']}\n\n{e['after']}\n\nRADA: {e['advice']}\n\nŹRÓDŁO: {e['source']}\n\nUWAGA: Wydarzenie ostrzegawcze nie oznacza tury spawnu armii. Dane z pliku nie gwarantują odpalenia skryptu.")
    table.bind('<<TreeviewSelect>>',selected)
    app.btn(controls,'PRZELICZ',refresh,variant='dark',small=True).pack(side='left')
    refresh();table.selection_set('0');selected()
    app.section(parent,'Pamiętaj: wydarzenie ≠ rzeczywisty najazd')
    app.lbl(parent,'Dla Mongołów i Timurydów moment pojawienia się armii zależy także od campaign_script.txt. Możliwa jest inna skala czasu w modzie.',10,MUTED,wraplength=960,justify='left').pack(anchor='w')

def page_army_builder(app,parent):
    app.heading(parent,'Warsztat wojskowy v0.9.5','Kreator armii — maks. 20 oddziałów',
                'Dobierz wojska z faktycznego EDU aktywnego moda. Koszty to wartości z pliku, bez dynamicznych premii kampanii.')
    if not app.model:
        app._need_mod(parent);return
    facs=[f['name'] for f in app.model.get('factions',[]) if f.get('name')]
    if not facs:app._need_mod(parent,'Brak danych EDU.');return
    top=tk.Frame(parent,bg=BG);top.pack(fill='x',pady=10)
    app.lbl(top,'Frakcja:',11,INK).pack(side='left',padx=(0,8))
    faction=tk.StringVar(value=facs[0])
    chooser=ttk.Combobox(top,textvariable=faction,values=facs,state='readonly',style='Premium.TCombobox',width=23)
    chooser.pack(side='left',padx=(0,12))
    selected_units=[]
    unit_by_name={u['name']:u for u in app.model['units'] if not u.get('general') and u.get('role')!='Okręty'}
    name_var=tk.StringVar()
    unit_select=ttk.Combobox(top,textvariable=name_var,state='readonly',style='Premium.TCombobox',width=43)
    unit_select.pack(side='left',padx=(0,8))
    app.btn(top,'+ DODAJ',lambda:add_unit(),variant='gold',small=True).pack(side='left')
    listing=tk.Listbox(parent,bg=PANEL,fg=INK,selectbackground='#5b4b32',font=('Segoe UI',11),
                     height=14,highlightthickness=0,relief='flat',activestyle='none')
    listing.pack(fill='x',pady=(10,5))
    summary=app.lbl(parent,'',11,GOLD,wraplength=900)
    summary.pack(anchor='w',pady=(3,10))
    def update_available(evt=None):
        relevant=sorted(n for n,u in unit_by_name.items() if faction.get() in u.get('owners',[]))
        unit_select.configure(values=relevant);name_var.set(relevant[0] if relevant else '')
        selected_units.clear();refresh()
    def refresh():
        listing.delete(0,'end')
        for i,u in enumerate(selected_units):
            listing.insert('end',f"{i+1:02}. {u['name']}  |  {u['role']}  |  rekrutacja {int(u['cost'] or 0)}  |  utrzymanie {int(u['upkeep'] or 0)}")
        cost=sum(int(u.get('cost') or 0) for u in selected_units)
        upkeep=sum(int(u.get('upkeep') or 0) for u in selected_units)
        counts={x['role']:sum(y['role']==x['role'] for y in selected_units) for x in selected_units}
        roles=' | '.join(f'{k}: {v}' for k,v in counts.items())
        summary.configure(text=f'{len(selected_units)}/20 slotów   •   Koszt rekrutacji: {cost:,} fl.   •   Utrzymanie/tura: {upkeep:,} fl.\n{roles}')
    def add_unit():
        if len(selected_units)>=20:messagebox.showwarning('Limit','Armia może mieć maksymalnie 20 oddziałów.',parent=app);return
        u=unit_by_name.get(name_var.get())
        if u and faction.get() in u.get('owners',[]):selected_units.append(u);refresh()
    def remove_unit():
        ix=listing.curselection()
        if ix:selected_units.pop(ix[0]);refresh()
    actions=tk.Frame(parent,bg=BG);actions.pack(anchor='w',pady=5)
    app.btn(actions,'USUŃ ZAZNACZONY',remove_unit,variant='dark',small=True).pack(side='left',padx=(0,10))
    app.btn(actions,'WYCZYŚĆ',lambda:(selected_units.clear(),refresh()),variant='ghost',small=True).pack(side='left',padx=(0,10))
    def copy_army():
        txt=f'Kruchyx — armia {faction.get()}\n'+'\n'.join(f"{i+1}. {u['name']}" for i,u in enumerate(selected_units))+'\n'+summary.cget('text')
        app.clipboard_clear();app.clipboard_append(txt);app.update()
    app.btn(actions,'KOPIUJ PLAN',copy_army,variant='gold',small=True).pack(side='left')
    chooser.bind('<<ComboboxSelected>>',update_available);update_available()
    app.lbl(parent,'Ważne: EDU nie potwierdza, czy masz już odpowiednie budynki do rekrutacji. Ten ekran nie edytuje zapisów gry.',10,MUTED,wraplength=920).pack(anchor='w',pady=12)

def page_search(app,parent):
    app.heading(parent,'Kruchyx v0.9.5','Wyszukiwarka wiedzy','Przeszukuje wydarzenia, exploity i lekcje z bazy offline; działa także bez wybranego moda.')
    data=knowledge();records=[]
    for e in data['events']:records.append(('Kroniki',e['title'],e['after']+'\n'+e['advice']))
    for e in data['exploits']:records.append(('Exploit',e['title'],e['short']+'\n\n'+'\n'.join(f'{i+1}. {x}' for i,x in enumerate(e['steps']))+'\n\nUwaga: '+e['limits']+'\n'+e['source']))
    for e in data['lessons']:records.append(('Akademia',e['title'],e['body']))
    row=tk.Frame(parent,bg=BG);row.pack(fill='x',pady=10)
    search=tk.StringVar();entry=ttk.Entry(row,textvariable=search,style='Premium.TEntry');entry.pack(side='left',fill='x',expand=True,padx=(0,10))
    listing=tk.Listbox(parent,height=12,bg=PANEL,fg=INK,selectbackground='#5b4b32',relief='flat',font=('Segoe UI',11))
    listing.pack(fill='x',pady=(8,8))
    detail=_textbox(parent,11);filtered=[]
    def refresh(*args):
        listing.delete(0,'end');filtered.clear();q=search.get().casefold().strip()
        for group,title,body in records:
            if q in (group+' '+title+' '+body).casefold():
                listing.insert('end',f'[{group}]  {title}');filtered.append((group,title,body))
        if filtered:listing.selection_set(0);select()
        else:_display(detail,'Brak wyników.')
    def select(evt=None):
        ix=listing.curselection()
        if ix:_display(detail,filtered[ix[0]][1]+'\n\n'+filtered[ix[0]][2])
    listing.bind('<<ListboxSelect>>',select)
    search.trace_add('write',refresh);entry.focus_set();refresh()

def page_mobile(app,parent):
    app.heading(parent,'Kruchyx Mobile v0.9.5','Android i iPhone — raport mobilny',
                'Eksportuje bezpieczny, tylko-do-odczytu plik JSON z analizą aktywnego moda i kalendarzem. Import w aplikacji Flutter.')
    co,ci=app.card(parent);co.pack(fill='x',pady=12)
    app.lbl(ci,'1. Wybierz mod lub prezentację na komputerze.',12,INK,'bold',PANEL).pack(anchor='w',pady=5)
    app.lbl(ci,'2. Wyeksportuj Kruchyx_Mobile_Raport.json.',12,INK,'bold',PANEL).pack(anchor='w',pady=5)
    app.lbl(ci,'3. Skopiuj plik na Androida / iPhone’a i wybierz „Importuj raport” w aplikacji mobilnej.',12,INK,'bold',PANEL).pack(anchor='w',pady=5)
    app.btn(ci,'EKSPORTUJ RAPORT NA TELEFON',lambda:export_companion(app),variant='gold').pack(anchor='w',pady=17)
    app.lbl(ci,'Brak automatycznego sterowania działającą grą: v0.9.5 przenosi wyłącznie raporty oraz działa offline.',10,MUTED,bg=PANEL,wraplength=850).pack(anchor='w')
    app.section(parent,'Platformy i wymagania')
    for label,desc in [('Windows','Python + PyInstaller; zbuduj EXE na Windows.'),('Android','Flutter SDK + Android SDK; zbuduj APK na Windows.'),('iPhone','Flutter SDK + Xcode na macOS; podpisany build na iPhone wymaga właściwego zespołu Apple.')]:
        app.lbl(parent,f'{label}: {desc}',11,INK,wraplength=950).pack(anchor='w',pady=8)
