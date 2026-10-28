"""Medieval II Mod Studio v0.7 — przystępny ciemny interfejs. Zachowuje moduły v0.6.1."""
import re
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import advanced as ad
from studio06 import Studio as Studio061

BG='#09121b'; PANEL='#111f2b'; FIELD='#172b38'; GREEN='#54f8bc'; FG='#e5f4f2'; MUTED='#95b1bd'; BLUE='#28b9df'

class Studio(Studio061):
    def __init__(self):
        super().__init__()
        self.title('MEDIEVAL // MOD STUDIO  v0.7')
        self.geometry('1370x850'); self.minsize(1000,640)
        self.setup_theme()
        self.add_header()
        self.style_native(self)
        self.after(300, self.show_first_help)
        self.bind('<Control-s>',lambda e:self.commit_all())
        self.bind('<F5>',lambda e:self.load_advanced())
        try:self.iconbitmap(str(Path(__file__).with_name('modstudio.ico')))
        except Exception:pass

    def setup_theme(self):
        self.configure(bg=BG)
        s=ttk.Style(self); s.theme_use('clam')
        s.configure('.',background=BG,foreground=FG,font=('Segoe UI',10))
        s.configure('TFrame',background=BG)
        s.configure('TLabelframe',background=PANEL,bordercolor='#315064',relief='solid')
        s.configure('TLabelframe.Label',background=PANEL,foreground=GREEN,font=('Segoe UI',11,'bold'))
        s.configure('TLabel',background=BG,foreground=FG)
        s.configure('Muted.TLabel',foreground=MUTED,background=BG)
        s.configure('Title.TLabel',background=BG,foreground=GREEN,font=('Segoe UI',20,'bold'))
        s.configure('Heading.TLabel',background=BG,foreground=GREEN,font=('Segoe UI',12,'bold'))
        s.configure('TButton',background=FIELD,foreground=FG,padding=(12,8),borderwidth=1,bordercolor='#426074',focuscolor=FIELD)
        s.map('TButton',background=[('active','#244254')],foreground=[('active',GREEN)])
        s.configure('Accent.TButton',background='#087a5c',foreground='#ffffff',font=('Segoe UI',10,'bold'),padding=(16,10))
        s.map('Accent.TButton',background=[('active','#119a73')])
        s.configure('TEntry',fieldbackground=FIELD,foreground=FG,insertcolor=GREEN,padding=5)
        s.configure('TCombobox',fieldbackground=FIELD,background=FIELD,foreground=FG,arrowcolor=GREEN,padding=5)
        s.map('TCombobox',fieldbackground=[('readonly',FIELD)],foreground=[('readonly',FG)])
        s.configure('TNotebook',background=BG,borderwidth=0)
        s.configure('TNotebook.Tab',background=FIELD,foreground=MUTED,padding=(14,10),font=('Segoe UI',9,'bold'))
        s.map('TNotebook.Tab',background=[('selected','#135b52')],foreground=[('selected','#ffffff')])
        s.configure('Treeview',background=PANEL,fieldbackground=PANEL,foreground=FG,rowheight=34,borderwidth=0,font=('Segoe UI',10))
        s.map('Treeview',background=[('selected','#176657')],foreground=[('selected','#ffffff')])
        s.configure('Treeview.Heading',background=FIELD,foreground=GREEN,font=('Segoe UI',10,'bold'),padding=8)
        s.configure('TScrollbar',background=FIELD,troughcolor=BG)
        self.option_add('*TCombobox*Listbox.background',FIELD)
        self.option_add('*TCombobox*Listbox.foreground',FG)
        self.option_add('*TCombobox*Listbox.selectBackground','#176657')

    def style_native(self,widget):
        for child in widget.winfo_children():
            if isinstance(child,tk.Text):
                child.configure(bg=PANEL,fg=FG,insertbackground=GREEN,selectbackground='#176657',relief='flat',font=('Consolas',10))
            if isinstance(child,tk.Listbox):
                child.configure(bg=PANEL,fg=FG,selectbackground='#176657',relief='flat',font=('Segoe UI',10))
            self.style_native(child)

    def add_header(self):
        # The header is placed above the existing UI without changing its original behavior.
        top=ttk.Frame(self,padding=(14,10));top.pack(side='top',fill='x',before=self.winfo_children()[0])
        ttk.Label(top,text='♜ KRUCHYX MEDIEVAL MOD STUDIOS',style='Title.TLabel').pack(side='left')
        ttk.Label(top,text='  |  v0.9.2  •  EDYTORY KLASYCZNE  •  Wykonane przez Kruchyx',style='Muted.TLabel').pack(side='left',padx=10)
        ttk.Button(top,text='① Wybierz mod',command=self.open_mod).pack(side='right',padx=4)
        ttk.Button(top,text='② Zmiany i zapis',style='Accent.TButton',command=lambda:self.tabs.select(self.changes_tab)).pack(side='right',padx=4)

    def show_first_help(self):
        if self.status.get().startswith('Wybierz'):
            self.status.set('START: Wybierz folder moda → wybierz generała → wybierz oddział → ustaw doświadczenie → dodaj zmianę → zapisz.')

    def create_army(self):
        p=self.army_tab
        ttk.Label(p,text='ARMIE I GENERAŁOWIE',style='Title.TLabel').pack(anchor='w',pady=(0,4))
        ttk.Label(p,text='Wybierz postać po lewej, kliknij oddział w tabeli i zmień jego doświadczenie. Bez numerów i surowych wpisów.',style='Muted.TLabel').pack(anchor='w',pady=(0,14))
        main=ttk.Panedwindow(p,orient='horizontal');main.pack(fill='both',expand=True)
        left=ttk.Frame(main,padding=(4,4));right=ttk.Frame(main,padding=(14,4))
        main.add(left,weight=1);main.add(right,weight=3)
        ttk.Label(left,text='1  WYBIERZ GENERAŁA',style='Heading.TLabel').pack(anchor='w',pady=(0,8))
        self.search_general=tk.StringVar()
        ttk.Entry(left,textvariable=self.search_general).pack(fill='x',pady=(0,8))
        self.search_general.trace_add('write',lambda *_:self.filter_characters())
        ttk.Label(left,text='Szukaj po nazwie lub frakcji',style='Muted.TLabel').pack(anchor='w',pady=(0,10))
        listing=ttk.Frame(left);listing.pack(fill='both',expand=True)
        self.general_list=tk.Listbox(listing,exportselection=False,width=30,activestyle='none',font=('Segoe UI',11))
        self.general_list.pack(side='left',fill='both',expand=True)
        scroll=ttk.Scrollbar(listing,orient='vertical',command=self.general_list.yview);scroll.pack(side='right',fill='y')
        self.general_list.configure(yscrollcommand=scroll.set)
        self.general_list.bind('<<ListboxSelect>>',lambda e:self.pick_general())
        ttk.Label(right,text='2  SZCZEGÓŁY POSTACI',style='Heading.TLabel').pack(anchor='w')
        self.army_who=ttk.Label(right,text='Wybierz generała z listy.',font=('Segoe UI',16,'bold'))
        self.army_who.pack(anchor='w',pady=(9,6))
        self.army_summary=ttk.Label(right,text='',style='Muted.TLabel');self.army_summary.pack(anchor='w',pady=(0,16))
        agebar=ttk.Frame(right);agebar.pack(fill='x',pady=(0,12))
        ttk.Label(agebar,text='Wiek generała').pack(side='left',padx=(0,12))
        self.army_age=tk.StringVar();ttk.Entry(agebar,textvariable=self.army_age,width=8).pack(side='left')
        ttk.Button(agebar,text='Zmień wiek',command=self.stage_age).pack(side='left',padx=10)
        ttk.Label(right,text='3  KLIKNIJ ODDZIAŁ',style='Heading.TLabel').pack(anchor='w',pady=(8,6))
        tablewrap=ttk.Frame(right);tablewrap.pack(fill='both',expand=True)
        self.army_tree=ttk.Treeview(tablewrap,columns=('number','name','exp'),show='headings',height=10,selectmode='browse')
        for key,title,width in [('number','NR',65),('name','JEDNOSTKA',450),('exp','DOŚWIADCZENIE',150)]:
            self.army_tree.heading(key,text=title);self.army_tree.column(key,width=width,stretch=key=='name',anchor='w' if key=='name' else 'center')
        self.army_tree.pack(side='left',fill='both',expand=True)
        sc=ttk.Scrollbar(tablewrap,orient='vertical',command=self.army_tree.yview);sc.pack(side='right',fill='y');self.army_tree.configure(yscrollcommand=sc.set)
        self.army_tree.bind('<<TreeviewSelect>>',lambda e:self.pick_unit())
        editor=ttk.LabelFrame(right,text='4  ZMIEŃ DOŚWIADCZENIE WYBRANEGO ODDZIAŁU',padding=14)
        editor.pack(fill='x',pady=(15,9))
        self.unit_selected_label=ttk.Label(editor,text='Najpierw kliknij oddział w tabeli.');self.unit_selected_label.pack(anchor='w',pady=(0,10))
        editrow=ttk.Frame(editor);editrow.pack(fill='x')
        ttk.Label(editrow,text='Doświadczenie (0–9):').pack(side='left',padx=(0,10))
        self.unit_experience=tk.StringVar()
        self.exp_spin=tk.Spinbox(editrow,from_=0,to=9,textvariable=self.unit_experience,width=5,font=('Segoe UI',13),bg=FIELD,fg=FG,insertbackground=GREEN,buttonbackground=FIELD)
        self.exp_spin.pack(side='left')
        ttk.Button(editrow,text='+ Dodaj zmianę',style='Accent.TButton',command=self.stage_selected_unit).pack(side='left',padx=14)
        ttk.Button(editrow,text='Zobacz zmiany i zapisz →',command=lambda:self.tabs.select(self.changes_tab)).pack(side='left')
        ttk.Label(right,text='Zapis następuje dopiero po zatwierdzeniu w „Zmiany i cofanie”. Przed zapisem tworzona jest kopia bezpieczeństwa.',style='Muted.TLabel').pack(anchor='w',pady=(5,0))
        # Compatibility with previous module internals.
        self.character=tk.StringVar();self.army_field=tk.StringVar(value='exp');self.army_value=tk.StringVar();self.unit_no=tk.StringVar(value='0')
        self.character_combo=ttk.Combobox(left,textvariable=self.character,state='readonly')
        self.army_info=ttk.Label(left,text='')
        self.current_characters=[];self.selected_unit_index=None

    def load_advanced(self):
        super().load_advanced()
        if hasattr(self,'general_list'):
            self.filter_characters()
            if self.character.get():
                self.choose_character(self.character.get())

    def filter_characters(self):
        if not hasattr(self,'general_list'):return
        query=self.search_general.get().casefold().strip()
        vals=[f"{r['faction']} | {r['name']}" for r in getattr(self,'characters',[]) if query in f"{r['faction']} {r['name']}".casefold()]
        self.visible_chars=vals
        self.general_list.delete(0,'end')
        for val in vals:self.general_list.insert('end',val)
        if self.character.get() in vals:
            ix=vals.index(self.character.get());self.general_list.selection_set(ix);self.general_list.see(ix)

    def choose_character(self,value):
        self.character.set(value)
        self.character_changed()

    def pick_general(self):
        sel=self.general_list.curselection()
        if sel:self.choose_character(self.visible_chars[sel[0]])

    def character_changed(self):
        # Override old raw repr of units (source of unreadable clutter).
        if not hasattr(self,'army_tree'):return
        rec=next((r for r in getattr(self,'characters',[]) if f"{r['faction']} | {r['name']}"==self.character.get()),None)
        self.army_tree.delete(*self.army_tree.get_children())
        self.selected_unit_index=None;self.unit_selected_label.configure(text='Najpierw kliknij oddział w tabeli.')
        if not rec:return
        self.army_who.configure(text=rec['name'])
        self.army_summary.configure(text=f"Frakcja: {rec['faction'].upper()}     •     Wiek: {rec['age']}     •     Oddziały: {len(rec['units'])}")
        self.army_age.set(rec['age'])
        for i,(unit,exp) in enumerate(rec['units']):
            clean=re.sub(r'\\t|\s+',' ',unit).strip()
            self.army_tree.insert('','end',iid=str(i),values=(i+1,clean,exp if exp else '—'))

    def pick_unit(self):
        sel=self.army_tree.selection()
        if not sel:return
        self.selected_unit_index=int(sel[0]);rec=next((r for r in getattr(self,'characters',[]) if f"{r['faction']} | {r['name']}"==self.character.get()),None)
        if rec and self.selected_unit_index<len(rec['units']):
            unit,exp=rec['units'][self.selected_unit_index]
            self.unit_selected_label.configure(text='Wybrany: '+re.sub(r'\\t|\s+',' ',unit).strip())
            self.unit_experience.set(exp if exp else '0')

    def stage_age(self):
        def run():
            if not self.character.get():raise ValueError('Najpierw wybierz generała.')
            p,t=self.campaign_text();f,n=self.character.get().split(' | ',1)
            self.stage(p,t,ad.edit_character(t,f,n,'age',self.army_age.get()))
        self.safe(run)

    def stage_selected_unit(self):
        def run():
            if not self.character.get():raise ValueError('Najpierw wybierz generała.')
            if self.selected_unit_index is None:raise ValueError('Kliknij oddział w tabeli, a następnie zmień jego doświadczenie.')
            p,t=self.campaign_text();f,n=self.character.get().split(' | ',1)
            self.stage(p,t,ad.edit_character(t,f,n,'exp',self.unit_experience.get(),self.selected_unit_index))
        self.safe(run)

if __name__=='__main__':
    Studio().mainloop()
