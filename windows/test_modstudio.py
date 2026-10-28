import unittest
from modstudio import edit_money,money_options,edit_unit_cost,edu_units,resolve_data_folder,campaign_paths
S='''playable\n england\nend\nfaction england, balanced smith\n denari 5000\n settlement\n{\n}\nfaction france, balanced smith\n denari 7000\n'''
U='''type Longbowmen\nstat_cost 0, 560, 150, 65, 50, 560, 4, 140\ntype Knights\nstat_cost 0, 800, 220, 65, 50, 560, 4, 140\n'''
class Test(unittest.TestCase):
 def test_money(self):
  x=edit_money(S,'england',12345)
  self.assertIn('denari 12345',x)
  self.assertIn('denari 7000',x)
  self.assertEqual(len(money_options(S)),2)
 def test_units(self):
  x=edit_unit_cost(U,'Longbowmen',1000,200)
  self.assertIn('stat_cost 0, 1000, 200, 65',x)
  self.assertIn('stat_cost 0, 800, 220',x)
  self.assertEqual(len(edu_units(U)),2)
 def test_folder_selection(self):
  from tempfile import TemporaryDirectory
  from pathlib import Path
  with TemporaryDirectory() as temp:
   root=Path(temp); data=root/'data'; camp=data/'world/maps/campaign/custom_camp'
   camp.mkdir(parents=True)
   (camp/'descr_strat.txt').write_text(S)
   self.assertEqual(resolve_data_folder(root),data)
   self.assertEqual(resolve_data_folder(data),data)
   self.assertEqual(campaign_paths(data),[camp/'descr_strat.txt'])
if __name__=='__main__':unittest.main()
