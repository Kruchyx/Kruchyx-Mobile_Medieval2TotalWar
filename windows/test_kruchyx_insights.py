from pathlib import Path
from mod_insights import analyze,report,file_capabilities,campaign_info,mod_summary,leaders_by_role,explanation
ROOT=Path(__file__).parent

def test_demo_edu_counts():
    m=analyze(ROOT/'examples')
    assert len(m['units'])==553
    assert len(m['factions'])==44
    assert sum(u['role']=='Okręty' for u in m['units'])==21

def test_folder_resolution():
    m=file_capabilities(ROOT/'examples')
    assert m['files']['edu'].name=='export_descr_unit.txt'
    assert m['files']['resources'] is not None
    assert m['files']['campaign'] is None

def test_report_qualified():
    r=report(analyze(ROOT/'examples'))
    assert 'niezweryfikowana' in r.lower()
    assert 'Wykonane przez Kruchyx' in r
    assert 'Anglia' in r

def test_deterministic():
    a=analyze(ROOT/'examples');b=analyze(ROOT/'examples')
    assert [(f['name'],f['score']) for f in a['factions']]==[(f['name'],f['score']) for f in b['factions']]

def test_explanation_no_false_start_claim():
    m=analyze(ROOT/'examples');ex=explanation(m['factions'][0])
    assert 'jednostek' in ex and m['factions'][0]['display'] in ex
    assert 'gospodark' not in ex.lower()

def test_specialists_are_in_roster():
    m=analyze(ROOT/'examples')
    for score,f in leaders_by_role(m,'Kawaleria wręcz'):
        assert f['role_best']['Kawaleria wręcz']
        assert score>0

def test_summary_is_source_specific():
    m=analyze(ROOT/'examples')
    s=mod_summary(m)
    assert '553' in s and '44' in s and '21' in s

def test_missing_edu_graceful(tmp_path):
    (tmp_path/'data').mkdir()
    (tmp_path/'data'/'descr_sm_resources.txt').write_text('type gold\ntrade_value 20\n')
    m=analyze(tmp_path)
    assert m['units']==[] and m['factions']==[]
    assert 'BRAK EDU' in report(m)

def test_campaign_money(tmp_path):
    fp=tmp_path/'descr_strat.txt'
    fp.write_text('start_date 1080\nplayable\n england\n poland\nend\nfaction england, balanced smith\n denari 10000\nsettlement { region London_Province population 1000 }\nfaction poland, balanced smith\n denari 12000\n')
    info=campaign_info(fp)
    assert info['start_date']==1080
    assert info['factions']['england']['money']==10000
    assert info['factions']['poland']['money']==12000
