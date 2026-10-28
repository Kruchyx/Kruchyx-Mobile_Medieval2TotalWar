from pathlib import Path
from tempfile import TemporaryDirectory
from academy_content import LESSONS, FIRST_TURNS, SOURCES, L, pick, advice_for_faction, battle_tip, building_tip
from campaign_intelligence import inspect_campaign, economy_ranking, detect_findings, diplomacy_advice
from mod_insights import analyze

# Test a synthetic campaign; never require proprietary installation files.
SAMPLE='''playable\n england\n poland\nend\nfaction england, balanced smith random\ndenari 10000\nsettlement {\n level large_town\n region London_Region\n population 3500\n building { type core_building wooden_wall }\n}\nfaction poland, balanced smith random\ndenari 12000\nsettlement castle {\n level castle\n region Cracow_Province\n population 1200\n}\nfaction slave, balanced smith random\ndenari 0\nsettlement {\n region Rebel_Region\n population 800\n}\nfaction_standings england, 0.30 poland\nfaction_standings england, -0.50 slave\nfaction_relationships england, allied_to poland\nfaction_relationships england, at_war_with slave\n'''

def test_content_full_translation():
    assert len(LESSONS)>=12
    assert len(FIRST_TURNS)>=10
    assert len(SOURCES)>=3
    assert all(len(x[4])>=4 for x in LESSONS)
    for x in LESSONS:
        assert L(x[2],'en') and L(x[2],'pl')
        for item in x[4]:assert item[0]!=item[1]
    assert pick('cheats') and pick('economy')

def test_building_and_battle_advice():
    assert 'port' in building_tip('city','income','en')
    assert 'włócz' in battle_tip('cavalry','pl')
    assert 'Castle:' in building_tip('castle','defense','en')

def test_initial_economy_and_diplomacy():
    with TemporaryDirectory() as d:
        p=Path(d)/'descr_strat.txt';p.write_text(SAMPLE)
        result=inspect_campaign(p)
    factions=result['factions']
    assert factions['england']['money']==10000
    assert factions['england']['total_population']==3500
    assert len(factions['england']['settlements'])==1
    assert factions['poland']['castle_count']==1
    assert factions['slave']['settlements'][0]['name']=='Rebel_Region'
    assert factions['england']['relationships']['allied_to']==['poland']
    assert any('poland' in x[0] for x in diplomacy_advice(result,'england','en'))
    ranked=economy_ranking(result)
    assert len(ranked)==2 and 'slave' not in [x['name'] for x in ranked]
    assert 0<=ranked[0]['score']<=100

def test_missing_campaign_not_faked():
    r=inspect_campaign(None)
    assert r['factions']=={}
    assert economy_ranking(r)==[]

def test_findings_mark_garrison_as_potential():
    with TemporaryDirectory() as d:
        root=Path(d); camp=root/'descr_strat.txt';camp.write_text(SAMPLE)
        ctx={'folder':root,'files':{'campaign':camp,'buildings':None,'edu':None,'resources':None}}
        findings=detect_findings(ctx)
    r=[x for x in findings if x['kind']=='opportunity']
    assert len(r)==1
    assert r[0]['confidence']=='potential'
    assert 'garnizonu' in r[0]['body'][0]

def test_demo_runs_without_campaign():
    folder=Path(__file__).resolve().parent/'examples'
    model=analyze(folder)
    assert len(model['units'])>500
    assert model['context']['files']['campaign'] is None
    assert advice_for_faction(model,'england','pl')
