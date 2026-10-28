"""Read-only detection + opt-in extraction of vanilla Medieval II data.

Never run official unpacker into the game's own directory. The old official
unpack_all.bat is deliberately NOT invoked. The target is a separate cache.
"""
from __future__ import annotations
import os
import hashlib
import re
import subprocess
import sys
from pathlib import Path

RUNTIME_DLLS = ('msvcr71.dll', 'msvcp71.dll')
NT_DLL_NOT_FOUND = 0xC0000135
NT_BAD_IMAGE_FORMAT = 0xC000007B

NEEDED = ('export_descr_unit.txt', 'export_descr_buildings.txt', 'descr_sm_resources.txt',
          'descr_regions.txt', 'descr_strat.txt', 'descr_campaign_db.xml')


def vanilla_cache_root(game_root=None):
    root=Path(os.environ.get('LOCALAPPDATA') or (Path.home()/'.local'/'share'))
    base=root/'Kruchyx Medieval Mod Studios'/'vanilla_cache'
    if game_root is None:return base
    # Different Steam/library installations must never silently share stale data.
    key=hashlib.sha256(str(Path(game_root).resolve()).casefold().encode('utf-8')).hexdigest()[:12]
    return base/key


def is_game_root(path):
    p=Path(path)
    return p.is_dir() and (bool(list(p.glob('medieval2*.exe'))) or
                           (p/'packs').is_dir() and (p/'tools').is_dir())


def find_game_root(path):
    p=Path(path).resolve()
    for candidate in (p,*p.parents):
        if is_game_root(candidate):return candidate
    return None


def known_game_locations():
    home=Path.home()
    roots=[]
    home_steam=home/'AppData'/'Local'/'Steam'
    prefixes=[home_steam,Path('C:/Program Files (x86)/Steam'),Path('C:/Steam'),Path('D:/SteamLibrary'),
              Path('E:/SteamLibrary'),Path('F:/SteamLibrary')]
    if sys.platform=='win32':
        try:
            import winreg
            for keyname in (r'Software\Valve\Steam',r'Software\WOW6432Node\Valve\Steam'):
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,keyname) as key:
                        prefixes.append(Path(winreg.QueryValueEx(key,'SteamPath')[0]))
                except OSError:pass
        except ImportError:pass
    for prefix in prefixes:
        root=prefix/'steamapps'/'common'/'Medieval II Total War'
        if is_game_root(root) and root.resolve() not in roots:roots.append(root.resolve())
    return roots


def list_campaign_choices(game_root):
    """Explicit Vanilla + Kingdoms + mods. A base campaign may still be packed."""
    p=Path(game_root)
    choices=[{'id':'vanilla','path':p,'label_pl':'Medieval II — kampania podstawowa (Vanilla)',
              'label_en':'Medieval II — Grand Campaign (Vanilla)','kind':'vanilla'}]
    folder=p/'mods'
    campaigns={'americas':('Kingdoms — Ameryki','Kingdoms — Americas'),
               'british_isles':('Kingdoms — Brytania','Kingdoms — Britannia'),
               'crusades':('Kingdoms — Krucjaty','Kingdoms — Crusades'),
               'teutonic':('Kingdoms — Krzyżacy','Kingdoms — Teutonic')}
    if folder.is_dir():
        for f in sorted(folder.iterdir(), key=lambda x:x.name.lower()):
            if f.is_dir() and ((f/'data').is_dir() or (f/'packs').is_dir()):
                labels=campaigns.get(f.name.lower())
                choices.append({'id':f.name,'path':f,'label_pl':labels[0] if labels else f'🛡  {f.name}',
                                'label_en':labels[1] if labels else f'🛡  {f.name}',
                                'kind':'kingdoms' if labels else 'mod'})
    return choices


def find_unpacker(game_root):
    p=Path(game_root)
    for path in (p/'tools'/'unpacker'/'unpacker.exe',p/'tools'/'unpacker.exe'):
        if path.is_file():return path
    return None


def list_packs(game_root):
    root=Path(game_root)
    packdir=root/'packs'
    return sorted(packdir.glob('*.pack')) if packdir.is_dir() else []


def cache_data_dir(cache_root=None):
    c=Path(cache_root) if cache_root is not None else vanilla_cache_root()
    return c/'data' if (c/'data').is_dir() else c


def cache_summary(cache_root=None):
    c=cache_data_dir(cache_root)
    return {f: bool(list(c.rglob(f))) for f in NEEDED}


# Campaign and world-map definitions are distributed as LOOSE files in Steam's
# Medieval II installations. Missing them from the .pack scan is normal.
VANILLA_LOOSE_PATHS = {
    'descr_regions.txt': Path('data/world/maps/base/descr_regions.txt'),
    'descr_strat.txt': Path('data/world/maps/campaign/imperial_campaign/descr_strat.txt'),
}


def find_loose_vanilla_files(game_root):
    """Locate base campaign files without touching the player's installation."""
    game = Path(game_root).resolve()
    return {key: (game / relative if (game / relative).is_file() else None)
            for key, relative in VANILLA_LOOSE_PATHS.items()}


def vanilla_file_availability(game_root, cache_root=None):
    """Combine .pack cache AND actual loose base-campaign files.

    The origin is explicit; no copies, no writes and no spoofed extraction status.
    """
    game = Path(game_root).resolve()
    cache = Path(cache_root) if cache_root is not None else vanilla_cache_root(game)
    cached = cache_summary(cache)
    loose = find_loose_vanilla_files(game)
    available = {key: cached.get(key, False) or bool(loose.get(key)) for key in NEEDED}
    sources = {key: ('cache' if cached.get(key) else 'game' if loose.get(key) else 'missing')
               for key in NEEDED}
    return {'found': available, 'cache_found': cached, 'loose_files': loose,
            'sources': sources}


def runtime_dll_status(game_root):
    """Inspect the player's own installation; never fetch DLLs online."""
    game = Path(game_root).resolve()
    exe = find_unpacker(game)
    parent = exe.parent if exe else game / 'tools' / 'unpacker'
    result = {}
    for dll in RUNTIME_DLLS:
        near_exe = parent / dll
        in_game = game / dll
        result[dll] = ('unpacker' if near_exe.is_file() else
                       'game_root' if in_game.is_file() else 'missing')
    return result


def extractor_environment(game_root):
    """Make legacy game runtime discoverable by the child process only.

    No registry edits and no copies into the game directory. Windows DLL
    search for unpackaged apps includes directories on PATH.
    """
    env = os.environ.copy()
    game = Path(game_root).resolve()
    if all((game / name).is_file() or
           ((find_unpacker(game) or game / 'tools' / 'unpacker' / 'unpacker.exe').parent / name).is_file()
           for name in RUNTIME_DLLS):
        env['PATH'] = str(game) + os.pathsep + env.get('PATH', '')
    return env


def repair_legacy_runtime(game_root):
    """Opt-in repair: copy only known CRT DLLs from the OWN game installation.

    Existing destination files are never overwritten. Caller must obtain
    permission before using this function. Never touches System32.
    """
    import shutil
    game = Path(game_root).resolve()
    exe = find_unpacker(game)
    if not exe or not is_game_root(game):
        raise FileNotFoundError('Game or unpacker not found')
    actions = []
    for dll in RUNTIME_DLLS:
        original = game / dll
        dest = exe.parent / dll
        if dest.is_file():
            actions.append((dll, 'already_present'))
            continue
        if not original.is_file():
            actions.append((dll, 'missing_in_game'))
            continue
        if original.stat().st_size == 0:
            actions.append((dll, 'invalid_source'))
            continue
        try:
            # 'xb' ensures even a concurrent repair never overwrites a DLL.
            with original.open('rb') as source, dest.open('xb') as target:
                shutil.copyfileobj(source, target)
            actions.append((dll, 'copied'))
        except FileExistsError:
            actions.append((dll, 'already_present'))
        except OSError as exc:
            actions.append((dll, 'error: ' + str(exc)))
    return actions


def windows_exit_code(code):
    return (int(code) & 0xFFFFFFFF) if code is not None else None


def diagnose_unpack(details, found=None, lang='pl', game_root=None):
    """Make extractor failures actionable, but never guess at the exact cause."""
    entries = details or []
    logs = '\n'.join(str(x.get('log','')) for x in entries).casefold()
    codes = {windows_exit_code(x.get('returncode')) for x in entries if x.get('returncode') is not None}
    if NT_DLL_NOT_FOUND in codes:
        dlls = runtime_dll_status(game_root) if game_root else {}
        which = ', '.join(k for k, v in dlls.items() if v == 'missing')
        if lang == 'en':
            return ('Windows 0xC0000135: unpacker.exe cannot start because a DLL is missing. '
                    'Check msvcr71.dll and msvcp71.dll in your game folder and next to unpacker.exe. '
                    + (('Not found in either location: ' + which + '. ') if which else '') +
                    'Use the in-app DLL repair button (copies only from your own installation) or copy them manually. '
                    'If missing in the game, verify files in Steam. Never download DLLs from unknown websites.')
        return ('Windows 0xC0000135: nie można uruchomić unpacker.exe — brak biblioteki DLL. '
                'Sprawdź msvcr71.dll oraz msvcp71.dll w folderze gry i obok unpacker.exe. '
                + (('Nie znaleziono w obu lokalizacjach: ' + which + '. ') if which else '') +
                'Użyj w programie przycisku „NAPRAW BRAKUJĄCE DLL” (kopiuje tylko z własnej instalacji) '
                'lub ręcznie skopiuj oba pliki. Jeśli nie ma ich nawet w grze, sprawdź pliki Steam. '
                'Nie pobieraj DLL z nieznanych stron.')
    if NT_BAD_IMAGE_FORMAT in codes:
        return ('Windows 0xC000007B: niezgodny format pliku DLL lub uszkodzony ekstraktor. '
                'Sprawdź spójność plików Medieval II w Steam.' if lang == 'pl' else
                'Windows 0xC000007B: incompatible DLL or damaged extractor. Verify Medieval II files in Steam.')
    if 'msvcp71' in logs or 'msvcr71' in logs or 'dll' in logs and ('missing' in logs or 'nie znalezion' in logs):
        return ('Brakuje biblioteki DLL starego ekstraktora. Sprawdź, czy msvcp71.dll i msvcr71.dll '
                'są we własnym folderze gry; jeśli są, skopiuj je obok unpacker.exe. '
                'Nie pobieraj DLL z przypadkowych stron.' if lang == 'pl' else
                'Legacy unpacker DLL missing. If msvcp71.dll or msvcr71.dll exist in the installed game, '
                'copy them alongside unpacker.exe. Never download random DLLs.')
    if any(k in logs for k in ('access is denied','odmowa dostępu','permission denied')):
        return ('Brak dostępu do plików. Sprawdź uprawnienia do gry oraz katalogu cache.' if lang == 'pl'
                else 'Permission denied. Check access to the game and extraction cache.')
    if any(k in logs for k in ('bad image','0xc000007b','not a valid win32')):
        return ('Niezgodność starego ekstraktora z systemem lub uszkodzona instalacja. '
                'Sprawdź spójność plików w Steam.' if lang == 'pl'
                else 'Incompatible or damaged legacy unpacker. Verify game files in Steam.')
    if not entries:
        return ('Brak zapisu działania ekstraktora.' if lang == 'pl' else 'No unpacker log recorded.')
    if found and all(found.values()):
        return ('Wszystkie wymagane pliki są dostępne: część z archiwów, część bezpośrednio w katalogu gry.'
                if lang == 'pl' else 'All required definitions are available from the archives and game files.')
    if found and any(found.values()):
        return ('Odczytano część plików. Pozostałe mogą być poza archiwami lub w innych paczkach.' if lang == 'pl'
                else 'Some files extracted. Remaining definitions may be outside the selected packs.')
    return ('Nie udało się odczytać definicji. Sprawdź dziennik ekstraktora: możliwy brak DLL, '
            'niezgodność wersji albo format argumentów. Nie uruchamiaj unpack_all.bat.' if lang == 'pl'
            else 'No definitions extracted. Check log for a missing DLL, incompatible unpacker or invalid arguments. '
            'Avoid unpack_all.bat.')


def unpack_vanilla(game_root, cache_root=None, timeout=150):
    """Extract ONLY required vanilla definitions outside the game directory.

    Uses official unpacker with source path relative to its working directory
    (as in the original unpacker docs) and responds to old Y/N prompts. All
    failures get logged in the cache for inspection; no in-game files changed.
    """
    game=Path(game_root).resolve()
    if not is_game_root(game):raise ValueError('Not a recognized Medieval II installation')
    exe=find_unpacker(game)
    packs=list_packs(game)
    if not exe or not packs:raise FileNotFoundError('Official unpacker.exe or game packs missing')
    output=Path(cache_root or vanilla_cache_root(game)).resolve()
    if output==game or game in output.parents:raise ValueError('Cache must be outside the game directory')
    output.mkdir(parents=True,exist_ok=True)
    summaries=[]
    dll_state=runtime_dll_status(game)
    child_env=extractor_environment(game)
    # For the original exe relative paths are more reliable than D:\...\*.pack.
    source=os.path.relpath(str(game/'packs'),str(exe.parent)).replace('/', '\\') + '\\*.pack'
    for name in NEEDED:
        command=[str(exe),'--source='+source,'--destination='+str(output),
                 '--filter='+name,'--verbosity=1','--mode=0']
        try:
            result=subprocess.run(command,cwd=str(exe.parent),capture_output=True,
                                  input='Y\nY\nY\n',text=True,errors='replace',timeout=timeout,
                                  creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),
                                  env=child_env)
            message=((result.stdout or '')+'\n'+(result.stderr or ''))
            summaries.append({'filter':name,'returncode':result.returncode,
                              'log':message[-5000:], 'source':source})
            # Repeating six commands cannot fix a missing runtime DLL.
            if windows_exit_code(result.returncode) in (NT_DLL_NOT_FOUND, NT_BAD_IMAGE_FORMAT):
                break
        except (OSError,subprocess.TimeoutExpired) as exc:
            summaries.append({'filter':name,'returncode':-1,'log':str(exc),'source':source})
    availability=vanilla_file_availability(game,output)
    found=availability['found']
    # An intact base installation may already contain loose campaign files even
    # when not one additional definition could be extracted from archives.
    success=any(found.values())
    advice=diagnose_unpack(summaries, found, game_root=game)
    log_path=output/'Kruchyx_Vanilla_Unpack.log'
    try:
        with log_path.open('w',encoding='utf-8') as log:
            log.write('KRUCHYX VANILLA DIAGNOSTICS\n')
            log.write('GAME: '+str(game)+'\n')
            log.write('EXE: '+str(exe)+'\n')
            log.write('SOURCE: '+source+'\n')
            log.write('CACHE: '+str(output)+'\n')
            log.write('FOUND: '+repr(found)+'\n')
            log.write('FOUND_IN_PACK_CACHE: '+repr(availability['cache_found'])+'\n')
            log.write('FOUND_IN_GAME_FOLDER: '+repr({k:str(v) if v else None for k,v in availability['loose_files'].items()})+'\n')
            log.write('FILE_SOURCES: '+repr(availability['sources'])+'\n')
            log.write('GAME_RUNTIME_DLLS: '+repr(dll_state)+'\n')
            log.write('GAME_FOLDER_IN_CHILD_PATH: '+str(str(game) in child_env.get('PATH',''))+'\n')
            log.write('ADVICE: '+advice+'\n')
            for entry in summaries:
                log.write('\n=== '+entry['filter']+' | exit '+str(entry['returncode'])+' ===\n')
                log.write(entry['log']+'\n')
    except OSError:
        log_path=None
    return {'success':success,'cache':output,'found':found,'runtime_dlls':dll_state,
            'sources':availability['sources'],'cache_found':availability['cache_found'],
            'loose_files':availability['loose_files'], 'details':summaries,
            'log_path':log_path,'advice':advice}
