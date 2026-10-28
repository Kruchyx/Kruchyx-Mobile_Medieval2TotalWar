import os,sys
from pathlib import Path
from tkinter import messagebox
from PIL import ImageGrab
from kruchyx_studio import App
from vanilla_guide import open_vanilla_guide

a=App();a.geometry('1440x880');a.update_idletasks()
a.lang='pl';a.show('calculators');a.update()
assert a.page=='calculators'
assert len(a.body.winfo_children()) > 0
img=ImageGrab.grab(bbox=(0,0,1440,880))
img.save('/mnt/data/Kruchyx_v0.9.3_Kalkulator_PODGLAD.png')
for lng in ('en','pl'):
    a.lang=lng
    for p in ('exploits','calculators','library','academy','trainer','advisor'):
        a.show(p);a.update_idletasks();a.update();assert a.page==p
    dlg=open_vanilla_guide(a,None);a.update();assert dlg.winfo_exists();dlg.destroy()
a.destroy()
print('GUI Smoke PL/EN OK')
