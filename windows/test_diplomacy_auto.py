import unittest
from diplomacy_auto import suggest_offer

class OfferTests(unittest.TestCase):
    def test_thirty_thousand(self):
        result=suggest_offer(30000)
        self.assertEqual((result.gift,result.demand_per_turn,result.reserve,result.break_even_payments),(10000,4000,20000,3))
    def test_presets(self):
        self.assertEqual(suggest_offer(30000,'ostrozny').gift,6000)
        self.assertEqual(suggest_offer(30000,'agresywny').gift,15000)
    def test_reject(self):
        self.assertEqual(suggest_offer(30000,adjustment=1).demand_per_turn,3600)
        self.assertEqual(suggest_offer(30000,adjustment=9).demand_per_turn,400)
    def test_bad_values(self):
        for money in ('foo','-1','2000000001'):
            with self.assertRaises(ValueError): suggest_offer(money)

if __name__=='__main__': unittest.main()
