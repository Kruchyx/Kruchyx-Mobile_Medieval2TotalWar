"""New approachable Medieval Premium views for v0.9.1. Pure Tkinter.
Read-only campaign recommendations + source-grounded offline Academy.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import webbrowser
from academy_content import LESSONS, FIRST_TURNS, SOURCES, GLOSSARY, L, pick, advice_for_faction, building_tip, battle_tip, TURN_PLAN
from campaign_intelligence import inspect_campaign, economy_ranking, detect_findings, merchant_insights, diplomacy_advice
from mod_insights import pretty,pretty_lang

BG='#0c1116';SIDE='#10191e';PANEL='#172129';PANEL2='#1d2a30';GOLD='#d4af72';GOLD_BRIGHT='#f0cd91';INK='#efeadf';MUTED='#a3b2b8';EMERALD='#70c7ad';RED='#e4a39b';EDGE='#37434a';FONT='Segoe UI'

def S(lang,pl,en):return en if lang=='en' else pl

def page_academy(a,root):
    lang=a.lang
    a.heading(root,S(lang,'Akademia dla początkujących','New Player Academy'),
              S(lang,'Naucz się Medieval II krok po kroku','Learn Medieval II step by step'),
              S(lang,'Od pierwszej tury do ofensywy, gospodarki, dyplomacji i cheatów. Bez technicznego żargonu.','From your first turn to economy, warfare, diplomacy and cheats — no technical jargon.'))
    a.hero(root,S(lang,'Twoja pierwsza kampania','Your first campaign'),
                S(lang,'Wybierz temat. Naucz się na przykładach, a potem przejdź do gry.','Choose a topic, learn by example, then put it into practice in game.'))
    completed=sum(bool(a.completed.get(str(i))) for i in range(len(FIRST_TURNS)))
    progress,pc=a.card(root,pad=17);progress.pack(fill='x',pady=(0,15))
    row=tk.Frame(pc,bg=PANEL);row.pack(fill='x')
    a.lbl(row,S(lang,'PIERWSZA TURA — LISTA KONTROLNA','FIRST TURN — CHECKLIST'),13,GOLD_BRIGHT,'bold',PANEL).pack(side='left')
    a.lbl(row,f'{completed}/{len(FIRST_TURNS)}',13,EMERALD,'bold',PANEL).pack(side='right')
    a.btn(pc,S(lang,'ZACZNIJ OD NOWA','RESET CHECKLIST'),lambda:reset_progress(a),variant='ghost',small=True).pack(anchor='e',pady=(5,0))
    gauge=tk.Frame(pc,bg='#334047',height=9);gauge.pack(fill='x',pady=(11,17))
    tk.Frame(gauge,bg=GOLD,height=9).place(relx=0,rely=0,relwidth=completed/len(FIRST_TURNS),relheight=1)
    grid=tk.Frame(pc,bg=PANEL);grid.pack(fill='x')
    for i,pair in enumerate(FIRST_TURNS):
        text=('✓  ' if a.completed.get(str(i)) else '○  ')+L(pair,lang)
        button=a.btn(grid,text,lambda idx=i:toggle_task(a,idx),variant='green' if a.completed.get(str(i)) else 'ghost',small=True)
        button.grid(row=i//2,column=i%2,sticky='ew',padx=4,pady=4)
    for c in range(2):grid.columnconfigure(c,weight=1)
    a.section(root,S(lang,'Plan pierwszych 20 tur','Your first 20 turns'))
    phases=tk.Frame(root,bg=BG);phases.pack(fill='x',pady=(0,7))
    for i,(pl,en,tip_pl,tip_en) in enumerate(TURN_PLAN):
        out,inner=a.card(phases,pad=15)
        out.grid(row=i//2,column=i%2,sticky='nsew',padx=5,pady=5)
        a.lbl(inner,en if lang=='en' else pl,13,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
        a.lbl(inner,tip_en if lang=='en' else tip_pl,10,INK,bg=PANEL,wraplength=370,justify='left').pack(anchor='w',pady=(8,0))
    for c in range(2):phases.columnconfigure(c,weight=1)
    a.section(root,S(lang,'Wybierz lekcję','Choose a lesson'))
    tiles=tk.Frame(root,bg=BG);tiles.pack(fill='x')
    for i,lesson in enumerate(LESSONS):
        lid,icon,titles,subtitle,steps,mistake,src=lesson
        b=a.btn(tiles,f'{icon}  {L(titles,lang)}',lambda key=lid:select_lesson(a,key),
                variant='gold' if lid==a.current_lesson else 'dark',small=True)
        b.grid(row=i//3,column=i%3,sticky='ew',padx=4,pady=5)
    for col in range(3):tiles.columnconfigure(col,weight=1)
    a.section(root,S(lang,'Lekcja i praktyczne kroki','Lesson and actionable steps'))
    lesson=pick(a.current_lesson) or LESSONS[0]
    lid,icon,titles,subtitle,steps,mistake,source=lesson
    outer,ci=a.card(root,pad=24);outer.pack(fill='x')
    a._academy_anchor=outer
    a.lbl(ci,f'{icon}  {L(titles,lang)}',19,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
    a.lbl(ci,L(subtitle,lang),12,MUTED,bg=PANEL,wraplength=870,justify='left').pack(anchor='w',pady=(8,17))
    for index,pair in enumerate(steps,1):
        row=tk.Frame(ci,bg=PANEL);row.pack(fill='x',pady=6)
        badge=tk.Label(row,text=f'{index:02}',fg='#161b1c',bg=GOLD,font=(FONT,11,'bold'),padx=9,pady=5)
        badge.pack(side='left',anchor='n',padx=(0,14))
        a.lbl(row,L(pair,lang),11,INK,bg=PANEL,wraplength=815,justify='left',anchor='w').pack(side='left',fill='x',expand=True)
    caution=tk.Frame(ci,bg='#372d29',padx=13,pady=13);caution.pack(fill='x',pady=(18,0))
    a.lbl(caution,('⚠  '+S(lang,'TYPOWY BŁĄD','COMMON MISTAKE')),10,GOLD_BRIGHT,'bold','#372d29').pack(anchor='w')
    a.lbl(caution,L(mistake,lang),11,INK,bg='#372d29',wraplength=850,justify='left').pack(anchor='w',pady=(6,0))
    ref={'manual':0,'strategy':0,'cheats':2,'modding':3}.get(source,0)
    link,li=a.card(root,pad=15);link.pack(fill='x',pady=(12,8))
    a.lbl(li,S(lang,'Podstawa wiedzy','Knowledge base')+': '+SOURCES[ref][0],10,MUTED,bg=PANEL).pack(side='left')
    a.btn(li,S(lang,'OTWÓRZ ŹRÓDŁO','OPEN SOURCE'),lambda url=SOURCES[ref][1]:webbrowser.open(url),variant='dark',small=True).pack(side='right')
    a.section(root,S(lang,'Doradca praktyczny','Practical advisor'))
    box,inn=a.card(root,pad=23);box.pack(fill='x',pady=(0,10))
    a.lbl(inn,S(lang,'Co budować w mojej osadzie?','What should I build?'),14,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
    controls=tk.Frame(inn,bg=PANEL);controls.pack(fill='x',pady=12)
    kind=tk.StringVar(value='city');goal=tk.StringVar(value='income')
    for var,options in ((kind,[('city',S(lang,'Miasto','City')),('castle',S(lang,'Zamek','Castle'))]),
                        (goal,[('income',S(lang,'Dochody','Income')),('growth',S(lang,'Rozwój','Growth')),('defense',S(lang,'Obrona','Defense'))])):
        cb=ttk.Combobox(controls,values=[label for _,label in options],state='readonly',style='Premium.TCombobox',width=22)
        cb.current(0);cb.pack(side='left',padx=(0,10))
        var.set(options[0][0])
        cb.bind('<<ComboboxSelected>>',lambda e,v=var,opts=options,w=cb:v.set(opts[w.current()][0]))
    advice_label=a.lbl(inn,'',11,INK,bg=PANEL,wraplength=900,justify='left');advice_label.pack(anchor='w',pady=(5,7))
    def refresh_build(*_):advice_label.configure(text=building_tip(kind.get(),goal.get(),lang))
    kind.trace_add('write',refresh_build);goal.trace_add('write',refresh_build);refresh_build()
    bouter,binn=a.card(root,pad=22);bouter.pack(fill='x',pady=(0,10))
    a.lbl(binn,S(lang,'Przeciwnik na polu bitwy','Enemy on the battlefield'),14,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
    opponents=[('cavalry',S(lang,'Kawaleria wroga','Enemy cavalry')),('infantry',S(lang,'Ciężka piechota','Heavy infantry')),
               ('missiles',S(lang,'Strzelcy','Missile troops')),('siege',S(lang,'Oblężenie','Siege'))]
    enemy=tk.StringVar(value='cavalry')
    opp=ttk.Combobox(binn,values=[label for _,label in opponents],style='Premium.TCombobox',state='readonly',width=31)
    opp.current(0);opp.pack(anchor='w',pady=11)
    tactic=a.lbl(binn,battle_tip(enemy.get(),lang),11,INK,bg=PANEL,wraplength=870,justify='left');tactic.pack(anchor='w',pady=6)
    def switch_enemy(_):enemy.set(opponents[opp.current()][0]);tactic.configure(text=battle_tip(enemy.get(),lang))
    opp.bind('<<ComboboxSelected>>',switch_enemy)
    if a.model and a.model.get('factions'):
        a.section(root,S(lang,'Rady dla wybranej frakcji','Advice for the selected faction'))
        outer,ci=a.card(root,pad=18);outer.pack(fill='x')
        fs=[x for x in a.model['factions'] if x['name'] not in ('slave',) and x.get('playable') is not False]
        ids=[x['name'] for x in fs]
        current=a.selected_faction if a.selected_faction in ids else ids[0]
        names=[pretty_lang(x['name'],lang) for x in fs]
        selector=ttk.Combobox(ci,values=names,state='readonly',style='Premium.TCombobox',width=40)
        selector.current(ids.index(current));selector.pack(anchor='w',pady=(0,12))
        area=tk.Frame(ci,bg=PANEL);area.pack(fill='x')
        def paint_faction(_=None):
            a.selected_faction=ids[selector.current()]
            for w in area.winfo_children():w.destroy()
            selected_campaign=a.model['context']['files'].get('campaign')
            all_tips=advice_for_faction(a.model,a.selected_faction,lang)
            if selected_campaign:
                all_tips+=diplomacy_advice(inspect_campaign(selected_campaign),a.selected_faction,lang)
            for tip,source in all_tips:
                line=tk.Frame(area,bg=PANEL);line.pack(fill='x',pady=5)
                a.lbl(line,'◆',11,GOLD,bg=PANEL).pack(side='left',padx=(0,10))
                a.lbl(line,tip+f'   [{source}]',10,INK,bg=PANEL,wraplength=790,justify='left').pack(side='left')
        selector.bind('<<ComboboxSelected>>',paint_faction);paint_faction()
    a.section(root,S(lang,'Słowniczek gracza','Player glossary'))
    gl,gi=a.card(root,pad=18);gl.pack(fill='x')
    for label,definition in GLOSSARY:
        row=tk.Frame(gi,bg=PANEL);row.pack(fill='x',pady=5)
        a.lbl(row,label,10,GOLD_BRIGHT,'bold',PANEL,width=25,anchor='w').pack(side='left')
        a.lbl(row,L(definition,lang),10,INK,bg=PANEL,wraplength=700,justify='left').pack(side='left')
    a.section(root,S(lang,'Zrób następny krok','Take the next step'))
    actions=tk.Frame(root,bg=BG);actions.pack(fill='x',pady=(0,20))
    a.btn(actions,S(lang,'POKAŻ DORADCĘ FRAKCJI','OPEN FACTION ADVISOR'),lambda:a.show('advisor')).pack(side='left',padx=(0,9))
    a.btn(actions,S(lang,'OTWÓRZ CHEAT MENU','OPEN CHEAT MENU'),lambda:a.show('trainer'),variant='dark').pack(side='left')
    a.btn(actions,S(lang,'SEKRETY I EXPLOITY','SECRETS & EXPLOITS'),lambda:a.show('exploits'),variant='dark').pack(side='left',padx=8)


def reset_progress(a):
    a.completed={}
    a._persist()
    a.show('academy')

def toggle_task(a,index):
    a.completed[str(index)]=not bool(a.completed.get(str(index)))
    a._persist();a.show('academy')

def select_lesson(a,lesson_id):
    a.current_lesson=lesson_id
    a.show('academy')
    # Keep the chosen content in view instead of jumping back to dashboard top.
    def scroll_to_lesson():
        anchor=getattr(a,'_academy_anchor',None)
        if anchor and anchor.winfo_exists():
            a.update_idletasks()
            distance=anchor.winfo_rooty()-a.body.winfo_rooty()
            total=max(1,a.body.winfo_reqheight()-a.canvas.winfo_height())
            a.canvas.yview_moveto(max(0,min(1,distance/total)))
    a.after_idle(scroll_to_lesson)


def page_economy(a,root):
    lang=a.lang
    a.heading(root,S(lang,'Strategia gospodarcza','Economic strategy'),
              S(lang,'Która frakcja ma najlepszy start?','Which faction has the strongest start?'),
              S(lang,'Rzeczywisty skarbiec, osady i populacja z pliku kampanii — bez zgadywania dochodu na turę.',
                'Treasury, settlements and population from campaign data — without guessing income per turn.'))
    if not a.model:a._need_mod(root);return
    f=a.model['context']['files'];context=a.model['context']
    if context['campaigns']:
        co,ci=a.card(root,pad=16);co.pack(fill='x',pady=(0,12))
        a.lbl(ci,S(lang,'AKTYWNA KAMPANIA','ACTIVE CAMPAIGN'),11,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
        choices=[p.parent.name for p in context['campaigns']]
        current=f.get('campaign')
        selector=ttk.Combobox(ci,values=choices,state='readonly',style='Premium.TCombobox',width=46)
        selector.current(context['campaigns'].index(current) if current in context['campaigns'] else 0)
        selector.pack(anchor='w',pady=(9,0))
        def change(_):a.change_campaign(context['campaigns'][selector.current()])
        selector.bind('<<ComboboxSelected>>',change)
    if not f.get('campaign'):
        co,ci=a.card(root,pad=25);co.pack(fill='x')
        a.lbl(ci,S(lang,'Brakuje descr_strat.txt','descr_strat.txt is missing'),17,RED,'bold',PANEL).pack(anchor='w')
        a.lbl(ci,S(lang,'Nie można wyznaczyć potencjału gospodarczego na podstawie samego EDU. Wybierz folder zawierający kampanię.',
                        'Economic start analysis requires a campaign file, not just EDU. Select a mod containing campaign data.'),11,MUTED,bg=PANEL,wraplength=850).pack(anchor='w',pady=8)
        a.btn(ci,S(lang,'AKADEMIA: EKONOMIA','ACADEMY: ECONOMY'),lambda:_show_economy_lesson(a),variant='dark').pack(anchor='w',pady=10)
        return
    data=inspect_campaign(f['campaign']);ranked=economy_ranking(data)
    if not ranked:
        outer,ci=a.card(root);outer.pack(fill='x')
        a.lbl(ci,S(lang,'Brak porównywalnych danych finansowych w kampanii.','No comparable treasury data found in campaign.'),12,RED,bg=PANEL).pack()
        return
    a.section(root,S(lang,'Ranking potencjału gospodarczego na starcie','Initial economic potential ranking'))
    msg=S(lang,'Indeks porównawczy: 30% skarbiec, 30% liczba osad, 25% populacja, 15% miasta. Nie jest to dochód/turę, a miasta i zamki mogą mieć inne możliwości. Nie uwzględnia handlu i budynków bez dalszych danych.',
          'Comparison index: 30% treasury, 30% settlements, 25% population, 15% cities. NOT income per turn, and cities/castles have different benefits. Trade and building effects are not modeled.')
    n,ci=a.card(root,pad=13,bg='#2d2a23');n.pack(fill='x',pady=(0,15))
    a.lbl(ci,msg,10,INK,bg='#2d2a23',wraplength=900,justify='left').pack(anchor='w')
    for i,x in enumerate(ranked[:12],1):
        outer,ci=a.card(root,pad=14);outer.pack(fill='x',pady=5)
        row=tk.Frame(ci,bg=PANEL);row.pack(fill='x')
        a.lbl(row,f'{i:02}   {pretty_lang(x["name"],lang)}',14,GOLD_BRIGHT,'bold',PANEL).pack(side='left')
        a.lbl(row,f'{x["score"]:.1f} / 100',12,EMERALD,'bold',PANEL).pack(side='right')
        bar=tk.Frame(ci,bg='#344049',height=6);bar.pack(fill='x',pady=9)
        tk.Frame(bar,bg=GOLD,height=6).place(relx=0,rely=0,relwidth=x['score']/100,relheight=1)
        detail=(f"Treasury: {x['money']:,} fl.  ·  Settlements: {len(x['settlements'])}  ·  Cities: {x['city_count']}  ·  Castles: {x['castle_count']}  ·  Pop.: {x['total_population']:,}" if lang=='en' else
                f"Skarbiec: {x['money']:,} fl.  ·  Osady: {len(x['settlements'])}  ·  Miasta: {x['city_count']}  ·  Zamki: {x['castle_count']}  ·  Ludność: {x['total_population']:,}")
        a.lbl(ci,detail,10,MUTED,bg=PANEL).pack(anchor='w')
    a.section(root,S(lang,'Warto wiedzieć','Useful context'))
    n,ci=a.card(root,pad=18);n.pack(fill='x')
    for line in [S(lang,'• Miasta zwykle oferują lepszy handel i podatki, zamki lepszą produkcję wojsk.',
                   '• Cities tend to have stronger trade/tax options; castles are military centers.'),
                 S(lang,'• Sprawdź dostęp do kopalń, portów, dróg i źródeł handlu w rzeczywistej grze.',
                   '• Check mines, ports, roads and trade routes in the actual game.'),
                 S(lang,'• Obecny ranking nie zna rzeczywistego salda, wojen ani podatków z późniejszych tur.',
                   '• This ranking cannot know future-turn balance, wars or taxes.')]:
        a.lbl(ci,line,11,INK,bg=PANEL,wraplength=870,justify='left').pack(anchor='w',pady=5)
    a.btn(root,S(lang,'NAUCZ SIĘ ZARZĄDZAĆ GOSPODARKĄ','LEARN ECONOMY BASICS'),lambda:_show_economy_lesson(a),variant='gold').pack(anchor='w',pady=18)

def _show_economy_lesson(a):a.current_lesson='economy';a.show('academy')


def page_intelligence(a,root):
    lang=a.lang
    a.heading(root,S(lang,'Kruchyx Intelligence','Kruchyx Intelligence'),
              S(lang,'Okazje, kupcy i kontrola błędów','Opportunities, merchants & bug checks'),
              S(lang,'Wszystkie odkrycia zawierają źródło i poziom pewności. To nie jest odczyt aktywnego zapisu gry.',
                'Every finding lists its source and confidence. This is not a reading of your live save.'))
    if not a.model:a._need_mod(root);return
    model=a.model;context=model['context'];files=context['files']
    data=inspect_campaign(files['campaign'])
    findings=detect_findings(context,data)
    a.section(root,S(lang,'Wykryte wskazówki','Detected leads'))
    if not findings:
        a.lbl(root,S(lang,'Brak znalezisk przy obecnym zestawie plików.','No findings with current files.'),12,MUTED).pack(anchor='w')
    for obj in findings:
        background={'confirmed':'#202f2b','potential':'#302c22','requires_test':'#302c22'}.get(obj['confidence'],'#25282b')
        outer,ci=a.card(root,pad=17,bg=background);outer.pack(fill='x',pady=6)
        badge={'confirmed':S(lang,'POTWIERDZONE W PLIKACH','FILE-CONFIRMED'),
               'potential':S(lang,'POTENCJALNA OKAZJA','POTENTIAL LEAD')}.get(obj['confidence'],S(lang,'WYMAGA TESTU','NEEDS TEST'))
        a.lbl(ci,('◆  '+L(obj['title'],lang)).upper(),12,GOLD_BRIGHT,'bold',background).pack(anchor='w')
        a.lbl(ci,L(obj['body'],lang),11,INK,bg=background,wraplength=880,justify='left').pack(anchor='w',pady=9)
        a.lbl(ci,badge+'   ·   '+(obj['source'] or S(lang,'Nieznane źródło','Unknown source')),9,MUTED,bg=background,wraplength=875,justify='left').pack(anchor='w')
    a.section(root,S(lang,'Szukanie okazji u kupców','Merchant opportunities'))
    outer,ci=a.card(root,pad=18);outer.pack(fill='x')
    a.lbl(ci,S(lang,'Zasoby o najwyższej wartości handlowej','Highest trade-value resources'),14,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
    for tip,tag in merchant_insights(model['resources'],lang):
        a.lbl(ci,'◇  '+tip,10,INK,bg=PANEL).pack(anchor='w',pady=4)
    a.lbl(ci,S(lang,'Kupiec zarabia na surowcu, ale jego dochód zależy też od finansów, odległości od stolicy i praw handlowych. Nie obiecujemy automatycznych exploitów.',
                   'Merchants trade resources, but income also depends on skill, distance to capital and trade rights. No exploit is promised.'),10,MUTED,bg=PANEL,wraplength=880,justify='left').pack(anchor='w',pady=(12,3))
    a.section(root,S(lang,'Co Kruchyx może wykryć, a czego nie?','What Kruchyx can and cannot detect'))
    outer,ci=a.card(root,pad=17);outer.pack(fill='x')
    rows=[
      (True,S(lang,'Dane startowe osad, frakcji i skarbca','Initial settlements, factions and treasury')),
      (True,S(lang,'Wartości zasobów i nietypowe definicje rekrutacji','Trade values and suspicious recruitment definitions')),
      (False,S(lang,'Garnizon automatycznie wygenerowany w grze','Garrisons generated by the game engine')),
      (False,S(lang,'Bieżąca pozycja kupców i stan późniejszych tur','Current merchants and later-turn save state')),
      (False,S(lang,'Wynik exploitu w twojej wersji moda — wymaga testu','Actual exploit behavior in your mod version — needs testing'))]
    for yes,msg in rows:a.status(ci,yes,msg,S(lang,'Dane startowe / pliki moda' if yes else 'Wymaga weryfikacji w rozgrywce',
                                      'Initial configuration / mod files' if yes else 'Requires in-game verification'))
    a.btn(root,S(lang,'OTWÓRZ PORADNIK O MODACH','OPEN MODDING GUIDE'),lambda:_show_mods_lesson(a),variant='dark').pack(anchor='w',pady=18)

def _show_mods_lesson(a):a.current_lesson='mods';a.show('academy')
