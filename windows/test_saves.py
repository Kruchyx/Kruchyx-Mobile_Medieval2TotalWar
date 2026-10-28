import unittest, tempfile
from pathlib import Path
from save_inspector import inspect_save,discover_saves
class Tests(unittest.TestCase):
 def test_kirsi_save_header(self):
  p=Path('/mnt/data/Polskakrachnagieldzi.sav')
  if not p.exists():self.skipTest('user fixture not supplied')
  x=inspect_save(p)
  self.assertEqual(x['mod'],'mods/kirsi_biggermap_medieval2/data')
  self.assertEqual(x['campaign'],'imperial_campaign')
  self.assertFalse(x['editable'])
 def test_invalid_save_never_claims_valid(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'foo.sav';p.write_bytes(b'blah')
   x=inspect_save(p);self.assertEqual(x['format'],'Nieznany / niepotwierdzony')
 def test_discovery(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'data';p.mkdir();s=Path(t)/'saves';s.mkdir();(s/'x.sav').write_bytes(b'x')
   self.assertEqual(len(discover_saves(p)),1)
if __name__=='__main__':unittest.main()
