import tempfile,unittest
from pathlib import Path
from history_store import History,edu_candidates

class TestHistory(unittest.TestCase):
 def test_save_persists_and_restore(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=root/'descr_strat.txt';p.write_bytes(b'old\r\n')
   h=History(root/'history');p.write_bytes(b'new\r\n');h.snapshot(p,b'old\r\n',b'new\r\n')
   fresh=History(root/'history')
   self.assertEqual(len(fresh.entries(p)),1)
   fresh.restore(p,Path(fresh.entries(p)[0]['before']))
   self.assertEqual(p.read_bytes(),b'old\r\n')
   self.assertEqual(len(History(root/'history').entries(p)),2)
   self.assertEqual(fresh.original(p).read_bytes(),b'old\r\n')
 def test_edu_discovery(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'medieval2.exe').touch();mod=root/'mods'/'KIRSI'/'data';mod.mkdir(parents=True)
   (root/'data').mkdir();(root/'data'/'export_descr_unit.txt').write_text('x')
   self.assertEqual(edu_candidates(mod)[0][1],'GRA PODSTAWOWA')
   (mod/'export_descr_unit.txt').write_text('y')
   self.assertEqual(edu_candidates(mod)[0][1],'MOD')
if __name__=='__main__':unittest.main()
