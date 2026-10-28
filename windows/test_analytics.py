import unittest
from pathlib import Path
from unit_analytics import parse_units,parse_resources,faction_ranking,decode,scan_mod
class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.units=parse_units(decode('/mnt/data/export_descr_unit(6).txt'))
    def test_count(self):self.assertEqual(len(self.units),553)
    def test_factions(self):self.assertIn('poland',[x['name'] for x in faction_ranking(self.units)])
    def test_ship(self):self.assertEqual(len([x for x in self.units if x['role']=='Okręty']),21)
    def test_resource(self):self.assertEqual(parse_resources(decode('/mnt/data/descr_sm_resources.txt'))[0]['name'],'gold')
    def test_no_comments(self):
        u=parse_units('; type Fake\ntype Real\ncategory infantry\nclass heavy\nstat_pri 12, 2, no\nstat_pri_armour 2, 3, 4, metal\nownership england, france\n')
        self.assertEqual(len(u),1);self.assertEqual(u[0]['name'],'Real')
    def test_score(self):
        knight=next(u for u in self.units if u['name']=='Polish Knights')
        self.assertIn('poland',knight['owners']);self.assertGreater(knight['score'],0)
if __name__=='__main__':unittest.main()
