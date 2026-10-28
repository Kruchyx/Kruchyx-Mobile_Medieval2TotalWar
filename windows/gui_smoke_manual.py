"""GUI smoke test; run with xvfb-run python test_gui_smoke_manual.py"""
from kruchyx_studio import App
from PIL import ImageGrab
from pathlib import Path
import traceback

app=App()
app.update_idletasks();app.update()
app.load_demo()
app.update_idletasks();app.update()
for lang in ('pl','en'):
    if app.lang!=lang:app.toggle_language()
    for page in ('welcome','advisor','units','economy','intelligence','academy','exploits','trainer','editor','saves','library'):
        app.show(page)
        app.update_idletasks();app.update()
        print('OK',lang,page,flush=True)
    if lang=='en':
        app.show('advisor');app.update_idletasks();app.update()
        ImageGrab.grab().save('/mnt/data/Kruchyx_v0.9.2_Doradca_EN.png')
        app.show('exploits');app.update_idletasks();app.update()
        ImageGrab.grab().save('/mnt/data/Kruchyx_v0.9.2_Sekrety_EN.png')
        app.show('library');app.update_idletasks();app.update()
        ImageGrab.grab().save('/mnt/data/Kruchyx_v0.9.2_Biblioteka_EN.png')
app.destroy()
