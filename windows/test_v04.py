import unittest
from modstudio import edit_faction_field, edit_settlement_population, settlement_options, edit_campaign_year, faction_field_options
S='''start_date 1080\nend_date 1530\nfaction england, balanced smith\n denari 1000\n denari_kings_purse 150\nsettlement\n{\n level city\n region London_Province\n year_founded 0\n population 3000\n building\n {\n  type core_building wooden_pallisade\n }\n}\nfaction france, balanced smith\n denari 2000\n denari_kings_purse 300\nsettlement\n{\n region Paris_Province\n population 4000\n}\n'''
class Test(unittest.TestCase):
 def test_faction(self):
  new=edit_faction_field(S,'england','denari_kings_purse',999)
  assert 'denari_kings_purse 999' in new and 'denari_kings_purse 300' in new
 def test_pop(self):
  assert len(settlement_options(S))==2
  new=edit_settlement_population(S,'London_Province',7000)
  assert 'population 7000' in new and 'population 4000' in new
 def test_year(self):
  new=edit_campaign_year(S,'start_date',1200)
  assert 'start_date 1200' in new and 'end_date 1530' in new
 def test_preserve(self):
  assert edit_settlement_population(S,'Paris_Province',4000)==S
if __name__=='__main__':unittest.main()
