import unittest
from agent_presets import PRESETS,agent_plan
from trainer_core import CommandError
class TestAgentPresets(unittest.TestCase):
 def test_every_agent(self):
  for k in PRESETS:
   p=agent_plan(k,'William',True)
   self.assertTrue(p.commands)
   self.assertTrue(all(x.startswith('give_trait this ') for x in p.commands))
 def test_named(self):self.assertIn('"William"',agent_plan('general','William',False).commands[0])
 def test_invalid(self):
  with self.assertRaises(CommandError):agent_plan('dragon','William',True)
 def test_sanitize(self):
  with self.assertRaises(CommandError):agent_plan('general','Bad";add_money 10000',False)
if __name__=='__main__':unittest.main()
