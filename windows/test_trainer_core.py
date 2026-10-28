import unittest
import tempfile
from pathlib import Path
import trainer_core as t

class TrainerTests(unittest.TestCase):
    def test_money_chunks(self):
        p=t.money('1000000');self.assertEqual(len(p.commands),25);self.assertTrue(all(x=='add_money 40000' for x in p.commands))
    def test_money_partial(self):self.assertEqual(t.money(80001).commands,('add_money 40000','add_money 40000','add_money 1'))
    def test_money_limits(self):
        for n in (-1,0,20000001,'foo'):
            with self.assertRaises(t.CommandError):t.money(n)
    def test_unit(self):self.assertEqual(t.unit('London','Spear Militia',2,9,3,3).commands[0], 'create_unit "London" "Spear Militia" 2 9 3 3')
    def test_unit_validation(self):
        with self.assertRaises(t.CommandError):t.unit('London','Spears',6,0,0,0)
    def test_name_injection(self):
        with self.assertRaises(t.CommandError):t.building('London"\nadd_money 999')
    def test_build(self):self.assertEqual(t.building('London').commands,('process_cq "London"',))
    def test_population(self):self.assertEqual(t.population('London',12345).commands,('add_population "London" 12345',))
    def test_movement(self):self.assertEqual(t.movement('William').commands,('character_reset "William"',))
    def test_teleport(self):self.assertEqual(t.teleport('William',10,20).commands,('move_character "William" 10 20',))
    def test_trait(self):self.assertEqual(t.trait('William','GoodCommander',3).commands,('give_trait "William" GoodCommander 3',))
    def test_quick(self):self.assertEqual(t.quick('fog').commands,('toggle_fow',))
    def test_export(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cheats.txt';t.export_plan(p,t.money(40000));self.assertIn('add_money 40000',p.read_text(encoding='utf-8'))

if __name__=='__main__': unittest.main()
