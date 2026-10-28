# -*- coding: utf-8 -*-
"""Kruchyx Medieval Mod Studios v0.9.6 — Grand Compendium.
Standalone Tkinter shell around the existing proven tooling. Fully read-only analytics.
"""
from __future__ import annotations
import json,os,subprocess,sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from mod_insights import analyze, explanation, explanation_en, report, pretty, pretty_lang, ROLES, mod_summary, mod_summary_en, leaders_by_role
from trainer_core import money, unit, building, population, movement, teleport, quick, CommandError
from agent_presets import PRESETS,agent_plan
from game_bridge import paste_to_focused_game
from ui_i18n import tr
from premium_pages import page_academy, page_economy, page_intelligence
from vanilla_support import find_game_root,known_game_locations,list_campaign_choices,is_game_root,unpack_vanilla,find_unpacker,list_packs,vanilla_cache_root
from exploit_pages import page_exploits
from calculator_pages import page_calculators
from vanilla_guide import open_vanilla_guide
from empire_companion import page_chronicles, page_army_builder, page_search, page_mobile

VERSION='0.9.6'
APP='Kruchyx Medieval Mod Studios'
ROOT=Path(__file__).resolve().parent
SETTINGS=Path.home()/'.kruchyx_medieval_mod_studios.json'
# Medieval Premium palette
BG='#0c1116';SIDE='#10191e';PANEL='#172129';PANEL2='#1d2a30';CARD='#19242c';
GOLD='#d4af72';GOLD_BRIGHT='#f0cd91';INK='#efeadf';MUTED='#a3b2b8';FAINT='#65767d';
EDGE='#37434a';EMERALD='#70c7ad';RED='#e4a39b';DARK='#0b1115'
FONT='Segoe UI'


def friendly_file(key):
    return {'edu':'Statystyki jednostek','buildings':'Budynki i rekrutacja',
            'campaign':'Kampania i start frakcji','resources':'Surowce handlowe',
            'traits':'Cechy i agenci','regions':'Regiony i geografia'}.get(key,key)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f'{APP}  •  v{VERSION}  •  Wykonane przez Kruchyx')
        self.geometry('1470x900');self.minsize(1050,680);self.configure(bg=BG)
        try:self.iconbitmap(str(ROOT/'kruchyx.ico'))
        except Exception:pass
        self.option_add('*Font',(FONT,10))
        try:self._prefs=json.loads(SETTINGS.read_text(encoding='utf-8')) if SETTINGS.is_file() else {}
        except (ValueError,OSError):self._prefs={}
        self.lang=self._prefs.get('lang','pl') if self._prefs.get('lang') in ('pl','en') else 'pl'
        self.completed=self._prefs.get('academy_checks',{}) if isinstance(self._prefs.get('academy_checks',{}),dict) else {}
        self.current_lesson='start'
        self._styles();self._images()
        self.model=None;self.active_path=None;self.page='welcome';self.nav={}
        self.current_role='Piechota wręcz';self.selected_faction=None;self.unit_rows=[]
        self.trainer_plan=None
        self._frame_layout()
        self.show('welcome')
        self.after(350,self._autoload)

    def _styles(self):
        s=ttk.Style(self);s.theme_use('clam')
        s.configure('Premium.TCombobox',fieldbackground=PANEL2,background=PANEL2,foreground=INK,
                    arrowcolor=GOLD,bordercolor=EDGE,padding=8,font=(FONT,11))
        s.map('Premium.TCombobox',fieldbackground=[('readonly',PANEL2)],foreground=[('readonly',INK)])
        s.configure('Premium.Treeview',background=PANEL,fieldbackground=PANEL,foreground=INK,
                    borderwidth=0,rowheight=38,font=(FONT,10))
        s.map('Premium.Treeview',background=[('selected','#4c4638')],foreground=[('selected','#ffe8bc')])
        s.configure('Premium.Treeview.Heading',background=PANEL2,foreground=GOLD_BRIGHT,relief='flat',
                    padding=(9,12),font=(FONT,10,'bold'))
        s.map('Premium.Treeview.Heading',background=[('active','#304148')])
        s.configure('Premium.Vertical.TScrollbar',background=PANEL2,arrowcolor=GOLD,troughcolor=BG)
        s.configure('Premium.TEntry',fieldbackground=PANEL2,foreground=INK,bordercolor=EDGE,padding=8,font=(FONT,11))
        s.configure('Premium.TCheckbutton',background=PANEL,foreground=INK,font=(FONT,10))
        s.map('Premium.TCheckbutton',background=[('active',PANEL)])

    def _images(self):
        self.crest=tk.PhotoImage(file=str(ROOT/'assets'/'kruchyx_crest.png'))
        self.banner=tk.PhotoImage(file=str(ROOT/'assets'/'medieval_banner.png'))
        self.divider_image=tk.PhotoImage(file=str(ROOT/'assets'/'divider_gold.png'))

    def _frame_layout(self):
        self.shell=tk.Frame(self,bg=BG);self.shell.pack(fill='both',expand=True)
        self.sidebar=tk.Frame(self.shell,bg=SIDE,width=251)
        self.sidebar.pack(side='left',fill='y');self.sidebar.pack_propagate(False)
        brand=tk.Frame(self.sidebar,bg=SIDE,pady=17);brand.pack(fill='x',padx=17)
        tk.Label(brand,image=self.crest,bg=SIDE).pack(anchor='center')
        self.lbl(brand,'KRUCHYX',18,GOLD_BRIGHT,'bold',SIDE).pack(anchor='center',pady=(1,0))
        self.lbl(brand,'MEDIEVAL MOD STUDIOS',9,GOLD,'bold',SIDE).pack(anchor='center')
        self.lbl(brand,f'RELEASE  {VERSION}',9,MUTED,bg=SIDE).pack(anchor='center',pady=(6,0))
        tk.Frame(self.sidebar,bg=EDGE,height=1).pack(fill='x',padx=16,pady=(0,13))
        for code,text,symbol in [
            ('welcome','  ✦   Strona główna',''),
            ('advisor','  ♛   Doradca frakcji',''),
            ('units','  ⚔   Ranking jednostek',''),
            ('economy','  ♜   Gospodarka i kampania',''),
            ('intelligence','  ◈   Łowca okazji',''),
            ('academy','  ✦   Akademia gracza',''),
            ('exploits','  ♠   Sekrety i exploity',''),
            ('calculators','  ♛   Kalkulatory',''),
            ('trainer','  ⚡   Trainer i MAX',''),
            ('editor','  ⚒   Edytor moda',''),
            ('saves','  ◈   Zapisy kampanii',''),
            ('library','  ▣   Biblioteka modów',''),
            ('chronicles','  ◷   Kroniki kampanii',''),
            ('army','  ⚔   Kreator armii',''),
            ('search','  ◈   Wyszukiwarka',''),
            ('mobile','  ▣   Kruchyx Mobile',''),
        ]:
            b=tk.Button(self.sidebar,text=tr(text,self.lang),anchor='w',padx=17,pady=5,relief='flat',bd=0,
                        bg=SIDE,fg=INK,activebackground=PANEL2,activeforeground=GOLD_BRIGHT,
                        font=(FONT,10),highlightthickness=0,cursor='hand2',command=lambda c=code:self.show(c))
            b.pack(fill='x',padx=10,pady=1);self.nav[code]=b
        spacer=tk.Frame(self.sidebar,bg=SIDE);self.nav_spacer=spacer;spacer.pack(fill='both',expand=True)
        self.your_mod_label=self.lbl(self.sidebar,'TWÓJ MOD',9,GOLD,'bold',SIDE)
        self.your_mod_label.pack(anchor='w',padx=22,pady=(0,4))
        self.mod_sidebar=self.lbl(self.sidebar,'Jeszcze nie wybrano',10,MUTED,bg=SIDE,wraplength=215,justify='left')
        self.mod_sidebar.pack(anchor='w',padx=22,pady=(0,14))
        tk.Frame(self.sidebar,bg=EDGE,height=1).pack(fill='x',padx=16,pady=7)
        self.footer_label=self.lbl(self.sidebar,'Wykonane przez Kruchyx',9,FAINT,bg=SIDE)
        self.footer_label.pack(pady=(7,17))

        self.right=tk.Frame(self.shell,bg=BG);self.right.pack(side='left',fill='both',expand=True)
        head=tk.Frame(self.right,bg=DARK,height=70);head.pack(fill='x');head.pack_propagate(False)
        headleft=tk.Frame(head,bg=DARK);headleft.pack(side='left',padx=30,pady=12)
        self.head_title=self.lbl(headleft,'Witaj w swoim centrum dowodzenia',17,INK,'bold',DARK)
        self.head_title.pack(anchor='w')
        self.head_sub=self.lbl(headleft,'Wybierz grę lub mod, aby rozpocząć',10,MUTED,bg=DARK)
        self.head_sub.pack(anchor='w',pady=(3,0))
        self.change_mod_btn=self.btn(head,'ZMIEŃ MOD',lambda:self.pick_folder(),variant='dark')
        self.change_mod_btn.pack(side='right',padx=(8,25),pady=13)
        self.lang_button=self.btn(head,'PL / EN',self.toggle_language,variant='gold',small=True)
        self.lang_button.pack(side='right',padx=(5,0),pady=13)
        self.lang_button.configure(text='EN → PL' if self.lang=='en' else 'PL → EN')
        tk.Frame(self.right,bg='#9c7549',height=2).pack(fill='x')
        self.canvas=tk.Canvas(self.right,bg=BG,bd=0,highlightthickness=0)
        self.scroll=ttk.Scrollbar(self.right,orient='vertical',command=self.canvas.yview,style='Premium.Vertical.TScrollbar')
        self.scroll.pack(side='right',fill='y');self.canvas.pack(side='left',fill='both',expand=True)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.body=tk.Frame(self.canvas,bg=BG)
        self.window_id=self.canvas.create_window((0,0),window=self.body,anchor='nw')
        self.body.bind('<Configure>',lambda e:self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>',lambda e:self.canvas.itemconfigure(self.window_id,width=e.width))
        self.canvas.bind_all('<MouseWheel>',self.on_wheel)

    def on_wheel(self,event):
        w=self.winfo_containing(event.x_root,event.y_root)
        if w and w.winfo_class() in ('Treeview','Text','TCombobox'):return
        if w:
            cursor=w
            while cursor is not None:
                if cursor==self.canvas:
                    self.canvas.yview_scroll(-1 if event.delta>0 else 1,'units');return
                cursor=cursor.master

    def lbl(self,parent,text,size=11,color=INK,weight='normal',bg=None,**kw):
        return tk.Label(parent,text=tr(text,self.lang),bg=bg or parent.cget('bg'),fg=color,
                        font=(FONT,size,weight),**kw)

    def btn(self,parent,text,action,variant='gold',small=False):
        opts={'gold':('#b98e56','#11171b','#e0ad68'), 'dark':(PANEL2,GOLD_BRIGHT,'#30414a'),
              'ghost':(PANEL,MUTED,PANEL2),'green':('#366c5d','#f7f2e9','#458875')}
        bg,fg,hover=opts[variant]
        b=tk.Button(parent,text=tr(text,self.lang),command=action,bg=bg,fg=fg,relief='flat',bd=0,
                    activebackground=hover,activeforeground=fg,highlightthickness=0,cursor='hand2',
                    font=(FONT,9 if small else 11,'bold'),padx=15 if small else 20,pady=9 if small else 12)
        return b

    def card(self,parent,pad=20,bg=PANEL):
        outer=tk.Frame(parent,bg=EDGE,padx=1,pady=1)
        inner=tk.Frame(outer,bg=bg,padx=pad,pady=pad)
        inner.pack(fill='both',expand=True)
        return outer,inner

    def heading(self,parent,eyebrow,title,desc=None):
        self.lbl(parent,tr(eyebrow,self.lang).upper(),10,GOLD,'bold').pack(anchor='w',pady=(7,9))
        self.lbl(parent,tr(title,self.lang),25,INK,'bold').pack(anchor='w')
        if desc:self.lbl(parent,desc,11,MUTED,wraplength=970,justify='left').pack(anchor='w',pady=(8,16))

    def section(self,parent,text):
        row=tk.Frame(parent,bg=BG)
        row.pack(fill='x',pady=(26,12))
        self.lbl(row,text,17,GOLD_BRIGHT,'bold').pack(side='left')
        tk.Frame(row,bg=EDGE,height=1).pack(side='left',fill='x',expand=True,padx=(18,0),pady=9)

    def status(self,parent,good,title,sub):
        row=tk.Frame(parent,bg=PANEL,pady=8)
        row.pack(fill='x')
        self.lbl(row,'●' if good else '○',12,EMERALD if good else RED,'bold',PANEL).pack(side='left',padx=(3,15))
        f=tk.Frame(row,bg=PANEL);f.pack(side='left',fill='x',expand=True)
        self.lbl(f,title,11,INK,'bold',PANEL).pack(anchor='w')
        self.lbl(f,sub,9,MUTED,bg=PANEL,wraplength=780,justify='left').pack(anchor='w',pady=(3,0))

    def show(self,page):
        self.page=page
        for name,b in self.nav.items():
            b.configure(bg=PANEL2 if name==page else SIDE,fg=GOLD_BRIGHT if name==page else INK)
        for child in self.body.winfo_children():child.destroy()
        self.canvas.yview_moveto(0)
        titles={'welcome':'Centrum dowodzenia','advisor':'Doradca strategiczny','units':'Atlas jednostek',
                'economy':'Gospodarka i kampania','intelligence':'Łowca okazji','academy':'Akademia gracza',
                'exploits':'Sekrety i exploity','calculators':'Kalkulatory strategii','trainer':'Trainer i pakiety MAX','editor':'Warsztat modyfikacji','saves':'Zapisy kampanii','library':'Biblioteka modów','chronicles':'Kroniki kampanii','army':'Kreator armii','search':'Wyszukiwarka wiedzy','mobile':'Kruchyx Mobile'}
        self.head_title.configure(text=tr(titles.get(page,'Kruchyx'),self.lang))
        self.head_sub.configure(text=f'{"Vanilla Kingdoms Uncompromised — DEMO" if self.active_path==ROOT/"examples" else self.active_path.name if self.active_path else tr("Wybierz mod, aby aktywować analizę",self.lang)}   •   v{VERSION}   •   {tr("Wykonane przez Kruchyx",self.lang)}')
        panel=tk.Frame(self.body,bg=BG,padx=29,pady=23)
        panel.pack(fill='both',expand=True)
        if page=='welcome':self.page_home(panel)
        elif page=='advisor':self.page_advisor(panel)
        elif page=='units':self.page_units(panel)
        elif page=='trainer':self.page_trainer(panel)
        elif page=='economy':page_economy(self,panel)
        elif page=='intelligence':page_intelligence(self,panel)
        elif page=='academy':page_academy(self,panel)
        elif page=='exploits':page_exploits(self,panel)
        elif page=='calculators':page_calculators(self,panel)
        elif page=='editor':self.page_editor(panel)
        elif page=='saves':self.page_saves(panel)
        elif page=='library':self.page_library(panel)
        elif page=='chronicles':page_chronicles(self,panel)
        elif page=='army':page_army_builder(self,panel)
        elif page=='search':page_search(self,panel)
        elif page=='mobile':page_mobile(self,panel)

    def hero(self,parent,headline,subtitle,cta=None):
        h=245
        cv=tk.Canvas(parent,height=h,bg=PANEL,highlightthickness=1,highlightbackground='#665440')
        cv.pack(fill='x',pady=(0,19))
        cv.create_image(0,0,anchor='nw',image=self.banner)
        cv.create_text(36,37,anchor='nw',text='KRUCHYX  /  MEDIEVAL PREMIUM',font=(FONT,11,'bold'),fill=GOLD_BRIGHT)
        cv.create_text(36,84,anchor='nw',text=tr(headline,self.lang),font=(FONT,27,'bold'),fill='#f6ead5')
        cv.create_text(36,141,anchor='nw',text=tr(subtitle,self.lang),font=(FONT,11),fill='#d8ccba',width=700)
        if cta:
            text,fn=cta
            button=self.btn(cv,text,fn,variant='gold')
            cv.create_window(36,197,anchor='nw',window=button)

    def _need_mod(self,parent,msg='Wybierz mod, aby zobaczyć te informacje.'):
        outer,inn=self.card(parent)
        outer.pack(fill='x',pady=(10,15))
        self.lbl(inn,'Brak aktywnego moda',18,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
        self.lbl(inn,msg,11,MUTED,bg=PANEL,wraplength=800).pack(anchor='w',pady=10)
        self.btn(inn,'WYBIERZ MOD',self.pick_folder).pack(anchor='w')

    def page_home(self,parent):
        if not self.model:
            self.hero(parent,'Twoje imperium zaczyna się tutaj.','Wybierz folder moda. Kruchyx przeanalizuje dane, pokaże mocne armie i pomoże wybrać frakcję.',('WYBIERZ MOD',self.pick_folder))
            self.heading(parent,'Pierwsze uruchomienie','Trzy kroki do własnej kampanii','Bez szukania plików EDU, bez dziesięciu zakładek i bez zgadywania, które funkcje są dostępne.')
            strip=tk.Frame(parent,bg=BG);strip.pack(fill='x',pady=10)
            for n,title,sub in [('01','Wybierz grę lub mod','Folder Medieval II, mods albo data'),('02','Automatyczna analiza','Ranking wojsk i podsumowanie'),('03','Przejdź do działania','Doradca, trainer, edytor')]:
                c,inn=self.card(strip,pad=17);c.pack(side='left',fill='both',expand=True,padx=(0,9))
                self.lbl(inn,n,18,GOLD,'bold',PANEL).pack(anchor='w');self.lbl(inn,title,12,INK,'bold',PANEL).pack(anchor='w',pady=6)
                self.lbl(inn,sub,10,MUTED,bg=PANEL).pack(anchor='w')
            self.btn(parent,'✦  '+('NEW PLAYER ACADEMY — START HERE' if self.lang=='en' else 'AKADEMIA DLA POCZĄTKUJĄCYCH — ZACZNIJ TUTAJ'),lambda:self.show('academy'),variant='gold').pack(anchor='w',pady=(8,14))
            self.btn(parent,'♠  '+('EXPLOITS & SECRETS' if self.lang=='en' else 'SEKRETY GRY I EXPLOITY'),lambda:self.show('exploits'),variant='dark',small=True).pack(anchor='w',pady=(0,12))
            self.btn(parent,'♛  '+('TRIBUTE & MERCHANT CALCULATORS' if self.lang=='en' else 'KALKULATOR TRYBUTU I KUPCÓW'),lambda:self.show('calculators'),variant='dark',small=True).pack(anchor='w',pady=(0,12))
            self.btn(parent,'◷  KRONIKI KAMPANII v0.9.5',lambda:self.show('chronicles'),variant='gold',small=True).pack(anchor='w',pady=(0,12))
            self.section(parent,'Chcesz najpierw zobaczyć przykład?')
            self.btn(parent,'URUCHOM PREZENTACJĘ NA DANYCH VANILLA KINGDOMS',self.load_demo,variant='dark').pack(anchor='w')
            self.lbl(parent,'Dane demonstracyjne pochodzą z przesłanego EDU i listy zasobów. Nie są kompletnym modem.',10,MUTED).pack(anchor='w',pady=12)
            return
        m=self.model; f=[z for z in m['factions'] if z.get('playable') is not False];files=m['context']['files']
        self.hero(parent,('VANILLA KINGDOMS / DEMO' if self.active_path==ROOT/'examples' else m['context']['mod'].name.replace('_',' ').upper())[:49],
                  'Raport strategiczny gotowy. Poznaj najlepsze armie, mocne strony frakcji i dostępne narzędzia.',('ZOBACZ REKOMENDACJE',lambda:self.show('advisor')))
        numbers=[(str(len(m['units'])),'JEDNOSTEK'),(str(len(f)),'FRAKCJI W EDU'),(str(sum(x['role']=='Okręty' for x in m['units'])),'OKRĘTÓW'),(f'{sum(bool(x) for x in files.values())}/6','ŹRÓDEŁ DANYCH')]
        row=tk.Frame(parent,bg=BG);row.pack(fill='x',pady=4)
        for n,label in numbers:
            co,ci=self.card(row,pad=18);co.pack(side='left',fill='both',expand=True,padx=(0,10))
            self.lbl(ci,n,24,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
            self.lbl(ci,label,9,MUTED,'bold',PANEL).pack(anchor='w',pady=(6,0))
        self.section(parent,'Jaką armię oferuje ten mod?')
        summary,si=self.card(parent,pad=18,bg='#20282c');summary.pack(fill='x',pady=(0,3))
        self.lbl(si,(mod_summary_en(m) if self.lang=='en' else mod_summary(m)),11,INK,bg='#20282c',wraplength=960,justify='left').pack(anchor='w')
        self.section(parent,'Doradca Kruchyx poleca')
        if not f:self._need_mod(parent,'Nie znaleziono pliku jednostek EDU. Wybierz folder z tym plikiem.')
        else:
            row=tk.Frame(parent,bg=BG);row.pack(fill='x')
            for ix,x in enumerate(f[:3],1):
                co,ci=self.card(row,pad=18,bg=PANEL);co.pack(side='left',fill='both',expand=True,padx=(0,10))
                self.lbl(ci,f"#{ix}  {('MILITARY POTENTIAL' if self.lang=='en' else 'POTENCJAŁ WOJSKOWY')}",9,GOLD,'bold',PANEL).pack(anchor='w')
                self.lbl(ci,pretty_lang(x['name'],self.lang),17,INK,'bold',PANEL).pack(anchor='w',pady=(11,3))
                self.lbl(ci,f"{('Roster index' if self.lang=='en' else 'Indeks rosteru')}  {x['score']:.1f}",11,EMERALD,'bold',PANEL).pack(anchor='w')
                self.lbl(ci,('See troop strengths in faction details' if self.lang=='en' else x['style'].capitalize()),10,MUTED,bg=PANEL,wraplength=240,justify='left').pack(anchor='w',pady=(9,10))
                self.btn(ci,'POZNAJ FRAKCJĘ',lambda name=x['name']:self.choose_faction(name),variant='dark',small=True).pack(anchor='w')
            self.lbl(parent,'Ranking EDU pokazuje potencjał jednostek, a nie przewagę startową. Bez pliku budynków nie wiemy, kiedy można je rekrutować.',10,MUTED,wraplength=980,justify='left').pack(anchor='w',pady=(11,0))
        if m['context'].get('vanilla') and m['context'].get('packed_base'):
            ext,ei=self.card(parent,pad=18);ext.pack(fill='x',pady=8)
            self.lbl(ei,'⚠  '+('BASE GAME DATA IS PACKED' if self.lang=='en' else 'DANE GRY PODSTAWOWEJ SĄ SPAKOWANE'),13,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
            self.lbl(ei,('To see vanilla units and economy, extract definitions to a separate cache using the official unpacker.' if self.lang=='en' else 'Aby analizować zwykłą kampanię i jednostki, odczytaj definicje do osobnego katalogu oficjalnym ekstraktorem.'),10,MUTED,bg=PANEL,wraplength=900).pack(anchor='w',pady=9)
            self.btn(ei,('PREPARE VANILLA DATA' if self.lang=='en' else 'PRZYGOTUJ DANE VANILLA'),lambda:self._extract_vanilla(m['context']['game_root']),variant='gold').pack(anchor='w')
        self.section(parent,'Stan analizy i możliwości')
        co,ci=self.card(parent);co.pack(fill='x')
        for key,fp in files.items():self.status(ci,bool(fp),friendly_file(key),'Wykryto — można korzystać z tych danych' if fp else 'Brak pliku — odpowiednie funkcje są ograniczone')
        self.section(parent,'Szybkie działania')
        row=tk.Frame(parent,bg=BG);row.pack(fill='x')
        for label,fn in [('RANKING FRAKCJI',lambda:self.show('advisor')),('ATLAS JEDNOSTEK',lambda:self.show('units')),('CHEATY I PAKIETY MAX',lambda:self.show('trainer'))]:
            self.btn(row,label,fn,variant='dark').pack(side='left',padx=(0,10))
        row2=tk.Frame(parent,bg=BG);row2.pack(fill='x',pady=8)
        for label,fn in [('♜  '+('ECONOMY' if self.lang=='en' else 'GOSPODARKA'),lambda:self.show('economy')),
                         ('◈  '+('OPPORTUNITIES' if self.lang=='en' else 'OKAZJE'),lambda:self.show('intelligence')),
                         ('✦  '+('BEGINNER ACADEMY' if self.lang=='en' else 'AKADEMIA GRACZA'),lambda:self.show('academy'))]:
            self.btn(row2,label,fn,variant='gold',small=True).pack(side='left',padx=(0,9))

    def page_advisor(self,parent):
        self.heading(parent,'Raport strategiczny','Czym najlepiej zagrać?',
                     'Doradca ocenia możliwości jednostek z wybranego moda i tłumaczy wybór. To analiza regułowa offline, a nie symulacja bitew ani model AI.')
        if not self.model:self._need_mod(parent);return
        m=self.model;f=[z for z in m['factions'] if z.get('playable') is not False];files=m['context']['files']
        co,ci=self.card(parent,pad=19,bg='#1e2a30');co.pack(fill='x',pady=(0,15))
        self.lbl(ci,'CO OZNACZA TEN RANKING?',12,GOLD_BRIGHT,'bold','#1e2a30').pack(anchor='w')
        self.lbl(ci,'Dopasowujemy polecane frakcje do stylu gry i analizujemy ofensywę, obronę, morale, zasięg oraz skład wojsk. Oceny oddzielnych ról są heurystyczne. Nie gwarantują zwycięstwa.',11,INK,bg='#1e2a30',wraplength=930,justify='left').pack(anchor='w',pady=8)
        cave=[]
        if not files['buildings']:cave.append('missing export_descr_buildings.txt: recruitment unverified' if self.lang=='en' else 'brak export_descr_buildings.txt: rekrutacja niezweryfikowana')
        if not files['campaign']:cave.append('missing descr_strat.txt: starting positions and playability unverified' if self.lang=='en' else 'brak descr_strat.txt: start frakcji i grywalność niezweryfikowane')
        if cave:self.lbl(ci,('LIMITATIONS: ' if self.lang=='en' else 'OGRANICZENIA: ')+('  •  '.join(cave)),10,RED,bg='#1e2a30',wraplength=900,justify='left').pack(anchor='w',pady=3)
        if not f:
            self._need_mod(parent,'EDU nie zostało znalezione. Dostępna jest wyłącznie diagnostyka plików.');return
        self.section(parent,'Wybierz swój styl wojny')
        role_labels=[('⚔  ELITE INFANTRY' if self.lang=='en' else '⚔  ELITARNA PIECHOTA','Piechota wręcz'),('♞  HEAVY CAVALRY' if self.lang=='en' else '♞  CIĘŻKA KAWALERIA','Kawaleria wręcz'),('➶  MISSILE TROOPS' if self.lang=='en' else '➶  OSTRZAŁ','Piechota strzelecka'),('♘  HORSE ARCHERS' if self.lang=='en' else '♘  ŁUCZNICY KONNI','Kawaleria strzelecka')]
        specialists=tk.Frame(parent,bg=BG);specialists.pack(fill='x')
        for i,(label,role) in enumerate(role_labels):
            choices=[z for z in leaders_by_role(m,role,limit=50) if z[1].get('playable') is not False][:3]
            c,inn=self.card(specialists,pad=15)
            c.grid(row=i//2,column=i%2,sticky='nsew',padx=(0,12),pady=6)
            specialists.columnconfigure(i%2,weight=1)
            self.lbl(inn,label,11,GOLD,'bold',PANEL).pack(anchor='w')
            if choices:
                self.lbl(inn,pretty_lang(choices[0][1]['name'],self.lang),15,INK,'bold',PANEL).pack(anchor='w',pady=(9,3))
                self.lbl(inn,f"{('Top score' if self.lang=='en' else 'Lider tej roli')}: {choices[0][0]:.1f} {('points' if self.lang=='en' else 'pkt')}",10,EMERALD,bg=PANEL).pack(anchor='w')
                self.lbl(inn,('Next: ' if self.lang=='en' else 'Dalej: ')+', '.join(pretty_lang(x[1]['name'],self.lang) for x in choices[1:]),10,MUTED,bg=PANEL,wraplength=430,justify='left').pack(anchor='w',pady=(6,0))
                self.btn(inn,'ZOBACZ FRAKCJĘ',lambda name=choices[0][1]['name']:self.choose_faction(name),variant='dark',small=True).pack(anchor='w',pady=(10,0))
            else:self.lbl(inn,'Brak danych',11,MUTED,bg=PANEL).pack(anchor='w')
        self.section(parent,'Najlepsze wybory w tym modzie')
        for ix,x in enumerate(f[:8],1):
            outer,inner=self.card(parent,pad=15);outer.pack(fill='x',pady=5)
            top=tk.Frame(inner,bg=PANEL);top.pack(fill='x')
            self.lbl(top,f'{ix:02}',15,GOLD_BRIGHT,'bold',PANEL).pack(side='left',padx=(0,19))
            self.lbl(top,pretty_lang(x['name'],self.lang),16,INK,'bold',PANEL).pack(side='left')
            self.lbl(top,f"{('Index' if self.lang=='en' else 'Indeks')} {x['score']:.1f}",11,EMERALD,'bold',PANEL).pack(side='right')
            self.lbl(inner,(explanation_en(x) if self.lang=='en' else explanation(x)),11,MUTED,bg=PANEL,wraplength=920,justify='left').pack(anchor='w',padx=37,pady=(7,9))
            if x['start_money'] is not None:
                self.lbl(inner,f"Skarbiec startowy: {x['start_money']:,}".replace(',',' ')+' florenów',10,GOLD,bg=PANEL).pack(anchor='w',padx=37)
            self.btn(inner,'SZCZEGÓŁY I ARMIA',lambda name=x['name']:self.choose_faction(name),variant='dark',small=True).pack(anchor='w',padx=37,pady=(9,0))
        self.section(parent,'Raport do zachowania')
        row=tk.Frame(parent,bg=BG);row.pack(fill='x')
        self.btn(row,'ZAPISZ RAPORT TXT',self.export_report).pack(side='left')
        self.btn(row,'KOPIUJ PODSUMOWANIE',self.copy_report,variant='dark').pack(side='left',padx=9)

    def choose_faction(self,name):
        self.selected_faction=name
        self.page_faction_dialog(name)

    def page_faction_dialog(self,name):
        f=next((x for x in self.model['factions'] if x['name']==name),None)
        if f is None:return
        dlg=tk.Toplevel(self,bg=BG);dlg.title(('Kruchyx Faction Advisor — ' if self.lang=='en' else 'Doradca Kruchyx — ')+pretty_lang(f['name'],self.lang));dlg.geometry('790x670');dlg.minsize(680,540)
        x=tk.Frame(dlg,bg=BG,padx=25,pady=20);x.pack(fill='both',expand=True)
        self.lbl(x,'RAPORT FRAKCJI',10,GOLD,'bold').pack(anchor='w')
        self.lbl(x,pretty_lang(f['name'],self.lang),24,INK,'bold').pack(anchor='w',pady=(7,10))
        self.lbl(x,(explanation_en(f) if self.lang=='en' else explanation(f)),12,MUTED,wraplength=715,justify='left').pack(anchor='w',pady=(0,18))
        self.lbl(x,'NAJSILNIEJSZE ROLE',13,GOLD_BRIGHT,'bold').pack(anchor='w',pady=(0,8))
        for role,score in f['strengths']:
            row=tk.Frame(x,bg=PANEL,pady=9,padx=14);row.pack(fill='x',pady=3)
            self.lbl(row,tr(role,self.lang),11,INK,'bold',PANEL).pack(side='left')
            self.lbl(row,str(score)+(' points' if self.lang=='en' else ' pkt'),11,EMERALD,'bold',PANEL).pack(side='right')
        self.lbl(x,'WYBRANE JEDNOSTKI',13,GOLD_BRIGHT,'bold').pack(anchor='w',pady=(17,8))
        for u in f['best'][:4]:
            self.lbl(x,f"• {u['name']} — {tr(u['role'],self.lang)}, {('index' if self.lang=='en' else 'indeks')} {u['score']:.1f}",11,INK).pack(anchor='w',pady=3)
        self.lbl(x,'UWAGA: niedostępne jeszcze potwierdzenie możliwości rekrutacji i realnej siły w kampanii (wymaga EDB i danych kampanii).',10,RED,wraplength=715,justify='left').pack(anchor='w',pady=13)
        self.btn(x,'ZAMKNIJ',dlg.destroy,variant='dark').pack(anchor='e',pady=(8,0))

    def page_units(self,parent):
        self.heading(parent,'Atlas armii','Jednostki, okręty i oblężenia','Wybierz kategorię i poznaj prawdziwe liczby: atak, szarżę, obronę, morale, zasięg i koszty.')
        if not self.model:self._need_mod(parent);return
        if not self.model['units']:
            self._need_mod(parent,'Brak pliku EDU w wybranym modzie.');return
        roles=['Piechota wręcz','Kawaleria wręcz','Piechota strzelecka','Kawaleria strzelecka','Okręty','Oblężnicze','Wszystkie']
        ribbon=tk.Frame(parent,bg=BG);ribbon.pack(fill='x',pady=(0,15))
        for index,role in enumerate(roles):
            b=self.btn(ribbon,role,lambda name=role:self.set_role(name),variant='gold' if self.current_role==role else 'dark',small=True)
            b.grid(row=index//4,column=index%4,sticky='ew',padx=(0,8),pady=4)
            ribbon.columnconfigure(index%4,weight=1)
        filters=tk.Frame(parent,bg=BG);filters.pack(fill='x',pady=5)
        self.lbl(filters,'SZUKAJ JEDNOSTKI',9,GOLD,'bold').pack(side='left',padx=(0,9))
        self.unit_filter=tk.StringVar()
        inp=ttk.Entry(filters,textvariable=self.unit_filter,style='Premium.TEntry',width=29)
        inp.pack(side='left');self.unit_filter.trace_add('write',lambda *_:self.render_unit_table())
        self.lbl(filters,'  FRAKCJA',9,GOLD,'bold').pack(side='left',padx=(15,9))
        owners=sorted({owner for u in self.model['units'] for owner in u['owners'] if owner!='slave'})
        self.unit_owner=tk.StringVar(value=tr('Wszystkie',self.lang))
        combo=ttk.Combobox(filters,textvariable=self.unit_owner,values=[tr('Wszystkie',self.lang)]+owners,state='readonly',style='Premium.TCombobox',width=23)
        combo.pack(side='left');combo.bind('<<ComboboxSelected>>',lambda _:self.render_unit_table())
        holder=tk.Frame(parent,bg=PANEL);holder.pack(fill='both',expand=True,pady=14)
        columns=('rank','name','score','atk','def','morale','cost')
        self.unit_tree=ttk.Treeview(holder,columns=columns,show='headings',height=12,style='Premium.Treeview',selectmode='browse')
        for key,label,width in [('rank','#',50),('name','JEDNOSTKA',275),('score','OCENA*',86),('atk','ATAK',75),('def','OBRONA',85),('morale','MORALE',85),('cost','KOSZT',90)]:
            self.unit_tree.heading(key,text=tr(label,self.lang));self.unit_tree.column(key,width=width,anchor='w' if key=='name' else 'center')
        self.unit_tree.pack(side='left',fill='both',expand=True)
        sc=ttk.Scrollbar(holder,orient='vertical',command=self.unit_tree.yview,style='Premium.Vertical.TScrollbar');sc.pack(side='right',fill='y')
        self.unit_tree.configure(yscrollcommand=sc.set)
        self.unit_tree.bind('<<TreeviewSelect>>',self.unit_selected)
        outer,ci=self.card(parent,pad=17);outer.pack(fill='x',pady=(0,8))
        self.unit_details=self.lbl(ci,'Kliknij dowolną jednostkę w tabeli, aby poznać jej mocne strony.',11,INK,bg=PANEL,justify='left',wraplength=860)
        self.unit_details.pack(anchor='w')
        self.lbl(parent,'* Ocena jest heurystyką dla roli; nie porównuj wprost punktów okrętów z punktami piechoty. Wyniki nie są testami bitewnymi.',10,MUTED,wraplength=920,justify='left').pack(anchor='w',pady=(3,0))
        self.render_unit_table()

    def set_role(self,role):
        self.current_role=role;self.show('units')

    def render_unit_table(self):
        if not hasattr(self,'unit_tree') or not self.unit_tree.winfo_exists():return
        role=self.current_role;term=self.unit_filter.get().strip().casefold();owner=self.unit_owner.get()
        ranked=[u for u in self.model['units'] if (role=='Wszystkie' or u['role']==role) and (owner in ('Wszystkie','All') or owner in u['owners']) and term in u['name'].casefold()]
        ranked.sort(key=lambda u:-u['score']);self.unit_rows=ranked
        self.unit_tree.delete(*self.unit_tree.get_children())
        for i,u in enumerate(ranked[:450],1):
            self.unit_tree.insert('', 'end',iid=str(i-1),values=(i,u['name'],u['score'],int(u['attack']),int(u['defence']),int(u['morale']),int(u['cost'])))
        self.unit_details.configure(text=(f'{len(ranked)} units found. Select one to inspect details and factions.' if self.lang=='en' else f'Wyniki: {len(ranked)} jednostek. Wybierz jednostkę, aby zobaczyć szczegóły i frakcje.'))

    def unit_selected(self,event=None):
        sel=self.unit_tree.selection()
        if not sel:return
        u=self.unit_rows[int(sel[0])]
        strengths=[]
        if u['armour_piercing']:strengths.append('armor piercing' if self.lang=='en' else 'przebija pancerz')
        if u['charge']>=7:strengths.append('strong charge' if self.lang=='en' else 'silna szarża')
        if u['range']>=150:strengths.append('long range' if self.lang=='en' else 'daleki zasięg')
        if u['morale']>=10:strengths.append('high morale' if self.lang=='en' else 'wysokie morale')
        if u['health']>=2:strengths.append('extra health' if self.lang=='en' else 'zwiększona żywotność')
        if self.lang=='en':
            msg=(f"{u['name']} • {tr(u['role'],self.lang)}\nAttack {u['attack']:g} | Charge {u['charge']:g} | Defense {u['defence']:g} | Morale {u['morale']:g} | Range {u['range']:g}\n"
                 f"Cost {u['cost']:g} | Upkeep {u['upkeep']:g} | EDU soldiers {u['size']:g}\n"
                 f"Strengths: {', '.join(strengths) or 'no standout traits'}\nFactions: {', '.join(pretty_lang(x,self.lang) for x in u['owners'][:12])}")
        else:
            msg=(f"{u['name']} • {u['role']}\nAtak {u['attack']:g} | Szarża {u['charge']:g} | Obrona {u['defence']:g} | Morale {u['morale']:g} | Zasięg {u['range']:g}\n"
                 f"Koszt {u['cost']:g} | Utrzymanie {u['upkeep']:g} | Żołnierze wg EDU: {u['size']:g}\n"
                 f"Przewagi: {', '.join(strengths) or 'bez wyróżnionych właściwości'}\nFrakcje: {', '.join(pretty_lang(x,self.lang) for x in u['owners'][:12])}")
        self.unit_details.configure(text=msg)

    def page_trainer(self,parent):
        self.heading(parent,'Centrum cheatów','Trainer i pakiety MAX','Generuj, kopiuj lub przekaż komendy do otwartej konsoli Medieval II. To nie jest jeszcze trainer odczytujący pamięć gry.')
        notice,ci=self.card(parent,pad=16,bg='#293135');notice.pack(fill='x',pady=(0,17))
        self.lbl(ci,'●  TRYB KONSOLI  •  DZIAŁA BEZ INGEROWANIA W PAMIĘĆ',11,GOLD_BRIGHT,'bold','#293135').pack(anchor='w')
        self.lbl(ci,'Asystowane Ctrl+V wymaga Windows, włączonej gry i ręcznie otwartej konsoli (~). Gra musi sama zatwierdzić komendy. Nielimitowany ruch ON/OFF nie jest jeszcze obsługiwany.',10,INK,bg='#293135',wraplength=930,justify='left').pack(anchor='w',pady=(6,0))
        form,ci=self.card(parent,pad=23);form.pack(fill='x')
        self.lbl(ci,'CO CHCESZ ZROBIĆ?',10,GOLD,'bold',PANEL).pack(anchor='w')
        actions=['Dodaj pieniądze','MAX — agent','Odnów ruch postaci','Natychmiastowa budowa','Dodaj ludność','Dodaj jednostki','Odkryj / ukryj mapę']
        self.action_items=actions
        self.action_var=tk.StringVar(value=tr('Dodaj pieniądze',self.lang))
        self.action_cb=ttk.Combobox(ci,textvariable=self.action_var,values=[tr(x,self.lang) for x in actions],style='Premium.TCombobox',state='readonly',width=37)
        self.action_cb.pack(anchor='w',pady=(9,14));self.action_cb.bind('<<ComboboxSelected>>',lambda e:self.update_trainer_fields())
        self.dynamic=tk.Frame(ci,bg=PANEL);self.dynamic.pack(fill='x')
        self.trainer_vars={}
        self.update_trainer_fields()
        controls=tk.Frame(ci,bg=PANEL);controls.pack(fill='x',pady=(15,7))
        self.btn(controls,'GENERUJ I KOPIUJ',self.generate_copy,variant='gold').pack(side='left',padx=(0,8))
        self.btn(controls,'WKLEJ DO GRY ZA 4 S',self.paste_assisted,variant='dark').pack(side='left')
        co,pad=self.card(parent,pad=18);co.pack(fill='both',expand=True,pady=(16,0))
        self.lbl(pad,'GOTOWE KOMENDY',10,GOLD,'bold',PANEL).pack(anchor='w',pady=(0,8))
        self.output=tk.Text(pad,height=9,bg=DARK,fg=EMERALD,insertbackground=GOLD,relief='flat',bd=0,padx=14,pady=14,
                            font=('Consolas',11),wrap='word')
        self.output.pack(fill='both',expand=True)
        self.trainer_hint=self.lbl(pad,'Wybierz akcję, a następnie kliknij „Generuj i kopiuj”.',10,MUTED,bg=PANEL,wraplength=800,justify='left')
        self.trainer_hint.pack(anchor='w',pady=(9,0))
        self.btn(parent,'✦  '+('BEGINNER CHEAT GUIDE' if self.lang=='en' else 'PORADNIK CHEATÓW DLA POCZĄTKUJĄCYCH'),
                 lambda:self._to_academy('cheats'),variant='dark',small=True).pack(anchor='w',pady=12)
        self.btn(parent,'♠  '+('EXPLOIT GUIDES & TRADE TRICKS' if self.lang=='en' else 'PORADNIK EXPLOITÓW I KUPCÓW'),lambda:self.show('exploits'),variant='dark',small=True).pack(anchor='w',pady=(0,12))
        self.section(parent,'Funkcje Live Trainer')
        bad,txt=self.card(parent,pad=16);bad.pack(fill='x')
        self.status(txt,False,'Nielimitowany ruch (ON / OFF)','Wyłączone: brak zweryfikowanego adaptera pamięci gry lub obsługiwanego API silnika.')
        self.status(txt,False,'Automatyczne rozpoznanie zaznaczonej postaci','Wyłączone: konsola „this” wymaga, byś sam zaznaczył postać w grze.')

    def field(self,parent,key,label,default):
        f=tk.Frame(parent,bg=PANEL);f.pack(fill='x',pady=4)
        self.lbl(f,label,10,MUTED,bg=PANEL,width=27,anchor='w').pack(side='left')
        v=tk.StringVar(value=default);self.trainer_vars[key]=v
        ttk.Entry(f,textvariable=v,width=29,style='Premium.TEntry').pack(side='left')

    def _trainer_action(self):
        return next((key for key in self.action_items if tr(key,self.lang)==self.action_var.get()),self.action_var.get())

    def update_trainer_fields(self):
        for child in self.dynamic.winfo_children():child.destroy()
        self.trainer_vars={};act=self._trainer_action()
        if act=='Dodaj pieniądze':self.field(self.dynamic,'cash','Kwota florenów','1000000')
        elif act=='MAX — agent':
            row=tk.Frame(self.dynamic,bg=PANEL);row.pack(fill='x',pady=5)
            self.lbl(row,'Rodzaj postaci',10,MUTED,bg=PANEL,width=27,anchor='w').pack(side='left')
            self.agent_var=tk.StringVar(value='general');ttk.Combobox(row,values=list(PRESETS),textvariable=self.agent_var,
                   state='readonly',style='Premium.TCombobox',width=27).pack(side='left')
            self.field(self.dynamic,'character','Nazwa postaci','William')
            self.this_var=tk.BooleanVar(value=True)
            ttk.Checkbutton(self.dynamic,text='Użyj postaci zaznaczonej w grze (this)',variable=self.this_var,style='Premium.TCheckbutton').pack(anchor='w',pady=7)
        elif act=='Odnów ruch postaci':self.field(self.dynamic,'character','Nazwa postaci','William')
        elif act=='Natychmiastowa budowa':self.field(self.dynamic,'city','Nazwa miasta','London')
        elif act=='Dodaj ludność':self.field(self.dynamic,'city','Nazwa miasta','London');self.field(self.dynamic,'pop','Dodaj mieszkańców','5000')
        elif act=='Dodaj jednostki':
            for args in [('target','Nazwa miasta lub generała','London'),('id','ID jednostki z EDU','Dismounted Feudal Knights'),('count','Liczba oddziałów (maks. 5)','1'),('exp','Doświadczenie (0–9)','9'),('arm','Pancerz (0–3)','3'),('weapon','Broń (0–3)','3')]:self.field(self.dynamic,*args)
        else:self.lbl(self.dynamic,'Przełącza widoczność mapy w konsoli gry.',11,MUTED,bg=PANEL).pack(anchor='w')
        self.trainer_plan=None

    def plan_commands(self):
        v=lambda key:self.trainer_vars[key].get()
        a=self._trainer_action()
        if a=='Dodaj pieniądze':return money(v('cash'))
        if a=='MAX — agent':return agent_plan(self.agent_var.get(),v('character'),self.this_var.get())
        if a=='Odnów ruch postaci':return movement(v('character'))
        if a=='Natychmiastowa budowa':return building(v('city'))
        if a=='Dodaj ludność':return population(v('city'),v('pop'))
        if a=='Dodaj jednostki':return unit(v('target'),v('id'),v('count'),v('exp'),v('arm'),v('weapon'))
        return quick('fog')

    def generate_copy(self):
        try:p=self.plan_commands()
        except (CommandError,ValueError) as exc:messagebox.showerror('Sprawdź dane',str(exc));return False
        self.trainer_plan=p
        self.output.delete('1.0','end');self.output.insert('end',p.as_text())
        self.clipboard_clear();self.clipboard_append(p.as_text());self.update()
        self.trainer_hint.configure(text=(f'✓ Copied {len(p.commands)} commands. ' if self.lang=='en' else f'✓ Skopiowano {len(p.commands)} komend. ')+p.caveat)
        return True

    def paste_assisted(self):
        if not self.generate_copy():return
        if not messagebox.askyesno('Asystowane wklejanie','Po 4 sekundach spróbuję wysłać Ctrl+V do aktywnego okna Medieval II.\n\nPrzejdź do gry, zaznacz odpowiednią postać i otwórz konsolę (~).\n\nNie wciskam Enter i nie potwierdzam wykonania. Kontynuować?'):
            return
        self.trainer_hint.configure(text='Przejdź do otwartej konsoli gry — wklejanie za 4 sekundy...')
        self.after(4000,self._do_paste)

    def _do_paste(self):
        try:
            title=paste_to_focused_game()
            self.trainer_hint.configure(text='Wysłano Ctrl+V do '+title+'. Sprawdź wykonanie w grze.')
        except Exception as exc:
            self.trainer_hint.configure(text='Nie przekazano komend: '+str(exc))
            messagebox.showwarning('Nie wysłano komend',str(exc))

    def page_editor(self,parent):
        self.heading(parent,'Warsztat królestwa','Edytuj bez zgadywania','Wybierz rodzaj zmiany. Program pokazuje, jakie pliki są wymagane i czy operacja dotyczy nowej, czy uruchomionej kampanii.')
        files=self.model['context']['files'] if self.model else {}
        for title,source,desc,required in [
            ('Startowe pieniądze i frakcje','campaign','Edycja denari, rozgrywalności i dat. Zmiany zwykle wymagają nowej kampanii.',True),
            ('Miasta i budynki','campaign','Zmiana populacji, właścicieli i zabudowy w descr_strat.',True),
            ('Jednostki i statystyki','edu','Modyfikacja EDU, statystyk i dostępności oddziałów. Wymaga luźnego EDU.',True),
            ('Generałowie i armie','campaign','Doświadczenie, armie startowe i cechy z zapisów kampanii.',True),
            ('Dyplomacja i grywalność','campaign','Relacje frakcji oraz lista grywalnych państw.',True),
        ]:
            active=bool(files.get(source));out,ci=self.card(parent,pad=15);out.pack(fill='x',pady=5)
            top=tk.Frame(ci,bg=PANEL);top.pack(fill='x')
            self.lbl(top,title,14,INK,'bold',PANEL).pack(side='left')
            self.lbl(top,'DOSTĘPNE' if active else 'BRAK ŹRÓDŁA',10,EMERALD if active else RED,'bold',PANEL).pack(side='right')
            self.lbl(ci,desc,10,MUTED,bg=PANEL,wraplength=790,justify='left').pack(anchor='w',pady=8)
            self.lbl(ci,'Wymagany plik: '+('descr_strat.txt' if source=='campaign' else 'export_descr_unit.txt'),10,GOLD,bg=PANEL).pack(anchor='w')
            if active:self.btn(ci,'OTWÓRZ WARSZTAT',self.open_classic,variant='dark',small=True).pack(anchor='w',pady=(12,0))
            else:self.lbl(ci,'Nie można edytować bez źródła. Wybierz inny mod lub wskaż właściwy folder.',10,FAINT,bg=PANEL).pack(anchor='w',pady=(5,0))
        self.section(parent,'Zachowane narzędzia')
        note,ci=self.card(parent,pad=20);note.pack(fill='x')
        self.lbl(ci,'Klasyczne edytory v0.8.1',14,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
        self.lbl(ci,'Zaawansowane funkcje wcześniejszych wersji pozostały w programie i otwierają się w osobnym oknie. Zachowano ich podgląd zmian, zapis z backupem i historię. Pełne przeniesienie ich do nowego GUI jest dalszym etapem.',11,MUTED,bg=PANEL,wraplength=900,justify='left').pack(anchor='w',pady=10)
        self.btn(ci,'OTWÓRZ EDYTORY KLASYCZNE',self.open_classic).pack(anchor='w')

    def page_saves(self,parent):
        self.heading(parent,'Pliki kampanii','Zapisy — bezpieczny podgląd','Nie modyfikujemy binarnych plików .sav bez pełnej walidacji. Poprzedni Save Explorer pozostaje dostępny.')
        n,ci=self.card(parent,pad=25);n.pack(fill='x',pady=15)
        self.lbl(ci,'ODCZYT DOSTĘPNY  •  ZAPIS WYŁĄCZONY',13,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
        self.lbl(ci,'Eksperymentalne rozpoznawanie pieniędzy zostało skalibrowane tylko na konkretnych wcześniejszych zapisach Anglii i Polski. Dla nowego moda nie możemy zakładać poprawności odczytu.',11,MUTED,bg=PANEL,wraplength=900,justify='left').pack(anchor='w',pady=13)
        self.btn(ci,'OTWÓRZ SAVE EXPLORER',self.open_classic,variant='dark').pack(anchor='w')
        self.section(parent,'Czego jeszcze nie można zrobić?')
        fail,fi=self.card(parent);fail.pack(fill='x')
        self.status(fi,False,'Edycja skarbca w zapisanym pliku SAV','Brak uniwersalnego parsera i testów poprawności zapisów dla tego moda.')
        self.status(fi,False,'Nielimitowany ruch działającej kampanii','Brak prawdziwej integracji z uruchomionym silnikiem gry.')

    def page_library(self,parent):
        self.heading(parent,'Twoja biblioteka','Wybierz mod jednym kliknięciem','Wskaż folder gry, katalog mods, konkretny mod lub jego folder data. Kruchyx poszuka rozpoznanych źródeł i przygotuje raport.')
        self.hero(parent,'Odkryj nowe królestwo.','Nie musisz wybierać konkretnych plików — wskaż folder gry lub moda.',('WYBIERZ FOLDER',self.pick_folder))
        self._library_game_picker(parent)
        self.btn(parent,('VANILLA UNPACKING GUIDE — STEP BY STEP' if self.lang=='en' else
                         'JAK ROZPAKOWAĆ VANILLA — INSTRUKCJA KROK PO KROKU'),
                 lambda:open_vanilla_guide(self,find_game_root(self.active_path) if self.active_path else None),
                 variant='gold').pack(anchor='w',pady=(10,16))
        if self.model:
            co,ci=self.card(parent);co.pack(fill='x',pady=11)
            self.lbl(ci,'OBECNIE WYBRANY',10,GOLD,'bold',PANEL).pack(anchor='w')
            self.lbl(ci,str(self.active_path),12,INK,bg=PANEL,wraplength=920,justify='left').pack(anchor='w',pady=8)
            self.btn(ci,'OTWÓRZ RAPORT',lambda:self.show('welcome'),variant='dark').pack(anchor='w')
        co,ci=self.card(parent);co.pack(fill='x',pady=11)
        self.lbl(ci,'DEMONSTRACJA NA PRZESŁANYCH DANYCH',11,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
        self.lbl(ci,'Uruchomi raport na przykładzie plików EDU i surowców Vanilla Kingdoms Uncompromised. Dane nie zawierają plików kampanii i budynków.',11,MUTED,bg=PANEL,wraplength=900,justify='left').pack(anchor='w',pady=8)
        self.btn(ci,'PRZEJRZYJ PRZYKŁAD',self.load_demo,variant='dark').pack(anchor='w')


    def _library_game_picker(self,parent):
        """Explicit vanilla selection; never default to first installed mod."""
        self.section(parent,'Medieval II — kampania podstawowa / Vanilla')
        outer,ci=self.card(parent,pad=17);outer.pack(fill='x',pady=6)
        known=known_game_locations()
        current=find_game_root(self.active_path) if self.active_path else None
        if current and current not in known:known.insert(0,current)
        self.lbl(ci,('Choose a game directory or select a detected Steam installation.' if self.lang=='en' else
                     'Wybierz folder gry lub wykrytą instalację Steam. Vanilla jest osobną pozycją na liście.'),
                 11,MUTED,bg=PANEL,wraplength=900,justify='left').pack(anchor='w',pady=(3,12))
        for game in known:
            self.btn(ci,'⚔  '+str(game),lambda g=game:self._open_campaign_picker(g),variant='dark',small=True).pack(anchor='w',pady=3)
        self.btn(ci,('FIND MEDIEVAL II INSTALLATION' if self.lang=='en' else 'WSKAŻ INSTALACJĘ MEDIEVAL II'),
                 self._pick_game,variant='gold',small=True).pack(anchor='w',pady=7)
        self.btn(ci,('READ VANILLA EXTRACTION GUIDE' if self.lang=='en' else 'PRZECZYTAJ INSTRUKCJĘ ROZPAKOWANIA'),
                 lambda:open_vanilla_guide(self,find_game_root(self.active_path) if self.active_path else None),
                 variant='dark',small=True).pack(anchor='w',pady=(0,8))
        selected=find_game_root(self.active_path) if self.active_path else None
        if selected and self.model and self.model['context'].get('vanilla'):
            sources=self.model['context']['files']
            if not sources.get('edu'):
                self.lbl(ci,('Vanilla data is packed. You can extract definitions to a separate cache.' if self.lang=='en' else
                             'Dane Vanilla są spakowane. Możesz wypakować definicje do osobnego, bezpiecznego katalogu.'),
                         10,GOLD_BRIGHT,bg=PANEL,wraplength=800,justify='left').pack(anchor='w',pady=8)
                self.btn(ci,('PREPARE VANILLA DATA (BETA)' if self.lang=='en' else 'PRZYGOTUJ DANE VANILLA (BETA)'),
                         lambda:self._extract_vanilla(selected),variant='green').pack(anchor='w',pady=4)

    def _pick_game(self):
        folder=filedialog.askdirectory(title=('Select Medieval II installation' if self.lang=='en' else 'Wybierz folder gry Medieval II'))
        if not folder:return
        game=find_game_root(folder)
        if not game:
            messagebox.showwarning('Medieval II',('No Medieval II installation found in this directory.' if self.lang=='en' else 'Nie rozpoznano instalacji Medieval II w tym katalogu.'))
            return
        self._open_campaign_picker(game)

    def _open_campaign_picker(self,game):
        options=list_campaign_choices(game)
        dlg=tk.Toplevel(self,bg=BG);dlg.title('Kruchyx — '+('Choose campaign' if self.lang=='en' else 'Wybierz kampanię'))
        dlg.geometry('690x555');dlg.transient(self);dlg.grab_set()
        box=tk.Frame(dlg,bg=BG,padx=24,pady=23);box.pack(fill='both',expand=True)
        self.lbl(box,'MEDIEVAL II / CAMPAIGN LIBRARY',13,GOLD_BRIGHT,'bold').pack(anchor='w')
        self.lbl(box,('Grand Campaign is always the first choice. Kingdoms and mods are listed below.' if self.lang=='en' else
                      'Pierwsza pozycja to zwykła kampania. Niżej kampanie Kingdoms i własne mody.'),
                 11,MUTED,bg=BG,wraplength=600,justify='left').pack(anchor='w',pady=(12,14))
        lb=tk.Listbox(box,bg=PANEL,fg=INK,selectbackground='#756342',selectforeground=INK,
                      relief='flat',font=(FONT,12),activestyle='none',highlightthickness=0)
        lb.pack(fill='both',expand=True)
        for option in options:lb.insert('end',option['label_en' if self.lang=='en' else 'label_pl'])
        lb.selection_set(0)
        def accept():
            if not lb.curselection():return
            option=options[lb.curselection()[0]]
            dlg.destroy()
            self.load_mod(option['path'],remember=True,allow_packed=(option['kind']=='vanilla'))
        lb.bind('<Double-Button-1>',lambda _e:accept())
        self.btn(box,('OPEN CAMPAIGN' if self.lang=='en' else 'OTWÓRZ KAMPANIĘ'),accept).pack(anchor='e',pady=14)
        dlg.wait_window()

    def _extract_vanilla(self,game):
        """Explicitly consented official extraction, isolated outside game install."""
        import threading
        exe=find_unpacker(game)
        if not exe or not list_packs(game):
            messagebox.showwarning('Vanilla',('Official unpacker.exe or .pack archives are missing.' if self.lang=='en' else
                                             'Nie znaleziono oficjalnego unpacker.exe lub archiwów .pack.'))
            return
        msg=(('The installed game extractor will copy selected definitions to:\n'+str(vanilla_cache_root(game))+
              '\nGame files will not be modified. Continue?') if self.lang=='en' else
             ('Uruchomimy ekstraktor gry. Definicje trafią wyłącznie do:\n'+str(vanilla_cache_root(game))+
              '\nNie zmienimy plików gry. Kontynuować?'))
        if not messagebox.askyesno('Vanilla data / Dane Vanilla',msg):return
        win=tk.Toplevel(self,bg=BG);win.title('Kruchyx — '+('Vanilla extraction' if self.lang=='en' else 'Odczyt Vanilla'))
        win.geometry('560x230')
        self.lbl(win,('Extracting official game data...' if self.lang=='en' else 'Odczytywanie danych z archiwów gry...'),
                 13,GOLD_BRIGHT,'bold',BG).pack(padx=22,pady=25)
        pb=ttk.Progressbar(win,mode='indeterminate',length=480);pb.pack(pady=5);pb.start(12)
        self.lbl(win,('May take some time. Do not launch other extractions.' if self.lang=='en' else
                      'Może chwilę potrwać. Nie uruchamiaj równocześnie kolejnych ekstrakcji.'),
                 10,MUTED,bg=BG).pack(padx=17,pady=12)
        def show_unpack_log(result):
            diag=tk.Toplevel(self,bg=BG)
            diag.title('Kruchyx — '+('Unpacker diagnostics' if self.lang=='en' else 'Diagnostyka rozpakowania'))
            diag.geometry('840x550')
            path=result.get('log_path')
            header=('EXTRACTION LOG' if self.lang=='en' else 'DZIENNIK ROZPAKOWANIA')
            self.lbl(diag,header,16,GOLD_BRIGHT,'bold',BG).pack(anchor='w',padx=18,pady=(16,5))
            hint=result.get('advice','')
            self.lbl(diag,hint,10,MUTED,bg=BG,wraplength=780).pack(anchor='w',padx=18,pady=(0,10))
            logfile=path.read_text(encoding='utf-8',errors='replace') if path and path.is_file() else '\n'.join(
                f"{d.get('filter')}: {d.get('returncode')}\n{d.get('log')}" for d in result.get('details',[]))
            area=tk.Text(diag,bg='#101d26',fg='#e7e5d8',insertbackground='#e7e5d8',wrap='word',
                         font=('Consolas',10),relief='flat')
            area.insert('1.0',logfile);area.configure(state='disabled')
            area.pack(fill='both',expand=True,padx=18,pady=8)
            def copy_log():
                diag.clipboard_clear();diag.clipboard_append(logfile)
                messagebox.showinfo('Kruchyx',('Log copied' if self.lang=='en' else 'Skopiowano dziennik błędów'),parent=diag)
            self.btn(diag,('COPY DIAGNOSTICS' if self.lang=='en' else 'KOPIUJ DIAGNOSTYKĘ'),copy_log,variant='gold').pack(anchor='e',padx=18,pady=(0,12))
        def done(result,error):
            pb.stop();win.destroy()
            if error:
                messagebox.showerror('Vanilla',str(error));return
            if result['success']:
                self.load_mod(game,remember=True,allow_packed=True)
                messagebox.showinfo('Vanilla',('Detected files: ' if self.lang=='en' else 'Wykryte pliki: ')+
                                    ', '.join(k for k,v in result['found'].items() if v))
                if not all(result['found'].values()):
                    show_unpack_log(result)
            else:
                messagebox.showwarning('Vanilla',('No usable files extracted. The diagnostic log will open.' if self.lang=='en' else
                                                 'Nie znaleziono wypakowanych plików. Otworzę dziennik diagnostyczny.')+
                                       '\n'+result.get('advice',''))
                show_unpack_log(result)
        def worker():
            try:result=unpack_vanilla(game);error=None
            except Exception as e:result=None;error=e
            self.after(0,lambda:done(result,error))
        threading.Thread(target=worker,daemon=True).start()

    def pick_folder(self):
        folder=filedialog.askdirectory(title='Wybierz Medieval II, mods, konkretny mod lub folder data')
        if not folder:return
        p=Path(folder)
        game=find_game_root(p)
        if game and p==game:
            self._open_campaign_picker(game);return
        options=[]
        for base in [p/'mods',p if p.name.lower()=='mods' else None]:
            if base and base.is_dir():
                options.extend(sorted(d for d in base.iterdir() if d.is_dir() and (d/'data').is_dir()))
        if len(options)==1:p=options[0]
        if len(options)>1:
            dlg=tk.Toplevel(self,bg=BG);dlg.title('Wybierz mod');dlg.geometry('630x460');dlg.transient(self);dlg.grab_set()
            box=tk.Frame(dlg,bg=BG,padx=20,pady=20);box.pack(fill='both',expand=True)
            self.lbl(box,'WYBIERZ MOD',17,GOLD_BRIGHT,'bold').pack(anchor='w',pady=(0,8))
            lb=tk.Listbox(box,bg=PANEL,fg=INK,selectbackground='#756342',selectforeground=INK,relief='flat',font=(FONT,11),activestyle='none')
            lb.pack(fill='both',expand=True)
            for f in options:lb.insert('end',f.name)
            lb.selection_set(0);choice=[]
            def accept():
                if lb.curselection():choice.append(options[lb.curselection()[0]])
                dlg.destroy()
            self.btn(box,'WYBIERZ',accept).pack(anchor='e',pady=10)
            dlg.wait_window()
            if not choice:return
            p=choice[0]
        self.load_mod(p,remember=True)

    def load_demo(self):
        self.load_mod(ROOT/'examples',remember=False)

    def load_mod(self,path,remember=False,allow_packed=False):
        try:
            model=analyze(path)
        except Exception as exc:
            messagebox.showerror('Nie udało się odczytać moda',f'{exc}\n\nSprawdź folder oraz dostęp do plików. Niczego nie zmieniono.');return
        if not any(model['context']['files'].values()) and not (model['context'].get('vanilla') and model['context'].get('packed_base')):
            messagebox.showwarning('Nie znaleziono plików','Ten folder nie zawiera rozpoznanych plików moda. Wybierz katalog data lub sam mod.');return
        self.model=model;self.active_path=Path(path).resolve()
        self.mod_sidebar.configure(text='Vanilla Kingdoms — DEMO' if self.active_path==ROOT/'examples' else self.active_path.name.replace('_',' ')[:46])
        if remember:
            self._prefs['last_mod']=str(self.active_path)
            self._persist()
        self.show('welcome')

    def _to_academy(self,lesson):
        self.current_lesson=lesson
        self.show('academy')

    def _persist(self):
        self._prefs['lang']=self.lang
        self._prefs['academy_checks']=self.completed
        try:SETTINGS.write_text(json.dumps(self._prefs,ensure_ascii=False,indent=2),encoding='utf-8')
        except OSError:pass

    def toggle_language(self):
        self.lang='en' if self.lang=='pl' else 'pl'
        self._persist()
        # Recreate navigation so all its labels are translated (and keep model state).
        for b in self.nav.values():b.destroy()
        self.nav.clear()
        for code,text in [
            ('welcome','  ✦   Strona główna'),('advisor','  ♛   Doradca frakcji'),
            ('units','  ⚔   Ranking jednostek'),('economy','  ♜   Gospodarka i kampania'),
            ('intelligence','  ◈   Łowca okazji'),('academy','  ✦   Akademia gracza'),('exploits','  ♠   Sekrety i exploity'),
            ('calculators','  ♛   Kalkulatory'),('trainer','  ⚡   Trainer i MAX'),('editor','  ⚒   Edytor moda'),
            ('saves','  ◈   Zapisy kampanii'),('library','  ▣   Biblioteka modów'),
            ('chronicles','  ◷   Kroniki kampanii'),('army','  ⚔   Kreator armii'),
            ('search','  ◈   Wyszukiwarka'),('mobile','  ▣   Kruchyx Mobile')]:
            b=tk.Button(self.sidebar,text=tr(text,self.lang),anchor='w',padx=17,pady=5,relief='flat',bd=0,
                        bg=SIDE,fg=INK,activebackground=PANEL2,activeforeground=GOLD_BRIGHT,
                        font=(FONT,10),highlightthickness=0,cursor='hand2',command=lambda c=code:self.show(c))
            b.pack(fill='x',padx=10,pady=1,before=self.nav_spacer)
            self.nav[code]=b
        self.lang_button.configure(text='EN → PL' if self.lang=='en' else 'PL → EN')
        self.change_mod_btn.configure(text=tr('ZMIEŃ MOD',self.lang))
        self.your_mod_label.configure(text=tr('TWÓJ MOD',self.lang))
        self.footer_label.configure(text=tr('Wykonane przez Kruchyx',self.lang))
        if self.active_path is None:self.mod_sidebar.configure(text=tr('Jeszcze nie wybrano',self.lang))
        self.title(f'{APP}  •  v{VERSION}  •  {tr("Wykonane przez Kruchyx",self.lang)}')
        self.show(self.page)

    def change_campaign(self,path):
        if self.active_path is None:return
        try:self.model=analyze(self.active_path,campaign_override=path)
        except Exception as exc:messagebox.showerror('Campaign / Kampania',str(exc));return
        self.show('economy')

    def _autoload(self):
        if not SETTINGS.is_file():return
        try:
            raw=json.loads(SETTINGS.read_text(encoding='utf-8'))
            p=Path(raw['last_mod'])
            if p.exists():self.load_mod(p,remember=False,allow_packed=True)
        except Exception:pass

    def export_report(self):
        if not self.model:return
        f=filedialog.asksaveasfilename(title='Zapisz raport Kruchyx',defaultextension='.txt',initialfile='Kruchyx_Raport_Moda.txt',filetypes=[('Raport tekstowy','*.txt')])
        if not f:return
        try:Path(f).write_text(report(self.model),encoding='utf-8')
        except OSError as exc:messagebox.showerror('Błąd zapisu',str(exc))
        else:messagebox.showinfo('Gotowe','Zapisano raport: '+str(f))

    def copy_report(self):
        if not self.model:return
        self.clipboard_clear();self.clipboard_append(report(self.model));self.update()
        messagebox.showinfo('Skopiowano','Podsumowanie strategiczne jest w schowku.')

    def open_classic(self):
        env=os.environ.copy()
        if self.active_path and self.active_path!=ROOT/'examples':env['KRUCHYX_ACTIVE_MOD']=str(self.active_path)
        try:
            cmd=([sys.executable,'--classic'] if getattr(sys,'frozen',False) else [sys.executable,str(ROOT/'studio081.py')])
            subprocess.Popen(cmd,cwd=ROOT,env=env)
        except OSError as exc:messagebox.showerror('Nie udało się uruchomić edytora',str(exc))

if __name__=='__main__':
    if os.name=='nt':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:pass
    if '--classic' in sys.argv:
        from studio081 import Studio
        Studio().mainloop()
    else:
        App().mainloop()
