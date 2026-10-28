import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vanilla_support import unpack_vanilla, diagnose_unpack


class VanillaDiagnosticsTests(unittest.TestCase):
    def create_game(self, folder):
        game = Path(folder) / 'Medieval II Total War'
        (game/'packs').mkdir(parents=True)
        (game/'packs'/'data_0.pack').touch()
        (game/'tools'/'unpacker').mkdir(parents=True)
        (game/'tools'/'unpacker'/'unpacker.exe').touch()
        (game/'medieval2.exe').touch()
        return game

    def test_relative_legacy_source_and_yes_answers(self):
        with tempfile.TemporaryDirectory() as d:
            game=self.create_game(d);cache=Path(d)/'Cache'
            class FakeResult:
                returncode=1
                stdout='legacy extractor error'
                stderr=''
            with patch('vanilla_support.subprocess.run',return_value=FakeResult()) as runner:
                result=unpack_vanilla(game,cache)
            self.assertFalse(result['success'])
            self.assertTrue(result['log_path'].is_file())
            self.assertIn('legacy extractor error',result['log_path'].read_text())
            cmd=runner.call_args.args[0]
            self.assertEqual(runner.call_count,6)
            self.assertIn('..\\..\\packs\\*.pack',' '.join(cmd))
            self.assertEqual(runner.call_args.kwargs['input'],'Y\nY\nY\n')
            self.assertEqual(runner.call_args.kwargs['cwd'],str((game/'tools'/'unpacker').resolve()))
            self.assertIn('--mode=0',cmd)

    def test_missing_legacy_dll_is_explained(self):
        result=[{'filter':'export_descr_unit.txt','log':'msvcp71.dll was not found'}]
        self.assertIn('msvcp71.dll',diagnose_unpack(result))
        self.assertIn('DLL',diagnose_unpack(result,lang='en'))

    def test_no_extraction_is_not_success(self):
        with tempfile.TemporaryDirectory() as d:
            game=self.create_game(d);cache=Path(d)/'Cache'
            class FakeResult:
                returncode=0
                stdout='Done'
                stderr=''
            with patch('vanilla_support.subprocess.run',return_value=FakeResult()):
                outcome=unpack_vanilla(game,cache)
            self.assertFalse(outcome['success'])
            self.assertEqual(sum(outcome['found'].values()),0)

if __name__=='__main__': unittest.main()
