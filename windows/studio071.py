"""v0.7.1: persistent history, restore points and EDU diagnostics."""
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from studio07 import Studio as Studio07
from history_store import History, edu_candidates
from modstudio import read_text, save_safely

class Studio(Studio07):
    def __init__(self):
        self.history=History()
        super().__init__()
        self.title('MEDIEVAL // MOD STUDIO v0.7.1')
        self.build_history_panel()
        self.build_edu_panel()
        self.refresh_history()

    def build_history_panel(self):
        parent=self.changes_tab
        frm=ttk.LabelFrame(parent,text='HISTORIA ZAPISÓW — zachowywana po zamknięciu programu',padding=10)
        frm.pack(fill='x',before=self.changes_view,pady=7)
        ttk.Label(frm,text='Każdy zapis tworzy trwały punkt przywracania. Wybierz wpis z listy, aby odtworzyć stan PRZED nim.',wraplength=1050).pack(anchor='w')
        outer=ttk.Frame(frm);outer.pack(fill='x',pady=6)
        self.history_tree=ttk.Treeview(outer,columns=('time','file','kind'),show='headings',height=7,selectmode='browse')
        for col,title,width in [('time','Data i godzina',185),('file','Zmodyfikowany plik',630),('kind','Rodzaj operacji',180)]:
            self.history_tree.heading(col,text=title);self.history_tree.column(col,width=width,anchor='w')
        self.history_tree.pack(side='left',fill='x',expand=True)
        sc=ttk.Scrollbar(outer,orient='vertical',command=self.history_tree.yview);sc.pack(side='right',fill='y');self.history_tree.configure(yscrollcommand=sc.set)
        bar=ttk.Frame(frm);bar.pack(fill='x')
        ttk.Button(bar,text='Odśwież historię',command=self.refresh_history).pack(side='left',padx=4)
        ttk.Button(bar,text='Przywróć stan sprzed wybranego zapisu',command=self.restore_selected).pack(side='left',padx=4)
        ttk.Button(bar,text='Przywróć pierwszy oryginał pliku',command=self.restore_original).pack(side='left',padx=4)
        ttk.Label(frm,text='Uwaga: przywracanie dotyczy jednego pliku. Każda operacja przywracania tworzy kolejny punkt historii.',style='Muted.TLabel').pack(anchor='w',pady=4)

    def build_edu_panel(self):
        p=self.unit_tab if hasattr(self,'unit_tab') else self.unit_adv_tab
        frm=ttk.LabelFrame(p,text='WYKRYWANIE PLIKU JEDNOSTEK EDU',padding=10)
        frm.pack(fill='x',padx=8,pady=8)
        ttk.Label(frm,text='Dokładna nazwa: export_descr_unit.txt  •  szukaj w data moda lub data głównej gry.').pack(anchor='w')
        self.edu_diagnostic=tk.StringVar(value='Nie sprawdzono')
        ttk.Label(frm,textvariable=self.edu_diagnostic,wraplength=1000).pack(anchor='w',pady=5)
        row=ttk.Frame(frm);row.pack(fill='x')
        ttk.Button(row,text='Znajdź EDU w modzie i grze',command=self.scan_edu).pack(side='left',padx=4)
        ttk.Button(row,text='Wskaż plik EDU ręcznie',command=self.choose_edu).pack(side='left',padx=4)
        ttk.Button(row,text='Utwórz kopię EDU w modzie',command=self.copy_edu_to_mod).pack(side='left',padx=4)

    def scan_edu(self):
        if not getattr(self,'data_dir',None):
            self.edu_diagnostic.set('Najpierw wybierz mod.');return
        choices=edu_candidates(self.data_dir)
        self.edu_matches=choices
        if choices:
            self.edu_diagnostic.set('Znaleziono: '+' | '.join(f'{label}: {path}' for path,label in choices))
            if choices[0][1]=='MOD':
                self.edu_file=choices[0][0]
                self.refresh();self.load_advanced()
            else:
                self.edu_file=None
                self.edu_diagnostic.set(self.edu_diagnostic.get()+'\nEDU jest poza modem. Kliknij «Utwórz kopię EDU w modzie» przed edycją.')
                self.refresh();self.load_advanced()
        else:
            self.edu_diagnostic.set('Brak rozpakowanego export_descr_unit.txt. Może być w archiwach .pack gry — nie da się edytować go bez wypakowania.')

    def choose_edu(self):
        name=filedialog.askopenfilename(title='Wybierz export_descr_unit.txt',filetypes=[('EDU','export_descr_unit.txt'),('TXT','*.txt')])
        if not name:return
        if Path(name).name.lower()!='export_descr_unit.txt':
            messagebox.showerror('Nieprawidłowy plik','Wybierz export_descr_unit.txt');return
        self.edu_file=Path(name).resolve()
        self.edu_diagnostic.set('Aktywny EDU: '+str(self.edu_file))
        self.refresh();self.load_advanced()

    def copy_edu_to_mod(self):
        data=getattr(self,'data_dir',None)
        source=getattr(self,'edu_file',None)
        if not source and getattr(self,'edu_matches',None):source=self.edu_matches[0][0]
        if not data or not source or not Path(source).is_file():
            messagebox.showwarning('Brak EDU','Najpierw znajdź lub wskaż istniejący EDU.');return
        dest=Path(data)/'export_descr_unit.txt'
        if source.resolve()==dest.resolve():
            messagebox.showinfo('EDU w modzie','Już edytujesz plik EDU w folderze moda.');return
        if dest.exists():
            messagebox.showerror('Istnieje już','W modzie jest już EDU — niczego nie nadpisano.');return
        if not messagebox.askyesno('Kopiowanie do moda',f'Skopiować EDU z:\n{source}\n\ndo:\n{dest}\n\nOryginał nie będzie modyfikowany?'):return
        shutil.copy2(source,dest);self.edu_file=dest
        self.edu_diagnostic.set('Utworzono lokalny EDU w modzie: '+str(dest))
        self.refresh();self.load_advanced()

    def refresh_history(self):
        if not hasattr(self,'history_tree'):return
        self.history_tree.delete(*self.history_tree.get_children())
        for entry in self.history.entries():
            self.history_tree.insert('', 'end', iid=entry['id'],values=(entry['time'],entry['path'],entry['kind']))

    def history_target(self):
        selection=self.history_tree.selection()
        if selection:return next((x for x in self.history.index if x['id']==selection[0]),None)
        messagebox.showinfo('Wybierz wpis','Najpierw zaznacz zapis w historii.');return None

    def restore_snapshot(self,path,snapshot,description):
        if self.pending:
            messagebox.showwarning('Oczekujące zmiany','Najpierw zapisz albo odrzuć oczekujące zmiany.');return
        if not messagebox.askyesno('Potwierdź przywrócenie',f'{description}\n\nPlik: {path}\n\nAktualny stan zostanie również zachowany w historii.') :return
        try:
            self.history.restore(path,snapshot,description)
            self.refresh();self.load_advanced();self.show_pending();self.refresh_history()
            messagebox.showinfo('Gotowe','Przywrócono wybraną wersję. Zapisano też poprzedni stan.')
        except Exception as exc:messagebox.showerror('Nie udało się przywrócić',str(exc))

    def restore_selected(self):
        entry=self.history_target()
        if entry:self.restore_snapshot(Path(entry['path']),Path(entry['before']),'Przywrócenie stanu sprzed '+entry['time'])

    def restore_original(self):
        entry=self.history_target()
        if not entry:return
        path=Path(entry['path']);original=self.history.original(path)
        if original:self.restore_snapshot(path,original,'Przywrócenie pierwszego oryginału')
        else:messagebox.showwarning('Brak','Nie ma zachowanej oryginalnej kopii tego pliku.')

    def _commit_all_core(self):
        if not self.pending:
            messagebox.showinfo('Brak zmian','Nie ma oczekujących zmian.');return
        if not messagebox.askyesno('Zapis','Zapisać '+str(len(self.pending))+' plik(ów)? Powstaną kopie i historia zmian.'):return
        done=[]
        try:
            # Validate all the source files before touching any.
            for path,item in self.pending.items():
                if read_text(path)[0]!=item['base']:raise ValueError(f'Plik został zmieniony poza aplikacją: {path}')
            for path,item in list(self.pending.items()):
                if item['base']==item['after']:continue
                before=Path(path).read_bytes()
                backup=save_safely(path,item['base'],item['after'],item['encoding'])
                done.append((path,backup,before,Path(path).read_bytes()))
            for path,backup,before,after in done:self.history.snapshot(path,before,after)
            self.undo_backups.extend((path,backup) for path,backup,_,_ in done)
            self.pending.clear();self.show_pending();self.refresh();self.load_advanced();self.refresh_history()
            messagebox.showinfo('Zapisano',f'Zapisano {len(done)} plik(ów). Punkty przywracania są dostępne po restarcie.')
        except Exception as exc:
            for path,backup,_,_ in reversed(done):
                if Path(backup).exists():shutil.copy2(backup,path)
            messagebox.showerror('Nie zapisano','Przywrócono wcześniejsze pliki. Szczegóły:\n'+str(exc))

    def _undo_last_core(self):
        if self.pending:
            messagebox.showwarning('Oczekujące zmiany','Najpierw zapisz albo odrzuć zmiany.');return
        entries=self.history.entries()
        if not entries:messagebox.showinfo('Historia','Brak zapisów w historii.');return
        e=entries[0]
        self.restore_snapshot(Path(e['path']),Path(e['before']),'Cofnięcie ostatniej operacji')

    def open_mod(self):
        super().open_mod()
        self.scan_edu()
        self.refresh_history()

if __name__=='__main__':Studio().mainloop()
