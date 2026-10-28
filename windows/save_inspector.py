"""Read-only Medieval II save inspection. Never modifies a .sav."""
from pathlib import Path
import struct, hashlib, datetime


def read_len_utf16(data, offset):
    if offset + 2 > len(data): return None, offset
    length=struct.unpack_from('<H', data, offset)[0]
    if not 0 < length <= 260 or offset + 2 + length*2 > len(data): return None, offset
    raw=data[offset+2:offset+2+length*2]
    try:
        value=raw.decode('utf-16le')
        if any(ord(c)<32 for c in value):return None,offset
        return value,offset+2+length*2
    except UnicodeError:return None,offset


def inspect_save(path):
    path=Path(path)
    size=path.stat().st_size
    with path.open('rb') as f: head=f.read(4096)
    mod, off=read_len_utf16(head,2) if head.startswith(b'\x0a\x0b') else (None,0)
    # Campaign field occurs in header after binary metadata: identify known length-prefixed UTF16 string.
    campaign=None
    for name in ('imperial_campaign','british_isles','crusades','teutonic','americas'):
        token=name.encode('utf-16le')
        if head.find(token)>0:campaign=name;break
    return {'path':str(path.resolve()),'filename':path.name,'bytes':size,
        'modified':datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'mod':mod or 'Nie rozpoznano', 'campaign':campaign or 'Nie rozpoznano',
        'format':'Medieval II (nagłówek)' if mod else 'Nieznany / niepotwierdzony',
        'editable':False}


def discover_saves(data_dir, cap=2000):
    if not data_dir:return []
    data=Path(data_dir).resolve()
    root=data.parent if data.name.lower()=='data' else data
    # Game and selected mod, no full recursive scans of huge game trees.
    game=None
    for parent in (root,*list(root.parents)[:8]):
        if (parent/'medieval2.exe').exists() or (parent/'kingdoms.exe').exists(): game=parent; break
    candidates=[root/'saves',root/'data'/'saves']
    if game:
        candidates += [game/'saves',game/'data'/'saves']
        # Save files can also be inside mod saves folder.
        if root!=game: candidates.append(game/'mods'/root.name/'saves')
    seen=set(); found=[]
    for folder in candidates:
        if not folder.is_dir(): continue
        for p in folder.glob('*.sav'):
            k=str(p.resolve()).lower()
            if k not in seen:
                seen.add(k);found.append(p)
                if len(found)>=cap:break
    return sorted(found,key=lambda x:x.stat().st_mtime,reverse=True)
