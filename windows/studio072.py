"""v0.7.2 - user-friendly save browser; safe read-only save inspection."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from studio071 import Studio as Studio071
from save_inspector import discover_saves, inspect_save

class Studio(Studio071):
    def __init__(self):
        super().__init__()
        self.title('MEDIEVAL // MOD STUDIO v0.7.2')
        self.build_save_tab()
        self.update_edu_warning()

    def update_edu_warning(self):
        if hasattr(self,'edu_diagnostic') and not getattr(self,'edu_file',None):
            self.edu_diagnostic.set('Brak dostępnego rozpakowanego export_descr_unit.txt. Ten mod może używać zasobów gry w archiwach .pack. Edytor EDU jest niedostępny do czasu wskazania poprawnego pliku; pozostałe funkcje działają normalnie.')

    def build_save_tab(self):
        self.save_tab=ttk.Frame(self.tabs,padding=16)
        self.tabs.add(self.save_tab,text='Zapisy kampanii · SAV')
        ttk.Label(self.save_tab,text='ZAPISY KAMPANII — BEZPIECZNY PODGLĄD',style='Heading.TLabel').pack(anchor='w',pady=(4,12))
        ttk.Label(self.save_tab,text='Wybierz zapis z listy. Odczyt nie zmienia pliku. Edycja binarnego SAV jest na razie zablokowana, aby nie uszkodzić kampanii.',wraplength=1100).pack(anchor='w',pady=(0,12))
        bar=ttk.Frame(self.save_tab);bar.pack(fill='x',pady=8)
        ttk.Button(bar,text='Znajdź zapisy',command=self.scan_saves).pack(side='left',padx=4)
        ttk.Button(bar,text='Otwórz plik SAV...',command=self.pick_save).pack(side='left',padx=4)
        ttk.Button(bar,text='Otwórz folder zapisów...',command=self.pick_save_folder).pack(side='left',padx=4)
        listing=ttk.Frame(self.save_tab);listing.pack(fill='both',expand=True)
        self.saves_tree=ttk.Treeview(listing,columns=('name','modified','size'),show='headings',height=12,selectmode='browse')
        for key,title,width in [('name','Nazwa zapisu',440),('modified','Data modyfikacji',185),('size','Rozmiar',125)]:
            self.saves_tree.heading(key,text=title);self.saves_tree.column(key,width=width)
        self.saves_tree.pack(side='left',fill='both',expand=True)
        scroll=ttk.Scrollbar(listing,orient='vertical',command=self.saves_tree.yview);scroll.pack(side='right',fill='y');self.saves_tree.configure(yscrollcommand=scroll.set)
        self.saves_tree.bind('<<TreeviewSelect>>',self.selected_save)
        self.save_details=tk.Text(self.save_tab,height=10,wrap='word',state='disabled')
        self.save_details.pack(fill='x',pady=(12,8))
        self.save_paths={}
        self.save_folder=None

    def pick_save(self):
        p=filedialog.askopenfilename(title='Wybierz save Medieval II',filetypes=[('Zapis kampanii','*.sav'),('Wszystkie pliki','*.*')])
        if p:self.populate_saves([Path(p)])
    def pick_save_folder(self):
        p=filedialog.askdirectory(title='Wybierz katalog zawierający pliki .sav')
        if p:
            self.save_folder=Path(p)
            self.populate_saves(sorted(self.save_folder.glob('*.sav'),key=lambda x:x.stat().st_mtime,reverse=True))
    def scan_saves(self):
        files=discover_saves(getattr(self,'data_dir',None))
        if self.save_folder and self.save_folder.is_dir():files+=list(self.save_folder.glob('*.sav'))
        self.populate_saves(list(dict.fromkeys(files)))
        if not files:messagebox.showinfo('Nie znaleziono zapisów','Nie znaleziono plików .sav w standardowych katalogach moda i gry. Kliknij „Otwórz folder zapisów...” i wybierz katalog ręcznie.')
    def populate_saves(self,paths):
        self.saves_tree.delete(*self.saves_tree.get_children());self.save_paths={}
        for n,p in enumerate(paths):
            try:
                info=inspect_save(p);iid=str(n)
                self.save_paths[iid]=Path(p)
                self.saves_tree.insert('', 'end', iid=iid,values=(p.name,info['modified'],f"{info['bytes']/1048576:.2f} MB"))
            except OSError:continue
        if self.save_paths:
            iid=next(iter(self.save_paths));self.saves_tree.selection_set(iid);self.selected_save()
    def selected_save(self,_event=None):
        sels=self.saves_tree.selection()
        if not sels:return
        try:
            item=inspect_save(self.save_paths[sels[0]])
            info=(f"NAZWA: {item['filename']}\n"
                  f"PLIK: {item['path']}\n"
                  f"MOD Z NAGŁÓWKA: {item['mod']}\n"
                  f"KAMPANIA: {item['campaign']}\n"
                  f"ZMIENIONO: {item['modified']}\n"
                  f"ROZMIAR: {item['bytes']:,} bajtów\n"
                  f"ROZPOZNANIE: {item['format']}\n\n"
                  'STAN: tylko do odczytu. Skarbiec, tura, armie i miasta nie są jeszcze wiarygodnie dekodowane.\n'
                  'Program nie zapisuje ani nie przerabia plików SAV.')
        except OSError as exc:info='Nie udało się odczytać pliku: '+str(exc)
        self.save_details.configure(state='normal');self.save_details.delete('1.0','end');self.save_details.insert('1.0',info);self.save_details.configure(state='disabled')
    def open_mod(self):
        super().open_mod()
        if hasattr(self,'saves_tree'):self.scan_saves()
        self.update_edu_warning()

if __name__=='__main__':Studio().mainloop()
