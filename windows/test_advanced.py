import unittest,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import advanced as a
from modstudio import read_text, money_options
SAMPLE=Path(__file__).parent/'fixtures'/'kirsi_descr_strat.txt'
class TestAdvanced(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.t=read_text(SAMPLE)[0]
 def test_source(self):
  self.assertEqual(len(money_options(self.t)),22)
  self.assertEqual(len(a.playable_factions(self.t)),22)
 def test_city(self):
  r=next(x for x in a.settlements(self.t) if x['region']=='London_Region')
  self.assertEqual(r['pop'],'3800')
  t=a.edit_settlement(self.t,'London_Region','population','4444')
  self.assertEqual(next(x for x in a.settlements(t) if x['region']=='London_Region')['pop'],'4444')
  self.assertEqual(t.count('\r\n'),self.t.count('\r\n'))
 def test_city_owner(self):
  t=a.edit_settlement(self.t,'London_Region','owner','france')
  self.assertEqual(next(x for x in a.settlements(t) if x['region']=='London_Region')['faction'],'france')
 def test_city_level_building(self):
  t=a.edit_settlement(self.t,'London_Region','level','city')
  t=a.edit_settlement(t,'London_Region','building','core_building stone_wall')
  self.assertEqual(next(x for x in a.settlements(t) if x['region']=='London_Region')['level'],'city')
 def test_character(self):
  self.assertTrue(any(x['name']=='William' for x in a.characters(self.t)))
  t=a.edit_character(self.t,'england','William','age','34')
  self.assertEqual(next(x for x in a.characters(t) if x['name']=='William')['age'],'34')
  t=a.edit_character(t,'england','William','exp','5',0)
  self.assertEqual(next(x for x in a.characters(t) if x['name']=='William')['units'][0][1],'5')
 def test_playable(self):
  t=a.edit_playability(self.t,'mongols','playable')
  self.assertEqual(a.playable_factions(t)['mongols'],'playable')
 def test_relationship(self):
  t=a.edit_relationship(self.t,'poland','france','allied_to')
  self.assertIn(('poland','allied_to','france'),a.relationships(t))
 def test_edu(self):
  sample='type Knights\r\nstat_cost 1, 500, 200, 100, 100\r\nstat_pri 12, 1, no, 0\r\n'
  t=a.edit_unit_stat(sample,'Knights','stat_cost',1,'600')
  self.assertIn('stat_cost 1, 600, 200',t)
if __name__=='__main__':unittest.main()
