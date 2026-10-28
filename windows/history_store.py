"""Durable history for Medieval II Mod Studio. No game file is changed by scanning."""
import os, json, hashlib, shutil, tempfile
from pathlib import Path
from datetime import datetime


def store_dir():
    root=Path(os.getenv('LOCALAPPDATA') or (Path.home()/'.local'/'share'))/'MedievalModStudio'/'history'
    root.mkdir(parents=True,exist_ok=True)
    return root

def key(path):
    return hashlib.sha256(str(Path(path).resolve()).lower().encode('utf-8')).hexdigest()[:24]

def sha(data):return hashlib.sha256(data).hexdigest()

class History:
    def __init__(self, root=None):
        self.root=Path(root) if root is not None else store_dir()
        self.root.mkdir(parents=True,exist_ok=True)
        self.index_path=self.root/'history.json'
        try:self.index=json.loads(self.index_path.read_text(encoding='utf-8'))
        except (ValueError,OSError):self.index=[]

    def persist(self):
        tmp=self.index_path.with_suffix('.tmp')
        tmp.write_text(json.dumps(self.index,ensure_ascii=False,indent=2),encoding='utf-8')
        os.replace(tmp,self.index_path)

    def entries(self,path=None):
        return [x for x in reversed(self.index) if path is None or x['path']==str(Path(path).resolve())]

    def snapshot(self,path,before,after,kind='zapis'):
        path=Path(path).resolve()
        stamp=datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        folder=self.root/key(path)
        folder.mkdir(parents=True,exist_ok=True)
        first=folder/'original.bin'
        if not first.exists():first.write_bytes(before)
        before_name=stamp+'_before.bin';after_name=stamp+'_after.bin'
        (folder/before_name).write_bytes(before)
        (folder/after_name).write_bytes(after)
        entry={'id':stamp+'_'+key(path),'time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'path':str(path),'before':str(folder/before_name),'after':str(folder/after_name),'before_hash':sha(before),'after_hash':sha(after),'kind':kind}
        self.index.append(entry);self.persist()
        return entry

    def restore(self,path,snapshot_path,kind='przywrócenie'):
        path=Path(path).resolve();snapshot=Path(snapshot_path)
        if not path.is_file():raise FileNotFoundError(path)
        desired=snapshot.read_bytes();current=path.read_bytes()
        if desired==current:return False
        folder=path.parent
        fd,temp=tempfile.mkstemp(prefix='.modstudio_',dir=folder)
        try:
            with os.fdopen(fd,'wb') as handle:
                handle.write(desired);handle.flush();os.fsync(handle.fileno())
            os.replace(temp,path)
        finally:
            if os.path.exists(temp):os.unlink(temp)
        self.snapshot(path,current,desired,kind)
        return True

    def original(self,path):
        p=self.root/key(path)/'original.bin'
        return p if p.exists() else None


def edu_candidates(data):
    """Find loose EDU only. Packs require external extraction; do not pretend otherwise."""
    data=Path(data).resolve()
    choices=[data/'export_descr_unit.txt']
    modroot=data.parent if data.name.lower()=='data' else data
    for parent in [modroot,*list(modroot.parents)[:6]]:
        if (parent/'medieval2.exe').is_file() or (parent/'kingdoms.exe').is_file():
            choices.append(parent/'data'/'export_descr_unit.txt')
            break
    return [(p,'MOD' if i==0 else 'GRA PODSTAWOWA') for i,p in enumerate(choices) if p.is_file()]
