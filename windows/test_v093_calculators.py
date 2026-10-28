import tempfile
import unittest
from pathlib import Path

from tribute_calculator import amount,tribute_scenario,merchant_scenario,variants,clipboard_plan
from vanilla_guide import manual_commands,guide_steps

class CalculatorGuideTests(unittest.TestCase):
    def test_reference_scenario(self):
        p=tribute_scenario('3 333 333',0,30,99_999_999)
        self.assertEqual((p.gift,p.per_turn,p.after_one_payment,p.break_even_payments),
                         (3_333_333,1_000_000,-2_333_333,4))
        self.assertEqual(p.after_five_payments,1_666_667)

    def test_reserve_preserved_and_no_ai_predictions(self):
        p=tribute_scenario('4.000.000',1_000_000,25)
        self.assertEqual((p.gift,p.per_turn,p.reserve),(3_000_000,750_000,1_000_000))
        self.assertIn('arytmetyka',clipboard_plan(p).lower())
        self.assertIn('arithmetic only',clipboard_plan(p,'en'))

    def test_bad_data_rejected(self):
        for cash,res in ((0,0),(100,100),(50,70),(-2,0)):
            with self.subTest(cash=cash,res=res):
                with self.assertRaises(ValueError):tribute_scenario(cash,res)
        with self.assertRaises(ValueError):tribute_scenario(100,0,0)
        with self.assertRaises(ValueError):tribute_scenario(100,0,201)
        with self.assertRaises(ValueError):tribute_scenario(100,0,30,100_000_000)
        with self.assertRaises(ValueError):tribute_scenario(2_147_483_647,0,200)
        with self.assertRaises(ValueError):amount('3 33 333')

    def test_merchant_not_predicted(self):
        m=merchant_scenario('500',5,70)
        self.assertEqual((m.simple_upper_bound,m.illustrative_income),(2500,1750))

    def test_variants(self):
        self.assertEqual([x.per_turn for x in variants(1_000_000)], [100_000,200_000,300_000,500_000])

    def test_safe_manual_path(self):
        with tempfile.TemporaryDirectory() as d:
            game=Path(d)/'Some Medieval II';unpacker=game/'tools'/'unpacker';unpacker.mkdir(parents=True)
            (unpacker/'unpacker.exe').write_bytes(b'not executable test')
            plan=manual_commands(game)
            self.assertIn('--filter=export_descr_unit.txt',plan)
            self.assertIn('--filter=descr_strat.txt',plan)
            self.assertNotIn('unpack_all.bat',plan)
            self.assertNotIn(f'--destination="{game}',plan)
            self.assertIn('vanilla_cache',plan)

    def test_guides_both_languages(self):
        self.assertGreaterEqual(len(guide_steps('pl')),6)
        self.assertIn('game',str(guide_steps('en')).lower())

if __name__=='__main__':unittest.main()
