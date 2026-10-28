import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from vanilla_support import (find_loose_vanilla_files, vanilla_file_availability,
                             unpack_vanilla)
from mod_insights import file_capabilities

class VanillaFallbackTests(unittest.TestCase):
    def make_game(self, tmp):
        game=Path(tmp)/'Medieval II Total War'
        (game/'packs').mkdir(parents=True)
        (game/'packs'/'data_0.pack').touch()
        (game/'tools'/'unpacker').mkdir(parents=True)
        (game/'tools'/'unpacker'/'unpacker.exe').touch()
        (game/'medieval2.exe').touch()
        regions=game/'data/world/maps/base/descr_regions.txt'
        campaign=game/'data/world/maps/campaign/imperial_campaign/descr_strat.txt'
        regions.parent.mkdir(parents=True);regions.write_text('test_region',encoding='utf8')
        campaign.parent.mkdir(parents=True);campaign.write_text('campaign imperial_campaign',encoding='utf8')
        return game,regions,campaign

    def test_loose_definitions_discovered_and_unmodified(self):
        with tempfile.TemporaryDirectory() as tmp:
            game,regions,campaign=self.make_game(tmp)
            avail=vanilla_file_availability(game,Path(tmp)/'external_cache')
            self.assertTrue(avail['found']['descr_regions.txt'])
            self.assertTrue(avail['found']['descr_strat.txt'])
            self.assertEqual(avail['sources']['descr_strat.txt'],'game')
            self.assertEqual(avail['sources']['descr_regions.txt'],'game')
            self.assertEqual(regions.read_text(),'test_region')
            self.assertEqual(campaign.read_text(),'campaign imperial_campaign')
            context=file_capabilities(game)
            self.assertEqual(context['files']['regions'],regions.resolve())
            self.assertEqual(context['files']['campaign'],campaign.resolve())

    def test_unpack_combines_cache_and_loose_and_logs_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            game,regions,campaign=self.make_game(tmp)
            cache=Path(tmp)/'external_cache'
            class FakeResult:
                returncode=0
                stdout='Successfully extracted all pack files'
                stderr=''
            def fake_run(*args,**kwargs):
                cmd=args[0]
                if '--filter=export_descr_unit.txt' in cmd:
                    outfile=cache/'data/export_descr_unit.txt'
                    outfile.parent.mkdir(parents=True,exist_ok=True)
                    outfile.write_text('type TEST\n',encoding='utf8')
                return FakeResult()
            with patch('vanilla_support.subprocess.run',side_effect=fake_run):
                got=unpack_vanilla(game,cache)
            self.assertTrue(got['success'])
            self.assertEqual(got['sources']['export_descr_unit.txt'],'cache')
            self.assertEqual(got['sources']['descr_regions.txt'],'game')
            self.assertEqual(got['sources']['descr_strat.txt'],'game')
            text=got['log_path'].read_text(encoding='utf8')
            self.assertIn('FOUND_IN_GAME_FOLDER:',text)
            self.assertIn('FILE_SOURCES:',text)
            self.assertIn(str(campaign.resolve()),text)
            self.assertEqual(regions.read_text(),'test_region')
            self.assertEqual(campaign.read_text(),'campaign imperial_campaign')

    def test_missing_loose_facts_reported_as_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            game,regions,campaign=self.make_game(tmp)
            regions.unlink();campaign.unlink()
            got=vanilla_file_availability(game,Path(tmp)/'external_cache')
            self.assertFalse(got['found']['descr_regions.txt'])
            self.assertFalse(got['found']['descr_strat.txt'])
            self.assertEqual(got['sources']['descr_strat.txt'],'missing')

if __name__=='__main__':unittest.main()
