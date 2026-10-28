"""New GUI pages and staged changes for v0.6; preserves v0.5 pages."""
import re, difflib, shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from modstudio import App as LegacyApp, read_text, save_safely, campaign_paths, resolve_data_folder, edit_money, edit_unit_cost, edit_faction_field, edit_settlement_population, edit_campaign_year
import advanced as ad

class Studio(LegacyApp):
    def __init__(self):
        super().__init__()
        self.title('Medieval II Mod Studio — v0.6.1 (naprawcza)')
        self.geometry('1250x850')
        self.pending={}  # path -> {base, encoding, after}; staged safely
        self.undo_backups=[]
        self._ignore_reload=False
        self.make_discovery_controls()
        self.city_tab=self.page('Miasta i budynki')
        self.army_tab=self.page('Armie i generałowie')
        self.dipl_tab=self.page('Dyplomacja / grywalność')
        self.unit_adv_tab=self.page('Statystyki jednostek')
        self.assist_tab=self.page('Asystent PL — offline')
        self.changes_tab=self.page('Zmiany i cofanie')
        self.create_city();self.create_army();self.create_dipl();self.create_unit_adv();self.create_assistant();self.create_changes()
        self.tabs.bind('<<NotebookTabChanged>>', lambda e:self.load_advanced())
        self.load_advanced()

    def page(self,title):
        frame=ttk.Frame(self.tabs,padding=12);self.tabs.add(frame,text=title);return frame

    def label_row(self, parent, fields):
        row=ttk.Frame(parent);row.pack(fill='x',pady=6)
        for text,var,values,width in fields:
            ttk.Label(row,text=text).pack(side='left',padx=(3,5))
            if values is None:w=ttk.Entry(row,textvariable=var,width=width)
            else:w=ttk.Combobox(row,textvariable=var,values=values,state='readonly',width=width)
            w.pack(side='left',padx=(0,10))
            yield w

    def foot(self,parent,callback):
        ttk.Button(parent,text='Dodaj do podglądu zmian',command=callback).pack(anchor='w',pady=8)
        ttk.Label(parent,text='Nic nie zapisze się na dysku, dopóki nie zatwierdzisz zmian w zakładce „Zmiany i cofanie”.',wraplength=920).pack(anchor='w')

    def create_city(self):
        p=self.city_tab
        ttk.Label(p,text='Osady — właściciel, populacja, poziom, pierwszy budynek',font=('Segoe UI',13,'bold')).pack(anchor='w')
        self.city=tk.StringVar();self.city_field=tk.StringVar(value='population');self.city_value=tk.StringVar();self.city_owner=tk.StringVar()
        self.city_combo,field_combo,self.city_entry=list(self.label_row(p,[('Region',self.city,[],42),('Pole',self.city_field,['population','level','owner','building'],20),('Nowa wartość',self.city_value,None,33)]))
        self.city_combo.bind('<<ComboboxSelected>>',lambda e:self.city_changed())
        field_combo.bind('<<ComboboxSelected>>',lambda e:self.city_changed())
        ttk.Label(p,text='Właściciel: identyfikator frakcji (np. poland). Budynek: np. core_building wooden_wall — edytuje PIERWSZY wpis type budynku w osadzie.').pack(anchor='w')
        self.foot(p,self.stage_city)
        self.city_info=ttk.Label(p,text='');self.city_info.pack(anchor='w',pady=12)

    def create_army(self):
        p=self.army_tab
        ttk.Label(p,text='Generałowie i ich oddziały startowe',font=('Segoe UI',13,'bold')).pack(anchor='w')
        self.character=tk.StringVar();self.army_field=tk.StringVar(value='age');self.army_value=tk.StringVar();self.unit_no=tk.StringVar(value='0')
        self.character_combo,field_combo,_,_=list(self.label_row(p,[('Postać',self.character,[],47),('Pole',self.army_field,['age','exp'],12),('Nowa wartość',self.army_value,None,12),('Nr oddziału (od 0)',self.unit_no,None,7)]))
        self.character_combo.bind('<<ComboboxSelected>>',lambda e:self.character_changed())
        self.foot(p,self.stage_army)
        self.army_info=ttk.Label(p,text='');self.army_info.pack(anchor='w',pady=12)

    def create_dipl(self):
        p=self.dipl_tab
        ttk.Label(p,text='Grywalność frakcji i początkowe relacje',font=('Segoe UI',13,'bold')).pack(anchor='w')
        self.dip_faction=tk.StringVar();self.play_status=tk.StringVar(value='playable');self.dip_target=tk.StringVar();self.dip_relation=tk.StringVar(value='allied_to')
        self.dip_faction_combo,self.play_combo=list(self.label_row(p,[('Frakcja',self.dip_faction,[],26),('Grywalność',self.play_status,['playable','unlockable','nonplayable'],18)]))
        ttk.Button(p,text='Dodaj zmianę grywalności',command=self.stage_playable).pack(anchor='w',pady=(3,16))
        self.dip_target_combo,self.rel_combo=list(self.label_row(p,[('Frakcja docelowa',self.dip_target,[],26),('Relacja',self.dip_relation,['allied_to','at_war_with'],20)]))
        ttk.Button(p,text='Dodaj zmianę dyplomacji',command=self.stage_relationship).pack(anchor='w',pady=8)
        ttk.Label(p,text='Relacje: nowe wpisy dopisywane są do pliku; istniejące relacje z wieloma celami wymagają ręcznej kontroli. Dla wzajemnego sojuszu dodaj wpis także od drugiej frakcji.',wraplength=1000).pack(anchor='w')

    def create_unit_adv(self):
        p=self.unit_adv_tab
        ttk.Label(p,text='Zaawansowane statystyki jednostek — export_descr_unit.txt',font=('Segoe UI',13,'bold')).pack(anchor='w')
        self.adv_unit=tk.StringVar();self.adv_stat=tk.StringVar(value='stat_cost');self.adv_index=tk.StringVar(value='1');self.adv_value=tk.StringVar()
        self.adv_unit_combo,_,_,_=list(self.label_row(p,[('Jednostka',self.adv_unit,[],38),('Pole',self.adv_stat,['stat_cost','stat_pri','stat_sec','stat_mental'],17),('Indeks od 0',self.adv_index,None,7),('Nowa liczba',self.adv_value,None,12)]))
        self.adv_unit_combo.bind('<<ComboboxSelected>>',lambda e:self.unit_adv_changed())
        ttk.Label(p,text='Edycja indeksu wartości rozdzielonej przecinkami; np. stat_cost indeks 1 = rekrutacja, 2 = utrzymanie. Indeksy innych pól sprawdź w podglądzie.',wraplength=1000).pack(anchor='w')
        self.foot(p,self.stage_unit)
        self.unit_info=ttk.Label(p,text='',wraplength=950);self.unit_info.pack(anchor='w',pady=10)

    def create_assistant(self):
        p=self.assist_tab
        ttk.Label(p,text='Asystent poleceń po polsku (lokalny, bez usługi AI)',font=('Segoe UI',13,'bold')).pack(anchor='w')
        ttk.Label(p,text='Obsługuje na razie dokładne polecenia poniżej. Nie wysyła plików do internetu i nie interpretuje dowolnego języka naturalnego.',wraplength=1000).pack(anchor='w',pady=6)
        self.command=tk.StringVar()
        ttk.Entry(p,textvariable=self.command,width=100).pack(fill='x',pady=10)
        for example in ('Ustaw floreny poland na 500000','Ustaw sakiewke england na 3000','Ustaw populacje London_Region na 10000','Ustaw wiek William z england na 35'):
            ex=example
            ttk.Button(p,text=ex,command=lambda s=ex:self.command.set(s)).pack(anchor='w',pady=3)
        self.foot(p,self.stage_command)

    def create_changes(self):
        p=self.changes_tab
        bar=ttk.Frame(p);bar.pack(fill='x')
        ttk.Button(bar,text='Odśwież różnice',command=self.show_pending).pack(side='left')
        ttk.Button(bar,text='ZAPISZ zatwierdzone zmiany (.bak)',command=self.commit_all).pack(side='left',padx=8)
        ttk.Button(bar,text='Odrzuć wszystkie oczekujące',command=self.discard_pending).pack(side='left')
        ttk.Button(bar,text='Cofnij ostatni zapis',command=self.undo_last).pack(side='right')
        self.changes_view=tk.Text(p,font=('Consolas',10),wrap='none');self.changes_view.pack(fill='both',expand=True,pady=12)

    def campaign_text(self):
        p=self.locate('campaign');return p,self.pending[p]['after'] if p in self.pending else read_text(p)[0]
    def edu_text(self):
        p=self.locate('edu');return p,self.pending[p]['after'] if p in self.pending else read_text(p)[0]

    def stage(self,path,old,edited):
        if old==edited:self.status.set('Bez zmian');return
        if path not in self.pending:
            original,enc=read_text(path)
            if original!=old:raise ValueError('Plik na dysku zmienił się: odśwież aplikację.')
            self.pending[path]={'base':original,'encoding':enc,'after':edited}
        else:self.pending[path]['after']=edited
        self.status.set('Zmiana dodana do kolejki: '+path.name)
        self.show_pending()
        self.tabs.select(self.changes_tab)

    def safe(self,fn):
        try:fn()
        except Exception as exc:messagebox.showerror('Nie udało się przygotować zmiany',str(exc))

    def load_advanced(self):
        if not hasattr(self,'city_combo'):return
        try:
            _,txt=self.campaign_text()
            self.cities=ad.settlements(txt);self.characters=ad.characters(txt)
            self.city_combo['values']=[r['region'] for r in self.cities]
            self.character_combo['values']=[f"{r['faction']} | {r['name']}" for r in self.characters]
            factions=[r[0] for r in ad.faction_blocks(txt)]
            self.dip_faction_combo['values']=factions;self.dip_target_combo['values']=factions
            for var,values in ((self.city,[r['region'] for r in self.cities]),(self.character,[f"{r['faction']} | {r['name']}" for r in self.characters]),(self.dip_faction,factions),(self.dip_target,factions)):
                if values and var.get() not in values:var.set(values[0])
            self.city_changed();self.character_changed()
        except Exception:pass
        try:
            _,txt=self.edu_text();self.advanced_units=ad.unit_stats(txt)
            vals=[x[0] for x in self.advanced_units];self.adv_unit_combo['values']=vals
            if vals and self.adv_unit.get() not in vals:self.adv_unit.set(vals[0])
            self.unit_adv_changed()
        except Exception:pass

    def city_changed(self):
        rec=next((r for r in getattr(self,'cities',[]) if r['region']==self.city.get()),None)
        if not rec:return
        field=self.city_field.get()
        value={'population':rec['pop'],'level':rec['level'],'owner':rec['faction'],'building':rec['buildings'][0] if rec['buildings'] else ''}.get(field,'')
        self.city_value.set(value)
        self.city_info.configure(text=f"Frakcja: {rec['faction']} | populacja: {rec['pop']} | poziom: {rec['level']} | budynki: {', '.join(rec['buildings'])}")
    def character_changed(self):
        rec=next((r for r in getattr(self,'characters',[]) if f"{r['faction']} | {r['name']}"==self.character.get()),None)
        if rec:self.army_info.configure(text='Wiek: '+rec['age']+' | Oddziały: '+str(list(enumerate(rec['units']))))
    def unit_adv_changed(self):
        stats=dict(getattr(self,'advanced_units',[])).get(self.adv_unit.get(),{})
        self.unit_info.configure(text=' | '.join(k+': '+v for k,v in stats.items()))

    def stage_city(self):
        def run():
            p,t=self.campaign_text();self.stage(p,t,ad.edit_settlement(t,self.city.get(),self.city_field.get(),self.city_value.get().strip()))
        self.safe(run)
    def stage_army(self):
        def run():
            p,t=self.campaign_text();f,n=self.character.get().split(' | ',1)
            self.stage(p,t,ad.edit_character(t,f,n,self.army_field.get(),self.army_value.get(),int(self.unit_no.get())))
        self.safe(run)
    def stage_playable(self):
        self.safe(lambda:self._stage_campaign(lambda t:ad.edit_playability(t,self.dip_faction.get(),self.play_status.get())))
    def stage_relationship(self):
        self.safe(lambda:self._stage_campaign(lambda t:ad.edit_relationship(t,self.dip_faction.get(),self.dip_target.get(),self.dip_relation.get())))
    def _stage_campaign(self,transform):
        p,t=self.campaign_text();self.stage(p,t,transform(t))
    def stage_unit(self):
        def run():
            p,t=self.edu_text();self.stage(p,t,ad.edit_unit_stat(t,self.adv_unit.get(),self.adv_stat.get(),int(self.adv_index.get()),self.adv_value.get()))
        self.safe(run)
    def stage_command(self):
        def run():
            phrase=self.command.get().strip().lower()
            p,t=self.campaign_text()
            if m:=re.fullmatch(r'ustaw floreny ([a-z_]+) na (\d+)',phrase):
                from modstudio import edit_money
                new=edit_money(t,m.group(1),int(m.group(2)))
            elif m:=re.fullmatch(r'ustaw sakiewke ([a-z_]+) na (\d+)',phrase):
                from modstudio import edit_faction_field
                new=edit_faction_field(t,m.group(1),'denari_kings_purse',int(m.group(2)))
            elif m:=re.fullmatch(r'ustaw populacje ([a-z0-9_]+) na (\d+)',phrase):
                new=ad.edit_settlement(t,m.group(1),'population',m.group(2))
            elif m:=re.fullmatch(r'ustaw wiek (.+) z ([a-z_]+) na (\d+)',phrase):
                new=ad.edit_character(t,m.group(2),m.group(1),'age',m.group(3))
            else:raise ValueError('Nie znam takiego polecenia. Wybierz jeden ze wzorów pod polem tekstowym.')
            self.stage(p,t,new)
        self.safe(run)

    def show_pending(self):
        if not hasattr(self,'changes_view'):return
        output=[]
        for path,item in self.pending.items():
            diff=''.join(difflib.unified_diff(item['base'].splitlines(keepends=True),item['after'].splitlines(keepends=True),fromfile=str(path)+' (oryginał)',tofile=str(path)+' (propozycja)'))
            output.append(diff[:500000] if diff else 'Bez zmian')
        self.changes_view.delete('1.0','end');self.changes_view.insert('1.0','\n'.join(output) if output else 'Brak oczekujących zmian.')
    def discard_pending(self):
        if self.pending and not messagebox.askyesno('Odrzucić?','Usunąć wszystkie niezapisane propozycje?'):return
        self.pending.clear();self.show_pending();self.load_advanced()
    def _commit_all_core(self):
        if not self.pending:messagebox.showinfo('Brak zmian','Nie ma nic do zapisania.');return
        if not messagebox.askyesno('Zapis','Zapisać '+str(len(self.pending))+' plik(ów)? Powstaną kopie .bak.'):return
        done=[]
        try:
            for path,item in list(self.pending.items()):
                if item['base']==item['after']:continue
                backup=save_safely(path,item['base'],item['after'],item['encoding'])
                done.append((path,backup))
            self.undo_backups.extend(done)
            self.pending.clear();self.show_pending();self.refresh();self.load_advanced()
            messagebox.showinfo('Zapisano','Zapisane pliki: '+str(len(done))+'\nKopie .bak utworzone.')
        except Exception as exc:
            # Roll back only files written in this batch.
            for path,backup in reversed(done):shutil.copy2(backup,path)
            messagebox.showerror('Błąd zapisu','Przywrócono pliki zapisane w tej partii.\n'+str(exc))
    def _undo_last_core(self):
        if not self.undo_backups:messagebox.showinfo('Cofanie','Brak ostatniego zapisu z bieżącej sesji.');return
        path,backup=self.undo_backups[-1]
        if not backup.exists():messagebox.showerror('Cofanie','Brak pliku kopii.');return
        if not messagebox.askyesno('Przywracanie',f'Przywrócić {path.name} z kopii {backup.name}? Aktualny plik zostanie zachowany jako nowa kopia.') :return
        from datetime import datetime
        snapshot=path.with_name(path.name+'.przed_cofnieciem_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.bak')
        shutil.copy2(path,snapshot);shutil.copy2(backup,path)
        self.undo_backups.pop();self.pending.pop(path,None);self.refresh();self.load_advanced();self.show_pending()
        messagebox.showinfo('Cofnięto','Przywrócono: '+str(path)+'\nPoprzedni stan: '+str(snapshot))


    # v0.6.1: rozpoznawanie modow bez recznego przeklikiwania katalogow.
    def make_discovery_controls(self):
        bar=ttk.Frame(self)
        bar.pack(fill='x',before=self.tabs,padx=12,pady=(0,5))
        ttk.Label(bar,text='Kampania:').pack(side='left')
        self.campaign_choice=tk.StringVar()
        self.campaign_picker=ttk.Combobox(bar,textvariable=self.campaign_choice,state='readonly',width=77)
        self.campaign_picker.pack(side='left',fill='x',expand=True,padx=5)
        self.campaign_picker.bind('<<ComboboxSelected>>',self.select_discovered_campaign)
        ttk.Button(bar,text='Znajdź kampanie',command=self.rescan_campaigns).pack(side='left',padx=3)
        ttk.Button(bar,text='Otwórz katalog pliku',command=self.show_campaign_path).pack(side='left',padx=3)
        self.discovered=[]

    def open_mod(self):
        import os
        directory=os.environ.pop('KRUCHYX_ACTIVE_MOD','') or filedialog.askdirectory(title='Wybierz katalog moda, DATA albo katalog gry')
        if not directory:return
        from discovery import find_data_candidates, scan_campaigns
        root=Path(directory)
        candidates=find_data_candidates(root)
        if not candidates:
            messagebox.showerror('Nie znaleziono folderu data','Nie wykryto katalogu data. Wybierz folder moda (np. mods\\kirsi_biggermap_medieval2) albo jego folder data.')
            return
        # Jeśli wybrano katalog gry z wieloma modami, wybierz mod, a nie pierwszy przypadkowy plik.
        if len(candidates)>1:
            dlg=tk.Toplevel(self);dlg.title('Wybierz mod / katalog data');dlg.geometry('860x360');dlg.transient(self);dlg.grab_set()
            ttk.Label(dlg,text='Wykryto kilka katalogów DATA. Wybierz mod do edycji:',padding=10).pack(anchor='w')
            chooser=tk.Listbox(dlg,exportselection=False);chooser.pack(fill='both',expand=True,padx=12)
            for c in candidates:chooser.insert('end',str(c))
            chooser.selection_set(0)
            result=[]
            def accept():
                if chooser.curselection():result.append(candidates[chooser.curselection()[0]])
                dlg.destroy()
            ttk.Button(dlg,text='Wybierz ten folder',command=accept).pack(pady=10)
            dlg.protocol('WM_DELETE_WINDOW',dlg.destroy)
            self.wait_window(dlg)
            if not result:return
            data=result[0]
        else:data=candidates[0]
        if self.pending and not messagebox.askyesno('Oczekujące zmiany','Masz niezapisane zmiany. Odrzucić je i wczytać inny mod?'):return
        self.pending.clear();self.show_pending()
        self.root_dir=root;self.data_dir=data
        self.folder_label.configure(text=str(data))
        self.edu_file=(data/'export_descr_unit.txt') if (data/'export_descr_unit.txt').is_file() else None
        self.rescan_campaigns()
        self.refresh_files()
        self.tabs.select(self.campaign_tab if self.campaign_file else self.files_tab)

    def rescan_campaigns(self):
        from discovery import scan_campaigns
        if self.data_dir is None:
            messagebox.showinfo('Najpierw wybierz mod','Wskaż folder moda albo data.')
            return
        self.discovered=scan_campaigns(self.data_dir)
        self.campaign_picker['values']=[str(p.relative_to(self.data_dir)) for p in self.discovered]
        if self.discovered:
            if self.campaign_file not in self.discovered:self.campaign_file=self.discovered[0]
            self.campaign_choice.set(str(self.campaign_file.relative_to(self.data_dir)))
        else:
            self.campaign_file=None;self.campaign_choice.set('Nie znaleziono descr_strat.txt')
        self.refresh();self.load_advanced()
        self.status.set(f'Katalog: {self.data_dir} | kampanie: {len(self.discovered)} | aktualna: {self.campaign_file or "brak"}')

    def select_discovered_campaign(self,event=None):
        selected=self.campaign_picker.current()
        if selected<0 or selected>=len(self.discovered):return
        p=self.discovered[selected]
        if self.pending and p!=self.campaign_file:
            if not messagebox.askyesno('Zmiana kampanii','Masz niezapisane zmiany. Odrzucić je i wybrać inną kampanię?'):
                self.campaign_choice.set(str(self.campaign_file.relative_to(self.data_dir)));return
            self.pending.clear();self.show_pending()
        self.campaign_file=p;self.refresh();self.load_advanced()
        self.status.set(f'Aktywna kampania: {p}')

    def show_campaign_path(self):
        p=self.campaign_file
        if not p:messagebox.showinfo('Brak kampanii','Nie znaleziono pliku kampanii.');return
        import subprocess,os
        if os.name=='nt':subprocess.Popen(['explorer', '/select,', str(p)])
        else:messagebox.showinfo('Ścieżka aktywnej kampanii',str(p))

    def choose_campaign(self):
        super().choose_campaign()
        if self.campaign_file:
            if self.data_dir and self.campaign_file not in self.discovered and self.campaign_file.is_relative_to(self.data_dir):
                self.discovered.append(self.campaign_file)
                self.campaign_picker['values']=[str(p.relative_to(self.data_dir)) for p in self.discovered]
            if self.data_dir and self.campaign_file.is_relative_to(self.data_dir):
                self.campaign_choice.set(str(self.campaign_file.relative_to(self.data_dir)))
            self.load_advanced()

    def route_open_file(self):
        super().route_open_file()
        if self.campaign_file and self.data_dir and self.campaign_file.is_relative_to(self.data_dir):
            if self.campaign_file not in self.discovered:
                self.discovered.append(self.campaign_file)
                self.campaign_picker['values']=[str(p.relative_to(self.data_dir)) for p in self.discovered]
            self.campaign_choice.set(str(self.campaign_file.relative_to(self.data_dir)))
        self.load_advanced()

    def stage(self,path,old,edited):
        path=Path(path).resolve()
        if old==edited:self.status.set('Bez zmian');return
        if path not in self.pending:
            original,enc=read_text(path)
            if original!=old:raise ValueError('Plik zmieniono poza aplikacją. Odczytaj go ponownie przed zapisaniem.')
            self.pending[path]={'base':original,'encoding':enc,'after':edited}
        else:
            if old!=self.pending[path]['after']:
                raise ValueError('Edytor używa nieaktualnej zawartości pliku. Odśwież widok zmian przed następną edycją.')
            self.pending[path]['after']=edited
        self.status.set('Zmiana dodana do kolejki: '+str(path))
        self.show_pending();self.tabs.select(self.changes_tab)

    def extra_proposed(self,kind):
        path=self.locate('campaign').resolve()
        old=self.pending[path]['after'] if path in self.pending else read_text(path)[0]
        encoding=self.pending[path]['encoding'] if path in self.pending else read_text(path)[1]
        if kind=='purse':new=edit_faction_field(old,self.faction.get(),'denari_kings_purse',self.get_integer(self.purse.get()))
        elif kind=='population':new=edit_settlement_population(old,self.region.get(),self.get_integer(self.population.get()))
        elif kind=='year':new=edit_campaign_year(old,self.year_field.get(),self.get_integer(self.year_value.get(),signed=True))
        else:raise ValueError('Nieobsługiwana operacja')
        return path,old,new,encoding

    def proposed(self,kind):
        path=self.locate(kind).resolve()
        old=self.pending[path]['after'] if path in self.pending else read_text(path)[0]
        enc=self.pending[path]['encoding'] if path in self.pending else read_text(path)[1]
        if kind=='campaign':new=edit_money(old,self.faction.get(),self.get_integer(self.money.get()))
        else:new=edit_unit_cost(old,self.unit.get(),self.get_integer(self.recruit.get()),self.get_integer(self.upkeep.get()))
        return path,old,new,enc

    def commit_extra(self,kind):
        try:
            path,old,new,_=self.extra_proposed(kind)
            self.stage(path,old,new)
        except Exception as exc:messagebox.showerror('Nie dodano zmiany',str(exc))

    def commit(self,kind):
        try:
            path,old,new,_=self.proposed(kind)
            self.stage(path,old,new)
        except Exception as exc:messagebox.showerror('Nie dodano zmiany',str(exc))

    def save_text_file(self):
        if not self.text_file_path:
            messagebox.showwarning('Brak pliku','Najpierw wybierz plik.');return
        try:
            path=self.text_file_path.resolve()
            text=self.text_editor.get('1.0','end-1c')
            if path in self.pending:
                if self.text_original!=self.pending[path]['after']:
                    raise ValueError('Plik jest już zmodyfikowany w innych zakładkach. Odrzuć zmiany tekstowe i wczytaj plik ponownie, żeby uniknąć nadpisania.')
                old=self.pending[path]['after']
            else:old=self.text_original
            self.stage(path,old,text)
            self.text_original=text
        except Exception as exc:messagebox.showerror('Nie dodano zmiany',str(exc))

    def commit_all(self):
        self._commit_all_core()
        # Jeśli zapis się udał, synchronizujemy również podgląd pliku tekstowego.
        if not self.pending and self.text_file_path and self.text_file_path.is_file():
            content,enc=read_text(self.text_file_path)
            self.text_original=content;self.text_encoding=enc
            self.text_editor.delete('1.0','end');self.text_editor.insert('1.0',content)

    def undo_last(self):
        self._undo_last_core()
        if self.text_file_path and self.text_file_path.is_file() and not self.pending:
            content,enc=read_text(self.text_file_path)
            self.text_original=content;self.text_encoding=enc
            self.text_editor.delete('1.0','end');self.text_editor.insert('1.0',content)

if __name__=='__main__':
    Studio().mainloop()
