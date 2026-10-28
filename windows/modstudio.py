#!/usr/bin/env python3
"""Medieval II Mod Studio — offline, non-destructive editor MVP."""
import difflib
import os
import re
import shutil
import tempfile
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

CAMPAIGN = Path('data/world/maps/campaign/imperial_campaign/descr_strat.txt')
EDU = Path('data/export_descr_unit.txt')


def resolve_data_folder(folder):
    folder = Path(folder)
    if folder.name.lower() == 'data' and folder.is_dir():
        return folder
    candidate = folder / 'data'
    if candidate.is_dir():
        return candidate
    return None


def campaign_paths(data_folder):
    base = data_folder / 'world' / 'maps' / 'campaign'
    if not base.is_dir():
        return []
    return sorted(base.glob('*/descr_strat.txt'), key=lambda p: (p.parent.name != 'imperial_campaign', str(p).lower()))



def read_text(path):
    raw = path.read_bytes()
    for encoding in (('utf-8-sig',) if raw.startswith(b'\xef\xbb\xbf') else ()) + ('utf-8', 'cp1250', 'cp1252'):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise ValueError('Nieznane kodowanie')


def to_bytes(text, encoding):
    return text.encode(encoding)


def edit_money(text, faction, amount):
    """Edit denari ONLY inside a faction block, preserving other text."""
    heads = list(re.finditer(r'(?im)^[ \t]*faction[ \t]+([a-z_][\w]*)[ \t]*,[^\r\n]*', text))
    for ix, hit in enumerate(heads):
        if hit.group(1).lower() != faction.lower():
            continue
        end = heads[ix+1].start() if ix+1 < len(heads) else len(text)
        chunk = text[hit.end():end]
        match = re.search(r'(?im)^([ \t]*denari[ \t]+)(-?\d+)([^\r\n]*)', chunk)
        if not match:
            raise ValueError(f'Brak pola denari w sekcji {faction}.')
        start = hit.end() + match.start(2)
        stop = hit.end() + match.end(2)
        return text[:start] + str(amount) + text[stop:]
    raise ValueError(f'Nie znaleziono sekcji frakcji: {faction}.')


def money_options(text):
    result = []
    matches = list(re.finditer(r'(?im)^[ \t]*faction[ \t]+([a-z_][\w]*)[ \t]*,[^\r\n]*', text))
    for i, match in enumerate(matches):
        block = text[match.end():matches[i+1].start() if i+1 < len(matches) else len(text)]
        money = re.search(r'(?im)^\s*denari\s+(-?\d+)', block)
        if money:
            result.append((match.group(1), int(money.group(1))))
    return result


def faction_field_options(text, field):
    result=[]
    heads=list(re.finditer(r'(?im)^[ \t]*faction[ \t]+([a-z_][\w]*)[ \t]*,[^\r\n]*',text))
    for i,head in enumerate(heads):
        part=text[head.end():heads[i+1].start() if i+1<len(heads) else len(text)]
        match=re.search(r'(?im)^\s*'+re.escape(field)+r'\s+(-?\d+)\b',part)
        if match:result.append((head.group(1),int(match.group(1))))
    return result


def edit_faction_field(text,faction,field,value):
    if field not in ('denari','denari_kings_purse'):
        raise ValueError('Nieobsługiwane pole frakcji.')
    heads=list(re.finditer(r'(?im)^[ \t]*faction[ \t]+([a-z_][\w]*)[ \t]*,[^\r\n]*',text))
    for i,head in enumerate(heads):
        if head.group(1).lower()!=faction.lower():continue
        end=heads[i+1].start() if i+1<len(heads) else len(text)
        part=text[head.end():end]
        found=re.search(r'(?im)^(\s*'+re.escape(field)+r'\s+)(-?\d+)\b',part)
        if not found:raise ValueError(f'Frakcja {faction} nie ma pola {field}.')
        a=head.end()+found.start(2);b=head.end()+found.end(2)
        return text[:a]+str(value)+text[b:]
    raise ValueError('Nie znaleziono frakcji.')


def settlement_options(text):
    # Locate settlement blocks via balanced braces, so nested building blocks do not leak.
    result=[]
    for match in re.finditer(r'(?im)^\s*settlement(?:_castle)?\s*\{',text):
        begin=match.end()-1;depth=0;end=None
        for i in range(begin,len(text)):
            if text[i]=='{':depth+=1
            elif text[i]=='}':
                depth-=1
                if depth==0:end=i+1;break
        if end is None:continue
        part=text[begin:end]
        region=re.search(r'(?im)^\s*region\s+([^\r\n;]+)',part)
        pop=re.search(r'(?im)^\s*population\s+(\d+)',part)
        if region and pop:result.append((region.group(1).strip(),int(pop.group(1)),match.start(),end))
    return result


def edit_settlement_population(text,region,value):
    for name,pop,start,end in settlement_options(text):
        if name!=region:continue
        part=text[start:end]
        match=re.search(r'(?im)^(\s*population\s+)(\d+)\b',part)
        if match is None:break
        a=start+match.start(2);b=start+match.end(2)
        return text[:a]+str(value)+text[b:]
    raise ValueError('Nie znaleziono osady lub pola population.')


def edit_campaign_year(text,field,value):
    if field not in ('start_date','end_date'):raise ValueError('Niedozwolone pole.')
    found=re.search(r'(?im)^(\s*'+field+r'\s+)(-?\d+)\b',text)
    if not found:raise ValueError('Brak pola '+field+' w pliku.')
    return text[:found.start(2)]+str(value)+text[found.end(2):]


def edu_units(text):
    units = []
    hits = list(re.finditer(r'(?im)^type\s+(.+?)\s*$', text))
    for i, hit in enumerate(hits):
        part = text[hit.end():hits[i+1].start() if i+1<len(hits) else len(text)]
        cost = re.search(r'(?im)^stat_cost\s+([^\r\n;]+)', part)
        if cost:
            nums = [v.strip() for v in cost.group(1).split(',')]
            if len(nums) >= 3:
                units.append((hit.group(1).strip(), nums[1], nums[2]))
    return units


def edit_unit_cost(text, unit, recruitment, upkeep):
    hits = list(re.finditer(r'(?im)^type\s+(.+?)\s*$', text))
    for i, hit in enumerate(hits):
        if hit.group(1).strip() != unit:
            continue
        end = hits[i+1].start() if i+1<len(hits) else len(text)
        block = text[hit.end():end]
        line = re.search(r'(?im)^(stat_cost\s+)([^\r\n;]+)', block)
        if not line:
            raise ValueError('Brak stat_cost w jednostce.')
        vals = line.group(2).split(',')
        if len(vals) < 3:
            raise ValueError('Nieprawidłowe stat_cost.')
        for idx, value in ((1, recruitment),(2, upkeep)):
            ws = re.match(r'\s*', vals[idx]).group()
            vals[idx] = ws + str(value)
        start = hit.end() + line.start(2)
        stop = hit.end() + line.end(2)
        return text[:start] + ','.join(vals) + text[stop:]
    raise ValueError('Nie znaleziono jednostki.')


def save_safely(path, old_text, new_text, encoding):
    if old_text == new_text:
        raise ValueError('Brak zmian do zapisu.')
    if path.read_bytes() != to_bytes(old_text, encoding):
        raise ValueError('Plik został zmieniony z zewnątrz. Odśwież dane.')
    backup = path.with_name(path.name + '.' + datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.bak')
    shutil.copy2(path, backup)
    fd, name = tempfile.mkstemp(prefix='.modstudio_', dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as fp:
            fp.write(to_bytes(new_text,encoding))
            fp.flush()
            os.fsync(fp.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)
    return backup


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Medieval II Mod Studio — 0.4')
        self.geometry('1100x740')
        self.minsize(770,580)
        self.root_dir = None
        self.data_dir = None
        self.campaign_file = None
        self.edu_file = None
        self.current = None
        self.options = []
        self.unit_options = []
        self.status = tk.StringVar(value='Wybierz folder data moda lub folder gry/moda z katalogiem data.')
        bar = ttk.Frame(self,padding=12)
        bar.pack(fill='x')
        ttk.Button(bar,text='Wybierz folder DATA / moda',command=self.open_mod).pack(side='left')
        self.folder_label = ttk.Label(bar,text='  Nie wybrano folderu')
        self.folder_label.pack(side='left',fill='x',expand=True)
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both',expand=True,padx=12,pady=(0,8))
        self.campaign_tab = ttk.Frame(self.tabs,padding=15)
        self.edu_tab = ttk.Frame(self.tabs,padding=15)
        self.tabs.add(self.campaign_tab,text='Kampania · descr_strat')
        self.tabs.add(self.edu_tab,text='Jednostki · EDU')
        self.files_tab = ttk.Frame(self.tabs,padding=12)
        self.tabs.add(self.files_tab,text='Przeglądarka plików TXT')
        self.build_files_tab()
        self.build_campaign()
        self.build_edu()
        ttk.Label(self,textvariable=self.status,relief='sunken',padding=7).pack(side='bottom',fill='x')

    def build_files_tab(self):
        ttk.Label(self.files_tab,text='Przeglądaj i edytuj pliki tekstowe moda',font=('Segoe UI',13,'bold')).pack(anchor='w')
        ttk.Label(self.files_tab,text='Pliki są wyszukiwane w wybranym katalogu data i podfolderach. Plik musi istnieć fizycznie na dysku; pliki zapakowane w archiwach gry nie są tu widoczne.',wraplength=920).pack(anchor='w',pady=(4,8))
        bar=ttk.Frame(self.files_tab);bar.pack(fill='x',pady=(0,6))
        ttk.Button(bar,text='Odśwież listę',command=self.refresh_files).pack(side='left')
        ttk.Button(bar,text='Otwórz dowolny plik TXT...',command=self.pick_text_file).pack(side='left',padx=6)
        ttk.Label(bar,text='Filtr nazwy:').pack(side='left',padx=(14,4))
        self.file_filter=tk.StringVar()
        e=ttk.Entry(bar,textvariable=self.file_filter,width=28);e.pack(side='left')
        self.file_filter.trace_add('write',lambda *_:self.apply_file_filter())
        ttk.Button(bar,text='Edytuj w odpowiedniej zakładce →',command=self.route_open_file).pack(side='right',padx=8)
        ttk.Button(bar,text='Zapisz z kopią .bak',command=self.save_text_file).pack(side='right')
        split=ttk.Panedwindow(self.files_tab,orient='horizontal');split.pack(fill='both',expand=True)
        left=ttk.Frame(split);right=ttk.Frame(split)
        split.add(left,weight=1);split.add(right,weight=4)
        self.file_list=tk.Listbox(left,exportselection=False,width=37)
        scroll=ttk.Scrollbar(left,orient='vertical',command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=scroll.set)
        self.file_list.pack(side='left',fill='both',expand=True);scroll.pack(side='right',fill='y')
        self.file_list.bind('<<ListboxSelect>>',self.on_file_selected)
        self.current_file_label=ttk.Label(right,text='Wybierz plik z listy',wraplength=650)
        self.current_file_label.pack(anchor='w',pady=(0,6))
        holder=ttk.Frame(right);holder.pack(fill='both',expand=True)
        self.text_editor=tk.Text(holder,wrap='none',font=('Consolas',10),undo=True)
        y=ttk.Scrollbar(holder,orient='vertical',command=self.text_editor.yview)
        x=ttk.Scrollbar(right,orient='horizontal',command=self.text_editor.xview)
        self.text_editor.configure(yscrollcommand=y.set,xscrollcommand=x.set)
        self.text_editor.pack(side='left',fill='both',expand=True);y.pack(side='right',fill='y');x.pack(fill='x')
        self.text_file_path=None
        self.text_original=''
        self.text_encoding=None
        self.all_text_files=[]
        self.filtered_text_files=[]

    def refresh_files(self):
        base=self.data_dir
        if base is None:return
        extensions={'.txt','.cfg','.ini','.lua','.xml','.json','.log'}
        try:
            self.all_text_files=sorted((p for p in base.rglob('*') if p.is_file() and p.suffix.lower() in extensions),key=lambda p:str(p).lower())
            self.apply_file_filter()
            self.status.set(f'Znaleziono {len(self.all_text_files)} plików tekstowych w {base}')
        except Exception as exc:
            messagebox.showerror('Błąd skanowania',str(exc))

    def apply_file_filter(self):
        if not hasattr(self,'file_list'):return
        needle=self.file_filter.get().lower()
        base=self.data_dir
        self.filtered_text_files=[p for p in self.all_text_files if needle in str(p.relative_to(base)).lower()]
        self.file_list.delete(0,'end')
        for p in self.filtered_text_files:self.file_list.insert('end',str(p.relative_to(base)))

    def on_file_selected(self,event=None):
        selected=self.file_list.curselection()
        if selected:self.open_text_file(self.filtered_text_files[selected[0]])

    def pick_text_file(self):
        path=filedialog.askopenfilename(title='Wybierz plik tekstowy',initialdir=str(self.data_dir or Path.home()),filetypes=[('Pliki tekstowe','*.txt *.cfg *.ini *.lua *.xml *.json *.log'),('Wszystkie pliki','*.*')])
        if path:self.open_text_file(Path(path))

    def open_text_file(self,path):
        if self.text_file_path is not None and self.text_editor.get('1.0','end-1c')!=self.text_original:
            if not messagebox.askyesno('Niezapisane zmiany','Odrzucić niezapisane zmiany i otworzyć inny plik?'):
                return
        try:
            content,encoding=read_text(path)
        except Exception as exc:
            messagebox.showerror('Nie można odczytać pliku',str(exc));return
        self.text_file_path=path;self.text_original=content;self.text_encoding=encoding
        self.text_editor.delete('1.0','end');self.text_editor.insert('1.0',content)
        self.text_editor.edit_reset()
        self.current_file_label.configure(text=f'{path}  |  kodowanie: {encoding}')
        self.status.set(f'Odczytano: {path.name}')
        # Otwierając znany plik, łączymy go z edytorem strukturalnym.
        if path.name.lower() in ('descr_strat.txt','export_descr_unit.txt'):
            self.route_open_file()

    def route_open_file(self):
        path=self.text_file_path
        if path is None:
            messagebox.showinfo('Najpierw wybierz plik','Kliknij plik w przeglądarce.')
            return
        if self.text_editor.get('1.0','end-1c') != self.text_original:
            messagebox.showwarning('Niezapisane zmiany', 'Zapisz zmiany w przeglądarce przed przejściem do edytora formularzy.')
            return
        name=path.name.lower()
        if name=='descr_strat.txt':
            self.campaign_file=path
            self.refresh()
            self.tabs.select(self.campaign_tab)
            self.status.set('Załadowano descr_strat.txt do edytora kampanii')
        elif name=='export_descr_unit.txt':
            self.edu_file=path
            self.refresh()
            self.tabs.select(self.edu_tab)
            self.status.set('Załadowano EDU do edytora jednostek')
        else:
            messagebox.showinfo('Edytor tekstowy','Dla tego pliku nie ma jeszcze formularza. Możesz modyfikować go bezpośrednio w przeglądarce.')

    def save_text_file(self):
        if not self.text_file_path:
            messagebox.showwarning('Brak pliku','Najpierw wybierz plik tekstowy.');return
        new=self.text_editor.get('1.0','end-1c')
        try:
            backup=save_safely(self.text_file_path,self.text_original,new,self.text_encoding)
            self.text_original=new
            self.status.set(f'Zapisano {self.text_file_path.name}; kopia: {backup.name}')
            messagebox.showinfo('Zapisano',f'Plik zapisany.\nKopia zapasowa: {backup}')
        except Exception as exc:
            messagebox.showerror('Nie zapisano',str(exc))

    def make_editor(self, parent):
        controls=ttk.Frame(parent)
        controls.pack(fill='x',pady=10)
        preview=tk.Text(parent,wrap='none',height=20,font=('Consolas',10),undo=False)
        preview.pack(fill='both',expand=True)
        preview.configure(state='disabled')
        return controls, preview

    def build_campaign(self):
        ttk.Label(self.campaign_tab,text='Zmień skarbiec początkowy frakcji (nowa kampania)',font=('Segoe UI',13,'bold')).pack(anchor='w')
        ttk.Label(self.campaign_tab,text='Zmiany zachowują format pliku. Przed zapisem zobaczysz różnice.',wraplength=730).pack(anchor='w',pady=(4,0))
        source=ttk.Frame(self.campaign_tab)
        source.pack(fill='x',pady=(10,0))
        ttk.Label(source,text='Plik kampanii:').pack(side='left')
        self.campaign_path_label=ttk.Label(source,text='Nie wybrano',width=65)
        self.campaign_path_label.pack(side='left',padx=7)
        ttk.Button(source,text='Wybierz descr_strat...',command=self.choose_campaign).pack(side='right')
        line=ttk.Frame(self.campaign_tab)
        line.pack(fill='x',pady=12)
        ttk.Label(line,text='Frakcja:').pack(side='left')
        self.faction=tk.StringVar()
        self.faction_combo=ttk.Combobox(line,textvariable=self.faction,width=26,state='readonly')
        self.faction_combo.pack(side='left',padx=10)
        self.faction_combo.bind('<<ComboboxSelected>>',self.faction_changed)
        ttk.Label(line,text='Floreny:').pack(side='left')
        self.money=tk.StringVar()
        ttk.Entry(line,textvariable=self.money,width=18).pack(side='left',padx=10)
        ttk.Button(line,text='Pokaż zmiany',command=lambda:self.preview_change('campaign')).pack(side='left')
        ttk.Button(line,text='Zapisz z kopią .bak',command=lambda:self.commit('campaign')).pack(side='left',padx=8)
        extra=ttk.LabelFrame(self.campaign_tab,text='Dodatkowe opcje descr_strat.txt',padding=10)
        extra.pack(fill='x',pady=(2,10))
        r1=ttk.Frame(extra);r1.pack(fill='x',pady=3)
        ttk.Label(r1,text='Królewska sakiewka:').pack(side='left')
        self.purse=tk.StringVar()
        ttk.Entry(r1,textvariable=self.purse,width=14).pack(side='left',padx=7)
        ttk.Button(r1,text='Podgląd',command=lambda:self.preview_extra('purse')).pack(side='left',padx=4)
        ttk.Button(r1,text='Zapisz',command=lambda:self.commit_extra('purse')).pack(side='left')
        r2=ttk.Frame(extra);r2.pack(fill='x',pady=3)
        ttk.Label(r2,text='Osada / region:').pack(side='left')
        self.region=tk.StringVar()
        self.region_combo=ttk.Combobox(r2,textvariable=self.region,width=30,state='readonly')
        self.region_combo.pack(side='left',padx=6)
        self.region_combo.bind('<<ComboboxSelected>>',self.region_changed)
        ttk.Label(r2,text='Populacja:').pack(side='left')
        self.population=tk.StringVar()
        ttk.Entry(r2,textvariable=self.population,width=13).pack(side='left',padx=6)
        ttk.Button(r2,text='Podgląd',command=lambda:self.preview_extra('population')).pack(side='left',padx=4)
        ttk.Button(r2,text='Zapisz',command=lambda:self.commit_extra('population')).pack(side='left')
        r3=ttk.Frame(extra);r3.pack(fill='x',pady=3)
        ttk.Label(r3,text='Rok kampanii:').pack(side='left')
        self.year_field=tk.StringVar(value='start_date')
        ttk.Combobox(r3,textvariable=self.year_field,values=['start_date','end_date'],width=15,state='readonly').pack(side='left',padx=6)
        self.year_value=tk.StringVar()
        ttk.Entry(r3,textvariable=self.year_value,width=13).pack(side='left',padx=6)
        ttk.Button(r3,text='Podgląd',command=lambda:self.preview_extra('year')).pack(side='left',padx=4)
        ttk.Button(r3,text='Zapisz',command=lambda:self.commit_extra('year')).pack(side='left')
        ttk.Label(extra,text='Uwaga: modyfikowanie roku i osad zwykle wymaga nowej kampanii. Zapis tworzy .bak.').pack(anchor='w',pady=(5,0))
        ttk.Label(self.campaign_tab,text='Podgląd różnic (− stara wartość, + nowa):').pack(anchor='w')
        _,self.diff_campaign=self.make_editor(self.campaign_tab)

    def build_edu(self):
        ttk.Label(self.edu_tab,text='Koszt rekrutacji i utrzymania jednostek',font=('Segoe UI',13,'bold')).pack(anchor='w')
        ttk.Label(self.edu_tab,text='Zmiana stat_cost dotyczy wybranej jednostki; nie zmienia pozostałych pól.',wraplength=730).pack(anchor='w',pady=(4,0))
        source=ttk.Frame(self.edu_tab)
        source.pack(fill='x',pady=(10,0))
        ttk.Label(source,text='Plik jednostek:').pack(side='left')
        self.edu_path_label=ttk.Label(source,text='Nie wybrano',width=65)
        self.edu_path_label.pack(side='left',padx=7)
        ttk.Button(source,text='Wybierz EDU...',command=self.choose_edu).pack(side='right')
        line=ttk.Frame(self.edu_tab)
        line.pack(fill='x',pady=12)
        ttk.Label(line,text='Jednostka:').pack(side='left')
        self.unit=tk.StringVar()
        self.unit_combo=ttk.Combobox(line,textvariable=self.unit,width=28,state='readonly')
        self.unit_combo.pack(side='left',padx=7)
        self.unit_combo.bind('<<ComboboxSelected>>',self.unit_changed)
        ttk.Label(line,text='Rekrutacja:').pack(side='left')
        self.recruit=tk.StringVar()
        ttk.Entry(line,textvariable=self.recruit,width=9).pack(side='left',padx=6)
        ttk.Label(line,text='Utrzymanie:').pack(side='left')
        self.upkeep=tk.StringVar()
        ttk.Entry(line,textvariable=self.upkeep,width=9).pack(side='left',padx=6)
        actions=ttk.Frame(self.edu_tab)
        actions.pack(fill='x')
        ttk.Button(actions,text='Pokaż zmiany',command=lambda:self.preview_change('edu')).pack(side='left')
        ttk.Button(actions,text='Zapisz z kopią .bak',command=lambda:self.commit('edu')).pack(side='left',padx=8)
        ttk.Label(self.edu_tab,text='Podgląd różnic:').pack(anchor='w',pady=(14,0))
        _,self.diff_edu=self.make_editor(self.edu_tab)

    def open_mod(self):
        directory=filedialog.askdirectory(title='Wybierz folder data lub folder gry/moda')
        if not directory:return
        root=Path(directory)
        data=resolve_data_folder(root)
        if data is None:
            messagebox.showerror('Błędny folder',
                'Wybierz bezpośrednio folder data albo folder moda/gry, w którym jest podfolder data.\n\n'
                'Jeśli mod ma niestandardową strukturę, możesz później wskazać konkretny plik.')
            return
        self.root_dir=root
        self.data_dir=data
        self.folder_label.configure(text=str(data))
        candidates=campaign_paths(data)
        self.campaign_file=candidates[0] if candidates else None
        self.edu_file=(data/'export_descr_unit.txt') if (data/'export_descr_unit.txt').is_file() else None
        self.refresh()
        self.refresh_files()
        self.tabs.select(self.files_tab)

    def choose_campaign(self):
        path=filedialog.askopenfilename(title='Wybierz plik descr_strat.txt',
            initialdir=str(self.data_dir or Path.home()),
            filetypes=[('Plik kampanii','descr_strat.txt'),('Pliki tekstowe','*.txt'),('Wszystkie','*.*')])
        if path:
            self.campaign_file=Path(path)
            self.refresh()

    def choose_edu(self):
        path=filedialog.askopenfilename(title='Wybierz export_descr_unit.txt',
            initialdir=str(self.data_dir or Path.home()),
            filetypes=[('Plik jednostek','export_descr_unit.txt'),('Pliki tekstowe','*.txt'),('Wszystkie','*.*')])
        if path:
            self.edu_file=Path(path)
            self.refresh()

    def locate(self,kind):
        path=self.campaign_file if kind=='campaign' else self.edu_file
        if not path or not path.is_file():
            name='descr_strat.txt' if kind=='campaign' else 'export_descr_unit.txt'
            raise ValueError(f'Nie znaleziono {name}. Kliknij „Wybierz ...” i wskaż plik ręcznie.\n'
                             'W podstawowej grze dane mogą być spakowane.')
        return path

    def refresh(self):
        self.campaign_path_label.configure(text=str(self.campaign_file or 'Nie znaleziono — wskaż plik'))
        self.edu_path_label.configure(text=str(self.edu_file or 'Nie znaleziono — wskaż plik'))
        notices=[]
        try:
            ctext,_=read_text(self.locate('campaign'))
            self.options=money_options(ctext)
            self.purse_options=dict(faction_field_options(ctext,'denari_kings_purse'))
            self.region_options=settlement_options(ctext)
            self.region_combo['values']=[x[0] for x in self.region_options]
            self.region.set(self.region_options[0][0] if self.region_options else '')
            self.region_changed()
            m=re.search(r'(?im)^\s*start_date\s+(-?\d+)',ctext)
            self.year_value.set(m.group(1) if m else '')
            self.faction_combo['values']=[x[0] for x in self.options]
            self.faction.set(self.options[0][0] if self.options else '')
            if self.options:self.faction_changed()
            notices.append(f'Kampania: {len(self.options)} frakcji')
        except Exception as exc:
            self.options=[];self.faction_combo['values']=[];self.faction.set('');self.money.set('')
            self.purse.set('');self.region.set('');self.population.set('');self.region_combo['values']=[]
            notices.append(f'Kampania: {exc}')
        try:
            etext,_=read_text(self.locate('edu'))
            self.unit_options=edu_units(etext)
            self.unit_combo['values']=[x[0] for x in self.unit_options]
            self.unit.set(self.unit_options[0][0] if self.unit_options else '')
            if self.unit_options:self.unit_changed()
            notices.append(f'Jednostki: {len(self.unit_options)}')
        except Exception as exc:
            self.unit_options=[];self.unit_combo['values']=[];self.unit.set('');self.recruit.set('');self.upkeep.set('')
            notices.append(f'Jednostki: {exc}')
        self.status.set(' | '.join(notices))

    def faction_changed(self,event=None):
        for name,money in self.options:
            if name==self.faction.get():self.money.set(str(money));break
        self.purse.set(str(self.purse_options.get(self.faction.get(),'')))

    def region_changed(self,event=None):
        for name,pop,*_ in getattr(self,'region_options',[]):
            if name==self.region.get():self.population.set(str(pop));break

    def extra_proposed(self,kind):
        path=self.locate('campaign')
        old,encoding=read_text(path)
        if kind=='purse':
            new=edit_faction_field(old,self.faction.get(),'denari_kings_purse',self.get_integer(self.purse.get()))
        elif kind=='population':
            new=edit_settlement_population(old,self.region.get(),self.get_integer(self.population.get()))
        elif kind=='year':
            new=edit_campaign_year(old,self.year_field.get(),self.get_integer(self.year_value.get(),signed=True))
        else:raise ValueError('Nieobsługiwana operacja')
        return path,old,new,encoding

    @staticmethod
    def get_integer(value,signed=False):
        if not re.fullmatch(r'-?\d+' if signed else r'\d+',value.strip()):
            raise ValueError('Wpisz poprawną liczbę całkowitą.')
        number=int(value)
        if not -2_147_483_648<=number<=2_147_483_647:
            raise ValueError('Przekroczono zakres liczby 32-bitowej.')
        return number

    def preview_extra(self,kind):
        try:
            path,old,new,_=self.extra_proposed(kind)
            diff=''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='przed',tofile='po'))
            self.set_preview('campaign',diff or 'Brak zmian.')
        except Exception as exc:messagebox.showerror('Błąd',str(exc))

    def commit_extra(self,kind):
        try:
            path,old,new,encoding=self.extra_proposed(kind)
            if old==new:raise ValueError('Brak zmian do zapisu.')
            self.preview_extra(kind)
            if not messagebox.askyesno('Potwierdź',f'Zapisać zmianę w {path.name}? Zostanie utworzona kopia .bak.'):
                return
            backup=save_safely(path,old,new,encoding)
            self.refresh()
            messagebox.showinfo('Zapisano',f'Zapisano. Kopia zapasowa: {backup}')
        except Exception as exc:messagebox.showerror('Nie zapisano',str(exc))

    def unit_changed(self,event=None):
        for name,recruit,upkeep in self.unit_options:
            if name==self.unit.get():self.recruit.set(recruit);self.upkeep.set(upkeep);break

    def proposed(self,kind):
        path=self.locate(kind)
        old,encoding=read_text(path)
        def number(v):
            if not re.fullmatch(r'\d{1,10}',v.strip()):raise ValueError('Kwota musi być liczbą całkowitą nieujemną (do 10 cyfr).')
            n=int(v)
            if n>2_147_483_647:raise ValueError('Przekroczono bezpieczny limit 32-bitowej liczby.')
            return n
        if kind=='campaign':
            new=edit_money(old,self.faction.get(),number(self.money.get()))
        else:
            new=edit_unit_cost(old,self.unit.get(),number(self.recruit.get()),number(self.upkeep.get()))
        return path,old,new,encoding

    def preview_change(self,kind):
        try:
            path,old,new,_=self.proposed(kind)
            diff=''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='przed',tofile='po'))
            self.set_preview(kind,diff if diff else 'Brak zmian.')
            self.status.set(f'Podgląd: {path.name}')
        except Exception as exc:
            messagebox.showerror('Błąd',str(exc))

    def set_preview(self,kind,content):
        box=self.diff_campaign if kind=='campaign' else self.diff_edu
        box.configure(state='normal');box.delete('1.0','end');box.insert('1.0',content);box.configure(state='disabled')

    def commit(self,kind):
        try:
            path,old,new,encoding=self.proposed(kind)
            if old==new:raise ValueError('Brak zmian do zapisu.')
            self.preview_change(kind)
            if not messagebox.askyesno('Potwierdzenie',f'Zmienić {path.name}?\nPrzed zapisem zostanie utworzona kopia .bak.'):
                return
            backup=save_safely(path,old,new,encoding)
            self.status.set(f'Zapisano: {path}\nBackup: {backup.name}')
            messagebox.showinfo('Zapisano',f'Zapisano zmiany.\nKopia zapasowa:\n{backup}')
            self.refresh()
        except Exception as exc:
            messagebox.showerror('Nie zapisano',str(exc))


if __name__=='__main__':
    App().mainloop()
