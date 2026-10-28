"""MEDIEVAL // MOD STUDIO v0.8.1 — rankings based on the selected mod's EDU."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from studio080 import Studio as Studio080
from unit_analytics import scan_mod,decode,parse_units,faction_ranking,parse_resources

class Studio(Studio080):
    def __init__(self):
        super().__init__()
        self.title('Kruchyx Medieval Mod Studios v0.9.2 — edytory klasyczne')
        self.build_rankings()
        self.after(350,self._detect_existing)
        import os
        if os.environ.get('KRUCHYX_ACTIVE_MOD'):
            self.after(700,self.open_mod)

    def build_rankings(self):
        tab=ttk.Frame(self.tabs,padding=14);self.tabs.add(tab,text='🏆 RANKING MODA')
        ttk.Label(tab,text='ANALIZATOR MODA  //  Wykonane przez Kruchyx',style='Heading.TLabel').pack(anchor='w')
        ttk.Label(tab,text='Ranking liczony z plików WYBRANEGO moda. To porównanie statystyk, nie symulacja bitwy ani gwarancja wygranej.',wraplength=1050).pack(anchor='w',pady=(6,9))
        bar=ttk.Frame(tab);bar.pack(fill='x',pady=(0,8))
        ttk.Button(bar,text='Wybierz folder moda / data / EDU',command=self.pick_analytics).pack(side='left')
        ttk.Button(bar,text='Analizuj aktualny mod',command=self.analyse_current).pack(side='left',padx=7)
        self.ana_status=tk.StringVar(value='Wskaż folder moda z plikiem export_descr_unit.txt. Analizator niczego nie modyfikuje.')
        ttk.Label(tab,textvariable=self.ana_status,wraplength=1100,style='Muted.TLabel').pack(anchor='w',pady=(0,9))
        opts=ttk.Frame(tab);opts.pack(fill='x',pady=5)
        ttk.Label(opts,text='Kategoria:').pack(side='left')
        self.ana_role=tk.StringVar(value='Frakcje — potencjał wojskowy')
        values=['Frakcje — potencjał wojskowy','Wszystkie jednostki','Piechota wręcz','Kawaleria wręcz','Piechota strzelecka','Kawaleria strzelecka','Okręty','Oblężnicze','Surowce handlowe']
        cb=ttk.Combobox(opts,values=values,textvariable=self.ana_role,state='readonly',width=35);cb.pack(side='left',padx=9);cb.bind('<<ComboboxSelected>>',lambda e:self.render_rankings())
        ttk.Label(opts,text='Filtr frakcji:').pack(side='left',padx=(15,4))
        self.ana_faction=tk.StringVar(value='Wszystkie')
        self.ana_faction_cb=ttk.Combobox(opts,textvariable=self.ana_faction,state='readonly',width=23,values=['Wszystkie']);self.ana_faction_cb.pack(side='left');self.ana_faction_cb.bind('<<ComboboxSelected>>',lambda e:self.render_rankings())
        ttk.Label(opts,text='Szukaj:').pack(side='left',padx=(15,4))
        self.ana_search=tk.StringVar();ttk.Entry(opts,textvariable=self.ana_search,width=22).pack(side='left');self.ana_search.trace_add('write',lambda *_:self.render_rankings())
        pan=ttk.Panedwindow(tab,orient='horizontal');pan.pack(fill='both',expand=True,pady=8)
        left=ttk.Frame(pan);right=ttk.Frame(pan);pan.add(left,weight=3);pan.add(right,weight=2)
        columns=('rank','name','score','extra')
        self.ana_tree=ttk.Treeview(left,columns=columns,show='headings',selectmode='browse')
        for key,label,w in [('rank','#',45),('name','Nazwa',250),('score','Ocena*',85),('extra','Dostępność / rola',230)]:
            self.ana_tree.heading(key,text=label);self.ana_tree.column(key,width=w,anchor='w')
        self.ana_tree.pack(side='left',fill='both',expand=True)
        vs=ttk.Scrollbar(left,command=self.ana_tree.yview);vs.pack(side='right',fill='y');self.ana_tree.config(yscrollcommand=vs.set)
        self.ana_tree.bind('<<TreeviewSelect>>',self.show_rank_detail)
        ttk.Label(right,text='DLACZEGO WARTO WYBRAĆ?',style='Heading.TLabel').pack(anchor='w',padx=10,pady=(2,9))
        self.ana_detail=tk.Text(right,height=20,wrap='word',font=('Consolas',10),bg='#0b1720',fg='#bdeadd',insertbackground='#54f8bc',state='disabled')
        self.ana_detail.pack(fill='both',expand=True,padx=10)
        ttk.Label(tab,text='* Ocena = umowny indeks statystyk EDU w danej roli. Frakcje: jakość dostępnych jednostek, NIE siła startowa, ekonomia ani dostępność budynków. Współczynniki są opisane w unit_analytics.py.',wraplength=1150,style='Muted.TLabel').pack(anchor='w')
        ttk.Label(tab,text='KRUCHYX MEDIEVAL MOD STUDIOS  •  Wykonane przez Kruchyx',style='Muted.TLabel').pack(anchor='e',pady=(6,0))
        self.ana_units=[];self.ana_factions=[];self.ana_rows=[];self.ana_resources=[]

    def _detect_existing(self):
        if getattr(self,'data_dir',None):self.analyse_current(silent=True)

    def open_mod(self):
        super().open_mod()
        self.analyse_current(silent=True)

    def pick_analytics(self):
        p=filedialog.askdirectory(title='Wskaż folder moda lub data (możesz też wskazać EDU poniżej)')
        if not p:return
        try:self.load_rankings(p)
        except Exception as e:
            if messagebox.askyesno('EDU nie znaleziono',str(e)+'\n\nWskazać export_descr_unit.txt ręcznie?'):
                f=filedialog.askopenfilename(filetypes=[('Export Descr Unit','export_descr_unit.txt'),('Tekst','*.txt')]);
                if f:self.load_rankings(f)

    def analyse_current(self,silent=False):
        root=getattr(self,'data_dir',None) or getattr(self,'root_dir',None)
        if not root:
            if not silent:messagebox.showinfo('Brak moda','Najpierw wybierz folder moda albo wskaż EDU.')
            return
        try:self.load_rankings(root)
        except Exception as e:
            self.ana_status.set(str(e))
            if not silent:messagebox.showwarning('Brak danych',str(e))

    def load_rankings(self,path):
        edu,root=scan_mod(path)
        units=parse_units(decode(edu))
        if not units:raise ValueError('EDU nie zawiera poprawnych definicji jednostek.')
        self.ana_units=units;self.ana_factions=faction_ranking(units)
        self.ana_resources=[]
        res=root/'descr_sm_resources.txt'
        if res.is_file():self.ana_resources=parse_resources(decode(res))
        owners=sorted(set(o for u in units for o in u['owners']))
        self.ana_faction_cb['values']=['Wszystkie']+owners
        self.ana_faction.set('Wszystkie')
        self.ana_status.set(f'✓ {edu}  |  {len(units)} jednostek, {len(owners)} identyfikatorów frakcji  |  Tylko odczyt')
        self.render_rankings()
        self.tabs.select(self.tabs.index(self.ana_tree.master.master.master)) if False else None

    def render_rankings(self):
        self.ana_tree.delete(*self.ana_tree.get_children());self.ana_rows=[]
        mode=self.ana_role.get();owner=self.ana_faction.get();query=self.ana_search.get().casefold().strip()
        if mode=='Surowce handlowe':
            rows=[r for r in self.ana_resources if query in r['name'].casefold()]
            self.ana_rows=rows
            for i,r in enumerate(rows,1):self.ana_tree.insert('', 'end',iid=str(i-1),values=(i,r['name'],r['value'],'trade_value, nie dochód'))
        elif mode.startswith('Frakcje'):
            rows=[r for r in self.ana_factions if (owner=='Wszystkie' or owner==r['name']) and query in r['name'].casefold()]
            self.ana_rows=rows
            for i,r in enumerate(rows,1):self.ana_tree.insert('', 'end',iid=str(i-1),values=(i,r['name'],r['score'],f"{r['count']} jednostek / {r['roles']} role"))
        else:
            rows=[u for u in self.ana_units if (mode=='Wszystkie jednostki' or u['role']==mode) and (owner=='Wszystkie' or owner in u['owners']) and (query in u['name'].casefold())]
            rows.sort(key=lambda u:-u['score'])
            self.ana_rows=rows
            for i,u in enumerate(rows,1):self.ana_tree.insert('', 'end',iid=str(i-1),values=(i,u['name'],u['score'],', '.join(u['owners'][:3])))
        self._detail('Wybierz pozycję z rankingu, aby zobaczyć statystyki i uzasadnienie.\n\nNie ma jednego obiektywnie najmocniejszego oddziału: ważna jest rola, przeciwnik, teren, koszt i dostępność.')

    def _detail(self,s):
        self.ana_detail.config(state='normal');self.ana_detail.delete('1.0','end');self.ana_detail.insert('1.0',s);self.ana_detail.config(state='disabled')

    def show_rank_detail(self,event=None):
        sel=self.ana_tree.selection()
        if not sel:return
        row=self.ana_rows[int(sel[0])]
        if 'value' in row:
            self._detail(f"SUROWIEC: {row['name']}\n\nWartość handlowa trade_value: {row['value']:g}\n\nTa wartość pochodzi z descr_sm_resources.txt. Sama w sobie nie oznacza dochodu na turę ani liczby złóż na mapie.")
        elif 'best' in row:
            best='\n'.join('  • '+x['name']+' ('+x['role']+', indeks '+str(x['score'])+')' for x in row['best'])
            self._detail(f"FRAKCJA: {row['name']}\n\nOcena potencjału wojskowego: {row['score']}\nJednostek w EDU: {row['count']}\nObsadzone role: {row['roles']}/4\n\nNajwyżej oceniane jednostki (różne role nie są bezpośrednio porównywalne):\n{best}\n\nUwaga: brak danych o armiach startowych, budynkach i sytuacji na mapie. To ranking rosteru, nie startowej potęgi.")
        else:
            u=row
            strengths=[]
            if u['armour_piercing']:strengths.append('Przebija pancerz')
            if u['charge']>=7:strengths.append('Mocna szarża')
            if u['morale']>=10:strengths.append('Wysokie morale')
            if u['defence']>=18:strengths.append('Wysoka obrona')
            if u['range']>=150:strengths.append('Duży zasięg')
            if u['health']>=2:strengths.append('Więcej punktów zdrowia')
            t=f"{u['name']}\n{u['role']}\n\nAtak: {u['attack']:g}   Szarża: {u['charge']:g}\nObrona*: {u['defence']:g}   Morale: {u['morale']:g}\nŻycie: {u['health']:g}   Zasięg: {u['range']:g}\nRekrutacja: {u['cost']:g}   Utrzymanie: {u['upkeep']:g}\nWielkość oddziału (EDU): {u['size']:g}\n\nMOCNE STRONY\n"+('\n'.join('• '+x for x in strengths) if strengths else 'Brak szczególnych przewag wykrytych z prostych statystyk')+f"\n\nFrakcje: {', '.join(u['owners'])}\n\nOcena w roli: {u['score']}\n\n*Obrona = suma 3 pól stat_pri_armour. Ocena jest heurystyczna, nie wynikiem testu bitwy."
            self._detail(t)

if __name__=='__main__':Studio().mainloop()
