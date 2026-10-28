import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from exploit_library import GUIDES, money_scenario
from vanilla_support import is_game_root,find_game_root,list_campaign_choices,find_unpacker,unpack_vanilla
from mod_insights import analyze,explanation_en,mod_summary_en,file_capabilities
from ui_i18n import tr

class BrotherEditionTests(unittest.TestCase):
    def mock_game(self,path):
        game=Path(path)/'Medieval II Total War'
        game.mkdir();(game/'medieval2.exe').touch()
        (game/'packs').mkdir();(game/'packs'/'data_0.pack').touch()
        unpacker=game/'tools'/'unpacker';unpacker.mkdir(parents=True)
        (unpacker/'unpacker.exe').touch()
        return game

    def test_vanilla_always_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=self.mock_game(tmp)
            for name in ('teutonic','vanilla_kingdoms_uncompromised'):
                (game/'mods'/name/'data').mkdir(parents=True)
            picks=list_campaign_choices(game)
            self.assertEqual(picks[0]['kind'],'vanilla')
            self.assertEqual([x['id'] for x in picks[1:]],['teutonic','vanilla_kingdoms_uncompromised'])
            self.assertEqual(find_game_root(game/'mods'/'teutonic'),game)

    def test_cache_isolation_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=self.mock_game(tmp)
            with self.assertRaises(ValueError):unpack_vanilla(game,game/'unsafe')

    def test_unpacker_invocation_has_filter_and_external_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=self.mock_game(tmp);cache=Path(tmp)/'external_cache'
            # Fake extraction returns missing data (we cannot run Windows unpacker on Linux).
            class Dummy:
                returncode=0;stdout='';stderr=''
            with patch('vanilla_support.subprocess.run',return_value=Dummy()) as run:
                result=unpack_vanilla(game,cache)
            self.assertFalse(result['success'])
            self.assertEqual(run.call_count,6)
            args=run.call_args[0][0]
            self.assertTrue(any(s.startswith('--filter=') for s in args))
            self.assertTrue(any(str(cache) in s for s in args))

    def test_mod_override_beats_base_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            game=self.mock_game(tmp)
            (game/'data').mkdir()
            (game/'data'/'export_descr_unit.txt').write_text('base')
            mod=game/'mods'/'test_mod'/'data';mod.mkdir(parents=True)
            (mod/'export_descr_unit.txt').write_text('mod')
            found=file_capabilities(mod)
            self.assertEqual(found['origins']['edu'],'selected')
            (mod/'export_descr_unit.txt').unlink()
            found=file_capabilities(mod)
            self.assertEqual(found['origins']['edu'],'base_game')

    def test_diplomacy_math_is_explicitly_theoretical(self):
        d=money_scenario(3333333,1000000,99999999)
        self.assertEqual(d['one_turn_net'],-2333333)
        self.assertEqual(d['theoretical_total'],99999995666667)
        with self.assertRaises(ValueError):money_scenario(-1,200,3)
        with self.assertRaises(ValueError):money_scenario(0,1,100000000)

    def test_guides_bilingual_source_and_caveats(self):
        self.assertEqual(len(GUIDES),4)
        for x in GUIDES:
            self.assertTrue(x['steps'])
            self.assertTrue(all(len(z)==2 for z in x['steps']))
            self.assertEqual(len(x['limits']),2)
            self.assertEqual(len(x['name']),2)

    def test_english_must_translate_screenshot_headings(self):
        for key in ('CO OZNACZA TEN RANKING?', 'Jaką armię oferuje ten mod?',
                    'Sekrety i exploity','Wybierz swój styl wojny',
                    'Ranking jednostek','Kliknij dowolną jednostkę w tabeli, aby poznać jej mocne strony.'):
            self.assertNotEqual(tr(key,'en'),key)

    def test_english_strategy_has_english_explanation(self):
        folder=Path(__file__).parent/'examples'
        model=analyze(folder)
        self.assertIn('faction',mod_summary_en(model))
        self.assertIn('recruitability',explanation_en(model['factions'][0]).lower())

if __name__=='__main__':unittest.main()
