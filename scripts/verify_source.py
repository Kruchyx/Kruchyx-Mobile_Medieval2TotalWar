"""Simple offline integrity check (stdlib only), run: python scripts/verify_source.py"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'mobile'/'kruchyx_mobile'
assets=APP/'assets'
codex=json.loads((assets/'codex_v096.json').read_text(encoding='utf-8'))
mechanics=json.loads((assets/'mechanics_v096.json').read_text(encoding='utf-8'))
report=json.loads((assets/'demo_report.json').read_text(encoding='utf-8'))
assert codex['schema']=='kruchyx-codex-v1'
assert len(codex['factions'])==22,len(codex['factions'])
assert len(set(f['id'] for f in codex['factions']))==22
assert len(codex['cities'])==24,len(codex['cities'])
assert len(mechanics['articles'])==32,len(mechanics['articles'])
assert report['sample'] is True
assert report['schema']=='kruchyx-companion-v1'
for f in codex['factions']:
    assert (APP/f['art']).is_file(), f['art']
assert (assets/'codex_banner.png').is_file()
for file in ['.github/workflows/build-android.yml','.github/workflows/build-windows.yml','.github/workflows/build-ios.yml',
             'mobile/kruchyx_mobile/pubspec.yaml','windows/kruchyx_studio.py','windows/diplomacy_auto.py',
             'docs/INSTRUKCJA_GITHUB_PL.md']:
    assert (ROOT/file).is_file(),file
assert 'android-actions/setup-android@v4' in (ROOT/'.github/workflows/build-android.yml').read_text()
print(f"OK: {len(codex['factions'])} frakcje, {len(codex['cities'])} miasta, {len(mechanics['articles'])} mechanik, grafiki i konfiguracja")
