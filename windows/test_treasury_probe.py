import unittest
from pathlib import Path
from treasury_probe import probe_treasury
class TreasuryTests(unittest.TestCase):
    def test_three_user_samples(self):
        root = Path(__file__).parent / 'fixtures' / 'sav_tests'
        if not root.exists(): self.skipTest('Optional real samples not distributed')
        for n,v in [(1,10000),(2,20000),(3,25000)]:
            self.assertEqual(probe_treasury(root / f'Test_anglia{n}.sav')['value'],v)
    def test_unknown(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'unknown.sav';p.write_bytes(b'test')
            self.assertEqual(probe_treasury(p)['status'],'unavailable')
if __name__=='__main__': unittest.main()
