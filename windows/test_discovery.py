import tempfile,unittest
from pathlib import Path
from discovery import find_data_candidates,scan_campaigns
from modstudio import read_text,money_options,edit_money

class DiscoveryTests(unittest.TestCase):
    def test_deep_kirsi_campaign(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'Medieval II Total War';data=root/'mods'/'kirsi_biggermap_medieval2'/'data'
            c=data/'world'/'maps'/'campaign'/'imperial_campaign'/'descr_strat.txt'
            c.parent.mkdir(parents=True);c.write_text('faction england, balanced smith\n denari 10000\n')
            self.assertEqual(find_data_candidates(root),[data.resolve()]);self.assertEqual(scan_campaigns(data),[c.resolve()])
            self.assertEqual(find_data_candidates(data),[data.resolve()])
    def test_multiple_campaigns(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t)/'data'
            for x in ('custom','imperial_campaign'):
                p=d/'world'/'maps'/'campaign'/x/'descr_strat.txt';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('')
            self.assertEqual([p.parent.name for p in scan_campaigns(d)],['imperial_campaign','custom'])
    def test_kirsi_factions(self):
        p=Path(__file__).parent/'fixtures'/'kirsi_descr_strat.txt'
        if not p.exists():self.skipTest('Brak kopii KIRSI')
        content,_=read_text(p)
        self.assertGreaterEqual(len(money_options(content)),20)
        self.assertRegex(edit_money(content,'england',12345),r'(?m)^\s*denari\s+12345\b')
if __name__=='__main__':unittest.main()
