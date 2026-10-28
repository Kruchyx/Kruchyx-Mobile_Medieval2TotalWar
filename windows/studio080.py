"""v0.7.9: agent MAX packs layered on proven v0.7.8 trainer."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from studio078 import Studio as Studio078
from agent_presets import PRESETS, agent_plan
from trainer_core import export_plan
from game_bridge import paste_to_focused_game

class Studio(Studio078):
    def __init__(self):
        super().__init__()
        self.title('MEDIEVAL // MOD STUDIO v0.8.0 — QUICK COPY + ASSISTED PASTE')
        self.build_agent_tab()
        self.add_trainer_quick_controls()

    def add_trainer_quick_controls(self):
        section=ttk.Frame(self.trainer_tab,padding=10)
        section.pack(fill='x',before=self.trainer_tab.winfo_children()[0])
        ttk.Label(section,text='SZYBKI TRAINER — kopiowanie i asystowane wklejanie',style='Heading.TLabel').pack(side='left',padx=(0,12))
        ttk.Button(section,text='⚡ Generuj i kopiuj',command=self.quick_trainer_copy).pack(side='left',padx=(0,8))
        ttk.Button(section,text='Wklej do gry za 4 s',command=self.assisted_trainer_paste).pack(side='left')

    def quick_trainer_copy(self):
        self.last_plan=None
        self.prepare()
        if self.last_plan:self.copy_all()

    def assisted_trainer_paste(self):
        self.quick_trainer_copy()
        if not self.last_plan:return
        if not messagebox.askokcancel('Przekazanie do Medieval II',
            'Za 4 sekundy wyślę Ctrl+V do aktywnego okna gry.\n'
            'Przełącz się teraz do Medieval II i otwórz konsolę (~).\n'
            'Nie wciskam Enter ani nie weryfikuję wykonania komend. Kontynuować?'):
            return
        self.after(4000,lambda:self._perform_assisted_paste(self.trainer_status))
        self.trainer_status.set('Przejdź do konsoli gry — wklejanie za 4 sekundy...')

    def build_agent_tab(self):
        page=ttk.Frame(self.tabs,padding=18)
        self.tabs.add(page,text='★ MAX AGENTÓW')
        ttk.Label(page,text='PAKIETY MAX — GENERAŁ I WSZYSCY AGENCI',style='Heading.TLabel').pack(anchor='w',pady=(0,8))
        ttk.Label(page,text='Wybierz rodzaj agenta, wskaż postać i wygeneruj sprawdzone komendy. '
                  'To generator, nie live trainer. Nie zaznaczaj funkcji, których gra nie obsługuje.',wraplength=1050).pack(anchor='w',pady=(0,12))
        upper=ttk.Frame(page);upper.pack(fill='x')
        ttk.Label(upper,text='Rodzaj postaci',width=22).grid(row=0,column=0,sticky='w',pady=5)
        self.agent_kind=tk.StringVar(value='priest')
        self.agent_combo=ttk.Combobox(upper,state='readonly',width=40,textvariable=self.agent_kind,
            values=list(PRESETS.keys()))
        self.agent_combo.grid(row=0,column=1,sticky='ew',padx=8,pady=5)
        ttk.Label(upper,text='Nazwa postaci',width=22).grid(row=1,column=0,sticky='w',pady=5)
        self.agent_name=tk.StringVar(value='William')
        ttk.Entry(upper,textvariable=self.agent_name,width=42).grid(row=1,column=1,sticky='ew',padx=8,pady=5)
        self.agent_selected=tk.BooleanVar(value=True)
        ttk.Checkbutton(upper,text='Użyj aktualnie zaznaczonej postaci (this)',variable=self.agent_selected).grid(row=2,column=0,columnspan=2,sticky='w',pady=5)
        ttk.Label(upper,text='Uwaga: nazwa musi być jednoznaczna, jeśli wyłączysz „this”.').grid(row=3,column=0,columnspan=2,sticky='w',pady=4)
        upper.columnconfigure(1,weight=1)
        ttk.Button(page,text='★ Przygotuj zestaw MAX',command=self.generate_agents).pack(anchor='w',pady=12)
        ttk.Label(page,text='KOMENDY DO KONSOLI',style='Heading.TLabel').pack(anchor='w')
        self.agent_out=tk.Text(page,height=18,font=('Consolas',11),wrap='none',background='#0b1720',foreground='#64edbc',insertbackground='#64edbc')
        self.agent_out.pack(fill='both',expand=True,pady=8)
        self.agent_plan=None
        buttons=ttk.Frame(page);buttons.pack(fill='x',pady=6)
        ttk.Button(buttons,text='⚡ GENERUJ I KOPIUJ MAX',command=self.generate_and_copy_agent).pack(side='left',padx=(0,8))
        ttk.Button(buttons,text='Kopiuj wszystkie',command=self.copy_agent).pack(side='left',padx=(0,8))
        ttk.Button(buttons,text='Wklej do gry za 4 s',command=self.assisted_agent_paste).pack(side='left',padx=(0,8))
        ttk.Button(buttons,text='Eksportuj TXT',command=self.export_agent).pack(side='left')
        self.agent_status=tk.StringVar(value='Najpierw wybierz typ postaci i przygotuj komendy.')
        ttk.Label(page,textvariable=self.agent_status,wraplength=1050).pack(anchor='w',pady=6)
        ttk.Label(page,text='Pakiet „MAX” oznacza zestaw korzystnych cech, a nie automatyczne ustawienie wszystkich atrybutów na absolutne maksimum. '
                  'W przypadku KIRSI należy sprawdzić, czy ID i poziomy nadal istnieją.',wraplength=1200).pack(anchor='w',pady=6)

    def generate_agents(self):
        try:p=agent_plan(self.agent_kind.get(),self.agent_name.get(),self.agent_selected.get())
        except Exception as ex:messagebox.showerror('Niepoprawne dane',str(ex));return
        self.agent_plan=p
        self.agent_out.delete('1.0','end');self.agent_out.insert('1.0',p.as_text())
        self.agent_status.set(f'Wygenerowano {len(p.commands)} poleceń. '+p.caveat)

    def generate_and_copy_agent(self):
        self.agent_plan=None
        self.generate_agents()
        if self.agent_plan is not None:
            self.copy_agent()

    def assisted_agent_paste(self):
        self.generate_and_copy_agent()
        if not self.agent_plan:return
        if not messagebox.askokcancel('Wklej do konsoli gry',
              'Za 4 sekundy spróbuję wkleić zestaw do okna Medieval II.\n\n'
              'Teraz przejdź do gry, zaznacz postać i OTWÓRZ KONSOLĘ (~).\n'
              'Narzędzie nie otwiera konsoli, nie wciska Enter i nie czyta pamięci gry.\n'
              'Zestaw może nie działać, jeśli KIRSI zmienia nazwy cech. Kontynuować?'):
            return
        self.agent_status.set('Za 4 sekundy wklejanie — przejdź do otwartej konsoli Medieval II...')
        self.after(4000,lambda:self._perform_assisted_paste(self.agent_status))

    def _perform_assisted_paste(self,status):
        try:
            title=paste_to_focused_game()
            status.set('Wysłano Ctrl+V do okna: '+title+'. Sprawdź wynik w grze; nie potwierdzono wykonania komend.')
        except Exception as exc:
            status.set('Nie wysłano komend: '+str(exc))
            messagebox.showwarning('Wklejanie wstrzymane',str(exc))

    def copy_agent(self):
        if self.agent_plan is None:messagebox.showinfo('Najpierw wygeneruj','Przygotuj pakiet MAX.');return
        self.clipboard_clear();self.clipboard_append(self.agent_plan.as_text());self.update()
        self.agent_status.set('Skopiowano komendy. Wklej w konsoli gry i sprawdź rezultat na wybranej postaci.')

    def export_agent(self):
        if self.agent_plan is None:messagebox.showinfo('Najpierw wygeneruj','Przygotuj pakiet MAX.');return
        p=filedialog.asksaveasfilename(defaultextension='.txt',filetypes=[('Pliki tekstowe','*.txt')],initialfile='max_agent.txt')
        if p:export_plan(p,self.agent_plan);self.agent_status.set('Zapisano instrukcje TXT do '+p)

if __name__=='__main__':Studio().mainloop()
