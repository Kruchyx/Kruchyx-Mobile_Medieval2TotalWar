# -*- coding: utf-8 -*-
"""Safe, bilingual unpacking walkthrough; does not execute game tools.

An optional library action handles read-only selective unpacking after explicit consent.
The guide itself only opens folders or copies text.
"""
from __future__ import annotations
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from vanilla_support import find_game_root, find_unpacker, vanilla_cache_root, list_packs, runtime_dll_status, repair_legacy_runtime

BG='#0c1116'; PANEL='#172129'; GOLD='#eac586'; INK='#efe9dc'; MUTED='#a8b8bb'; RED='#e6a89c'; GREEN='#85d8b8'


def t(lang,pl,en):return en if lang=='en' else pl


def manual_commands(game_root):
    """Return non-destructive commands targeting the same isolated cache as the application."""
    game = Path(game_root).resolve()
    if not game.is_dir() or not (game/'tools'/'unpacker'/'unpacker.exe').is_file():
        raise ValueError('Game with tools/unpacker/unpacker.exe required')
    cache=vanilla_cache_root(game)
    if cache==game or game in cache.parents:
        raise ValueError('Extraction destination cannot be inside the installed game')
    base=game/'tools'/'unpacker'
    files=('export_descr_unit.txt','export_descr_buildings.txt','descr_strat.txt',
           'descr_sm_resources.txt','descr_regions.txt','descr_campaign_db.xml')
    lines=['@echo off', 'chcp 65001 >nul',f'cd /d "{base}"',f'if not exist "{cache}" mkdir "{cache}"',
           f'set "PATH={game};%PATH%"']
    lines.extend(f'unpacker.exe --source=..\\..\\packs\\*.pack --destination="{cache}" --filter={name} --verbosity=1' for name in files)
    lines.extend(['echo.', 'echo KRUCHYX - Sprawdz wynik w katalogu:',f'echo {cache}','pause'])
    return '\r\n'.join(lines)+'\r\n'


def guide_steps(lang):
    return [
        (t(lang,'1. Otwórz BIBLIOTEKĘ MODÓW','1. Open MOD LIBRARY'),
         t(lang,'Wybierz instalację Medieval II i pierwszą pozycję: „Medieval II — kampania podstawowa (Vanilla)”. Nie wybieraj losowego moda.',
           'Choose your Medieval II installation and the FIRST entry: “Medieval II — Grand Campaign (Vanilla)”. Do not choose a random mod.')),
        (t(lang,'2. Spróbuj automatycznego odczytu (zalecane)','2. Try automatic extraction (recommended)'),
         t(lang,'Kliknij „PRZYGOTUJ DANE VANILLA (BETA)” w bibliotece. Kruchyx uruchomi oficjalny unpacker wyłącznie na definicjach potrzebnych analizatorowi.',
           'Click “PREPARE VANILLA DATA (BETA)” in the library. Kruchyx invokes the installed official unpacker and extracts only selected definitions.')),
        (t(lang,'3. Dwa pliki kampanii są zwykle JUŻ W GRZE','3. Two campaign files are normally ALREADY INSTALLED'),
         t(lang,'descr_regions.txt: data\\world\\maps\\base\\descr_regions.txt.  '
           'descr_strat.txt: data\\world\\maps\\campaign\\imperial_campaign\\descr_strat.txt.  '
           'Te pliki mogą nie występować w .pack; Kruchyx sprawdza je osobno, bez rozpakowywania i kopiowania.',
           'descr_regions.txt: data\\world\\maps\\base\\descr_regions.txt.  '
           'descr_strat.txt: data\\world\\maps\\campaign\\imperial_campaign\\descr_strat.txt.  '
           'These may not be in .pack archives. Kruchyx locates them in the installed game without moving them.')),
        (t(lang,'4. Sprawdź wynik','4. Check the result'),
         t(lang,'Wróć do Doradcy frakcji i Atlasu jednostek. Kruchyx powinien odnaleźć definicje EDU. Jeśli dane nie są widoczne, przejdź do instrukcji ręcznej niżej.',
           'Return to Faction Advisor and Unit Atlas. EDU data should become available. If it does not, follow the manual route below.')),
        (t(lang,'5. Ręczne rozpakowanie tylko plików analizy','5. Manually extract only analysis files'),
         t(lang,'W folderze gry znajdź „tools\\unpacker\\unpacker.exe”. Skopiuj gotowe komendy przyciskiem poniżej, zapisz je jako nowy plik „Kruchyx_Vanilla_Extract.bat” i uruchom. Komendy wskazują osobny katalog w LOCALAPPDATA, a NIE katalog gry.',
           'Find “tools\\unpacker\\unpacker.exe” in the installed game. Copy the commands below into a new “Kruchyx_Vanilla_Extract.bat” and run it. Commands use a separate LOCALAPPDATA cache, NOT the installed game folder.')),
        (t(lang,'6. Błąd MSVCP71.DLL lub MSVCR71.DLL?','6. Missing MSVCP71.DLL or MSVCR71.DLL?'),
         t(lang,'Nie pobieraj DLL z podejrzanych stron. Sprawdź, czy pliki msvcp71.dll i msvcr71.dll są obok medieval2.exe. Jeśli tak, skopiuj je z własnej instalacji do „tools\\unpacker”, po czym powtórz próbę.',
           'Do not download DLLs from unknown websites. Look for msvcp71.dll and msvcr71.dll next to medieval2.exe; if present, copy those DLLs from your own installation into “tools\\unpacker” and retry.')),
        (t(lang,'7. Ochrona instalacji gry','7. Protect your installation'),
         t(lang,'Nie uruchamiaj domyślnego „unpack_all.bat” tylko dla Kruchyx: zwykle wypakowuje do folderu data gry. Jeśli już wypakowałeś tam wszystkie pliki i gra przestała się uruchamiać, po zrobieniu kopii sprawdź i usuń z data tylko „descr_geography_new.txt” oraz „descr_geography_new.db”.',
           'Avoid the default “unpack_all.bat” for Kruchyx: it normally extracts into the installed game data folder. If you already extracted everything there and the game will not launch, back up the files and check for “descr_geography_new.txt” and “descr_geography_new.db” in data; remove only those two files.')),
    ]


def open_vanilla_guide(app,game_root=None):
    lang=app.lang
    game=find_game_root(game_root) if game_root else None
    win=tk.Toplevel(app,bg=BG)
    win.title(t(lang,'Kruchyx — Jak rozpakować Vanilla','Kruchyx — How to unpack Vanilla'))
    win.geometry('920x740');win.minsize(680,520)
    win.transient(app)
    canvas=tk.Canvas(win,bg=BG,highlightthickness=0)
    sc=tk.Scrollbar(win,command=canvas.yview)
    sc.pack(side='right',fill='y');canvas.pack(side='left',fill='both',expand=True)
    canvas.configure(yscrollcommand=sc.set)
    content=tk.Frame(canvas,bg=BG,padx=26,pady=20)
    ref=canvas.create_window((0,0),window=content,anchor='nw')
    content.bind('<Configure>',lambda _e:canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.bind('<Configure>',lambda e:canvas.itemconfigure(ref,width=e.width))
    tk.Label(content,text=t(lang,'VANILLA · PIERWSZE URUCHOMIENIE','VANILLA · FIRST RUN'),bg=BG,fg=GOLD,font=('Segoe UI',11,'bold')).pack(anchor='w')
    tk.Label(content,text=t(lang,'Jak odczytać zwykłą kampanię?','How to inspect the base campaign?'),bg=BG,fg=INK,font=('Segoe UI',23,'bold')).pack(anchor='w',pady=(8,4))
    desc=t(lang,'Nie musisz rozpakowywać całej gry. Kruchyx potrzebuje tylko kilku plików tekstowych. Sam poradnik nic nie modyfikuje.',
           'You do not need to unpack the whole game. Kruchyx only needs a few text files. This guide makes no changes.')
    tk.Label(content,text=desc,bg=BG,fg=MUTED,font=('Segoe UI',11),wraplength=790,justify='left').pack(anchor='w',pady=(0,15))
    for heading,body in guide_steps(lang):
        block=tk.Frame(content,bg=PANEL,padx=18,pady=13,highlightbackground='#443d30',highlightthickness=1)
        block.pack(fill='x',pady=5)
        tk.Label(block,text=heading,bg=PANEL,fg=GOLD,font=('Segoe UI',12,'bold')).pack(anchor='w')
        tk.Label(block,text=body,bg=PANEL,fg=INK,font=('Segoe UI',10),justify='left',wraplength=755).pack(anchor='w',pady=(6,0))
    target=game
    if not target:
        found=Path('D:/SteamLibrary/steamapps/common/Medieval II Total War')
        if found.exists():target=found
    actions=tk.Frame(content,bg=BG);actions.pack(fill='x',pady=18)
    btnopts=dict(relief='flat',bd=0,font=('Segoe UI',10,'bold'),padx=16,pady=10,cursor='hand2')
    def choose_game():
        path=filedialog.askdirectory(parent=win,title=t(lang,'Wybierz folder Medieval II','Select Medieval II installation'))
        if not path:return
        g=find_game_root(path)
        if not g:messagebox.showwarning('Medieval II',t(lang,'Nie rozpoznano instalacji gry.','Game installation not recognized.'),parent=win);return
        win.destroy();open_vanilla_guide(app,g)
    tk.Button(actions,text=t(lang,'WYBIERZ FOLDER GRY','CHOOSE GAME FOLDER'),command=choose_game,bg='#b99260',fg='#121619',**btnopts).pack(side='left',padx=(0,8),pady=3)
    if game:
        state = runtime_dll_status(game)
        def repair_dlls():
            current = runtime_dll_status(game)
            missing = [name for name,where in current.items() if where != 'unpacker']
            if not missing:
                messagebox.showinfo('Kruchyx', t(lang,'Obie biblioteki są już obok unpacker.exe.',
                  'Both runtime DLLs are already next to unpacker.exe.'),parent=win)
                return
            if not messagebox.askyesno('Kruchyx', t(lang,
                    'Skopiować brakujące msvcr71.dll / msvcp71.dll z WŁASNEGO folderu gry do tools\\unpacker? '
                    'Ta operacja doda jedynie brakujące pliki, nigdy nie nadpisze istniejących.',
                    'Copy missing msvcr71.dll / msvcp71.dll from YOUR game installation to tools\\unpacker? '
                    'Only missing files will be added; existing files are never replaced.'),parent=win):
                return
            results=repair_legacy_runtime(game)
            summary='\n'.join(n + ': ' + status for n,status in results)
            messagebox.showinfo('Kruchyx — DLL',summary,parent=win)
        tk.Button(actions,text=t(lang,'NAPRAW BRAKUJĄCE DLL','REPAIR MISSING DLLS'),command=repair_dlls,
                  bg='#705538',fg=INK,**btnopts).pack(side='left',padx=5,pady=3)
        def copy_commands():
            try:commands=manual_commands(game)
            except ValueError as exc:messagebox.showwarning('Kruchyx',str(exc),parent=win);return
            win.clipboard_clear();win.clipboard_append(commands)
            messagebox.showinfo('Kruchyx',t(lang,'Skopiowano bezpieczne komendy. Zapisz je w Notatniku jako plik .bat. Niczego nie uruchomiono automatycznie.',
                                                   'Safe commands copied. Save them in Notepad as a .bat file. Nothing was executed automatically.'),parent=win)
        tk.Button(actions,text=t(lang,'KOPIUJ KOMENDY DO .BAT','COPY .BAT COMMANDS'),command=copy_commands,bg='#365e55',fg=INK,**btnopts).pack(side='left',padx=5,pady=3)
        def open_folder():
            p=game/'tools'/'unpacker'
            if p.is_dir():
                try:os.startfile(str(p))
                except (OSError,AttributeError):messagebox.showinfo('Kruchyx',str(p),parent=win)
        tk.Button(actions,text=t(lang,'OTWÓRZ UNPACKER','OPEN UNPACKER FOLDER'),command=open_folder,bg='#25323a',fg=GOLD,**btnopts).pack(side='left',padx=5,pady=3)
    status=tk.Frame(content,bg=PANEL,padx=14,pady=13);status.pack(fill='x',pady=5)
    found_text=(str(game) if game else t(lang,'Wskaż folder gry przyciskiem powyżej, aby skopiować komendy dla swojej instalacji.',
                                           'Choose the game folder above to generate commands for your installation.'))
    diagnostic=t(lang,'Instalacja: ','Installation: ')+found_text
    if game:
        from vanilla_support import list_packs
        diagnostic+='\n'+t(lang,'Oficjalny unpacker: ','Official unpacker: ')+('OK' if find_unpacker(game) else t(lang,'BRAK','MISSING'))
        diagnostic+='   •   '+t(lang,'Archiwa .pack: ','Pack archives: ')+str(len(list_packs(game)))
        diagnostic+='\n'+t(lang,'Bezpieczny katalog danych: ','Safe cache folder: ')+str(vanilla_cache_root(game))
        diagnostic+='\n'+t(lang,'Biblioteki DLL: ','Runtime DLLs: ')+', '.join(
            k + ' = ' + v for k,v in runtime_dll_status(game).items())
        from vanilla_support import find_loose_vanilla_files
        loose = find_loose_vanilla_files(game)
        diagnostic+='\n'+t(lang,'Pliki kampanii w grze: ','Campaign files in game: ')+', '.join(
            key + '=' + ('OK' if file else ('BRAK' if lang=='pl' else 'MISSING'))
            for key,file in loose.items())
    tk.Label(status,text=diagnostic,bg=PANEL,fg=GREEN if game else MUTED,font=('Segoe UI',10),justify='left',wraplength=790).pack(anchor='w')
    tk.Label(content,text=t(lang,'Źródła: dokumentacja Pack Extractor (TWC Wiki), poradnik Steam i dokumentacja parametrów unpacker.exe na totalwar.org.',
                            'References: TWC Wiki Pack Extractor, Steam unpacking guide, and totalwar.org unpacker argument documentation.'),
             bg=BG,fg=MUTED,font=('Segoe UI',9),wraplength=790,justify='left').pack(anchor='w',pady=12)
    return win
