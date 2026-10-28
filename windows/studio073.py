"""v0.7.3 adds an experimental read-only treasury card to SAV Explorer."""
import tkinter as tk
from tkinter import ttk
from studio072 import Studio as Studio072
from save_inspector import inspect_save
from treasury_probe import probe_treasury

class Studio(Studio072):
    def __init__(self):
        super().__init__()
        self.title('MEDIEVAL // MOD STUDIO v0.7.3 — Save Explorer')
        # The previous inspector's plain text block is retained, with readable summary above it.
        self.treasury_panel = ttk.Frame(self.save_tab)
        self.treasury_panel.pack(fill='x', before=self.save_details, pady=(8, 4))
        self.treasury_title = ttk.Label(self.treasury_panel, text='SKARBIEC — ODCZYT EKSPERYMENTALNY', style='Heading.TLabel')
        self.treasury_title.pack(anchor='w')
        self.treasury_value = ttk.Label(self.treasury_panel, text='Wybierz zapis kampanii')
        self.treasury_value.pack(anchor='w', pady=(4,2))
        self.treasury_hint = ttk.Label(self.treasury_panel, text='Pliki SAV pozostają wyłącznie do odczytu.', wraplength=1200)
        self.treasury_hint.pack(anchor='w')
        if self.saves_tree.selection(): self.selected_save()

    def selected_save(self, event=None):
        super().selected_save(event)
        if not hasattr(self, 'treasury_value'): return
        ids=self.saves_tree.selection()
        if not ids: return
        path=self.save_paths.get(ids[0])
        if not path: return
        try:
            info=inspect_save(path)
            result=probe_treasury(path) if info['campaign']=='imperial_campaign' else {'status':'unavailable','reason':'Nieznany format kampanii.'}
            if result['status']=='experimental':
                self.treasury_value.configure(text=f"{result['value']:,} florenów  ·  prawdopodobny skarbiec (Anglia / test KIRSI)".replace(',', ' '))
                self.treasury_hint.configure(text=f"Pozycja: {result['offset']} bajtów. {result['reason']} Tylko odczyt; nie jest to uniwersalny dekoder.")
            else:
                self.treasury_value.configure(text='Skarbiec: nie rozpoznano')
                self.treasury_hint.configure(text=result['reason'] + ' Nie będziemy zgadywać pieniędzy.')
        except Exception as exc:
            self.treasury_value.configure(text='Skarbiec: błąd odczytu')
            self.treasury_hint.configure(text=str(exc))

if __name__=='__main__':
    Studio().mainloop()
