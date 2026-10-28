"""Trainer Control Center for Medieval II — safe command generator."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from studio073 import Studio as Studio073
import trainer_core as tc

class Studio(Studio073):
    def __init__(self):
        super().__init__()
        self.title('MEDIEVAL // MOD STUDIO v0.7.8 — Trainer Control Center')
        self.build_trainer()

    def build_trainer(self):
        self.trainer_tab=ttk.Frame(self.tabs,padding=18)
        self.tabs.add(self.trainer_tab,text='⚡ TRAINER')
        ttk.Label(self.trainer_tab,text='KRUCHYX  //  TRAINER I MAX',style='Heading.TLabel').pack(anchor='w',pady=(0,8))
        ttk.Label(self.trainer_tab,text='Wybierz działanie → wpisz dane → przygotuj komendy → skopiuj do konsoli Medieval II. '
                  'Ta wersja NIE steruje procesem gry automatycznie.',wraplength=1200).pack(anchor='w',pady=(0,10))
        area=ttk.Frame(self.trainer_tab);area.pack(fill='both',expand=True)
        left=ttk.Frame(area);left.pack(side='left',fill='y',padx=(0,14))
        right=ttk.Frame(area);right.pack(side='left',fill='both',expand=True)
        self.mode=tk.StringVar(value='money')
        actions=[('💰 Pieniądze','money'),('⚔ Jednostki','unit'),('🏰 Budowa','building'),('👥 Ludność','population'),('🐎 Ruch generała','movement'),('🗺 Teleportacja','teleport'),('⭐ Cechy','trait'),('👁 Mgła wojny','fog'),('⌖ Współrzędne','coords'),('🏆 Wygrana atakującego','win_attack'),('🛡 Wygrana obrońcy','win_defend')]
        ttk.Label(left,text='KATEGORIE',style='Heading.TLabel').pack(anchor='w',pady=(0,6))
        for label,mode in actions:
            ttk.Radiobutton(left,text=label,value=mode,variable=self.mode,command=self.render_fields).pack(anchor='w',pady=4)
        ttk.Label(right,text='PARAMETRY',style='Heading.TLabel').pack(anchor='w',pady=(0,6))
        self.field_box=ttk.Frame(right);self.field_box.pack(fill='x')
        self.inputs={}; self.last_plan=None
        ttk.Button(right,text='1  ·  Przygotuj komendy',command=self.prepare).pack(anchor='w',pady=(12,8))
        ttk.Label(right,text='PODGLĄD KOMEND — każda linia jest osobnym poleceniem',style='Heading.TLabel').pack(anchor='w',pady=(4,8))
        text_box=ttk.Frame(right);text_box.pack(fill='both',expand=True)
        self.commands=tk.Text(text_box,height=13,wrap='none',font=('Consolas',11),background='#0b1720',foreground='#64edbc',insertbackground='#64edbc')
        self.commands.pack(side='left',fill='both',expand=True)
        bar=ttk.Scrollbar(text_box,command=self.commands.yview);bar.pack(side='right',fill='y');self.commands.configure(yscrollcommand=bar.set)
        buttons=ttk.Frame(right);buttons.pack(fill='x',pady=(9,5))
        ttk.Button(buttons,text='2  ·  Kopiuj wszystkie',command=self.copy_all).pack(side='left',padx=(0,8))
        ttk.Button(buttons,text='Kopiuj jedną linię',command=self.copy_line).pack(side='left',padx=(0,8))
        ttk.Button(buttons,text='Eksport TXT',command=self.export_commands).pack(side='left')
        self.trainer_status=tk.StringVar(value='Gotowe do przygotowania komend. Gra nie została zmodyfikowana.')
        ttk.Label(right,textvariable=self.trainer_status,wraplength=950).pack(anchor='w',pady=6)
        ttk.Label(right,text='INSTRUKCJA: 1. Uruchom kampanię. 2. Otwórz konsolę (~). 3. Skopiuj jedną linię i wklej, '
                  'zatwierdź Enter. 4. Powtórz dla kolejnych linii. Nie wklejaj wielu linii naraz.',wraplength=1100).pack(anchor='w',pady=(8,0))
        self.render_fields()

    def render_fields(self):
        for w in self.field_box.winfo_children():w.destroy()
        self.inputs={}
        spec={
            'money':[('Kwota do dodania','amount','1000000')],
            'unit':[('Miasto lub generał','target','London'),('ID jednostki (z EDU)','unit','Spear Militia'),('Liczba oddziałów 1–5','count','1'),('Doświadczenie 0–9','exp','5'),('Pancerz 0–3','armor','0'),('Broń 0–3','weapon','0')],
            'building':[('Miasto z kolejką budowy','city','London')],
            'population':[('Miasto','city','London'),('Dodaj mieszkańców','amount','1000')],
            'movement':[('Nazwa postaci','character','William')],
            'teleport':[('Nazwa postaci','character','William'),('Współrzędna X','x','100'),('Współrzędna Y','y','100')],
            'trait':[('Nazwa postaci','character','William'),('ID cechy','trait','GoodCommander'),('Poziom','level','1')]
        }.get(self.mode.get(),[])
        if not spec:
            ttk.Label(self.field_box,text='Ta opcja nie wymaga dodatkowych danych.').pack(anchor='w')
        for label,key,default in spec:
            row=ttk.Frame(self.field_box);row.pack(fill='x',pady=3)
            ttk.Label(row,text=label,width=30).pack(side='left')
            sv=tk.StringVar(value=default);entry=ttk.Entry(row,textvariable=sv,width=36);entry.pack(side='left',fill='x',expand=True)
            self.inputs[key]=sv
        self.commands.delete('1.0','end')
        self.last_plan=None
        self.trainer_status.set('Zmień parametry i kliknij „Przygotuj komendy”.')

    def prepare(self):
        get=lambda key:self.inputs[key].get()
        mode=self.mode.get()
        try:
            if mode=='money':plan=tc.money(get('amount'))
            elif mode=='unit':plan=tc.unit(get('target'),get('unit'),get('count'),get('exp'),get('armor'),get('weapon'))
            elif mode=='building':plan=tc.building(get('city'))
            elif mode=='population':plan=tc.population(get('city'),get('amount'))
            elif mode=='movement':plan=tc.movement(get('character'))
            elif mode=='teleport':plan=tc.teleport(get('character'),get('x'),get('y'))
            elif mode=='trait':plan=tc.trait(get('character'),get('trait'),get('level'))
            else:plan=tc.quick(mode)
        except tc.CommandError as exc:
            messagebox.showerror('Niepoprawne dane',str(exc));return
        self.last_plan=plan
        self.commands.delete('1.0','end');self.commands.insert('1.0',plan.as_text())
        self.trainer_status.set(f'{plan.label}: {len(plan.commands)} komend. {plan.caveat}')

    def copy_all(self):
        if not self.last_plan:
            messagebox.showinfo('Najpierw przygotuj komendy','Kliknij „Przygotuj komendy”.');return
        self.clipboard_clear();self.clipboard_append(self.last_plan.as_text());self.update()
        self.trainer_status.set(f'Skopiowano {len(self.last_plan.commands)} linii. W konsoli wklejaj je PO JEDNEJ.')

    def copy_line(self):
        text=self.commands.get('1.0','end-1c').splitlines()
        if not text:return
        index=int(self.commands.index('insert').split('.')[0])-1
        selected=text[max(0,min(index,len(text)-1))].strip()
        if not selected:return
        self.clipboard_clear();self.clipboard_append(selected);self.update()
        self.trainer_status.set('Skopiowano komendę: '+selected)

    def export_commands(self):
        if not self.last_plan:
            messagebox.showinfo('Najpierw przygotuj komendy','Kliknij „Przygotuj komendy”.');return
        path=filedialog.asksaveasfilename(defaultextension='.txt',filetypes=[('Tekst','*.txt')],initialfile='medieval_cheaty.txt')
        if path:
            try:tc.export_plan(path,self.last_plan)
            except (OSError,tc.CommandError) as exc:messagebox.showerror('Nie można wyeksportować',str(exc));return
            self.trainer_status.set('Wyeksportowano instrukcje do '+path)

if __name__=='__main__':
    Studio().mainloop()
