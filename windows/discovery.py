"""Rozpoznawanie katalogów modów Medieval II, bez zmiany plików."""
from pathlib import Path

def find_data_candidates(folder: Path):
    root=Path(folder)
    if not root.is_dir():return []
    result=[]
    def add(p):
        if p.is_dir() and p.resolve() not in result:result.append(p.resolve())
    if root.name.lower()=='data':add(root)
    add(root/'data')
    # Gra: mods/<nazwa_moda>/data
    mods=root/'mods'
    if mods.is_dir():
        for mod in sorted(mods.iterdir()):
            if mod.is_dir():add(mod/'data')
    # Możliwe: wybrany katalog mods albo niestandardowy katalog zbiorczy
    if root.name.lower()=='mods':
        for mod in sorted(root.iterdir()):
            if mod.is_dir():add(mod/'data')
    return result

def scan_campaigns(data_folder: Path):
    data=Path(data_folder)
    if not data.is_dir():return []
    # Standardowa ścieżka (z dowolną nazwą kampanii), bez rekurencji po ogromnej mapie.
    base=data/'world'/'maps'/'campaign'
    if not base.is_dir():return []
    return sorted((p.resolve() for p in base.glob('*/descr_strat.txt') if p.is_file()),key=lambda p:(p.parent.name.lower()!='imperial_campaign',str(p).lower()))
