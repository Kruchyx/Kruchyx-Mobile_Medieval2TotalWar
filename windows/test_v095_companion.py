import json
import tempfile
import unittest
from pathlib import Path
from empire_companion import knowledge,read_event_ranges,derived_events,companion_report
from mod_insights import analyze

class CompanionTests(unittest.TestCase):
    def test_shared_data_schema(self):
        data=knowledge()
        self.assertEqual(data['version'],'0.9.5')
        self.assertGreaterEqual(len(data['exploits']),8)
        self.assertTrue(all(x['title'] and x['steps'] for x in data['exploits']))

    def test_event_offsets_and_comments(self):
        parsed=read_event_ranges('; event historic ignored\n; date 1 3\nevent historic mongols_invasion_warn\n date 128 144\nevent historic gunpowder_discovered\n date 210 220 ; comment')
        self.assertEqual(parsed['mongols_invasion_warn'],(128,144))
        self.assertEqual(parsed['gunpowder_discovered'],(210,220))
        self.assertNotIn('ignored',parsed)

    def test_event_from_custom_mod(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'data/world/maps/campaign/imperial_campaign'
            p.mkdir(parents=True)
            (p/'descr_events.txt').write_text('event historic mongols_invasion_warn\ndate 50 70\n',encoding='utf-8')
            events,source,found=derived_events(tmp)
            self.assertTrue(found)
            target=next(x for x in events if x['id']=='mongols_invasion_warn')
            self.assertEqual((target['turn_from'],target['turn_to']),(25,35))
            self.assertEqual(target['confidence'],'file')
            self.assertTrue(source.endswith('descr_events.txt'))
            self.assertEqual(next(x for x in events if x['id']=='gunpowder_discovered')['confidence'],'not_found')

    def test_report_demo_serializable(self):
        model=analyze(Path(__file__).parent/'examples')
        payload=companion_report(model,'DEMO')
        self.assertEqual(payload['schema'],'kruchyx-companion-v1')
        self.assertGreater(len(payload['units']),300)
        json.dumps(payload,ensure_ascii=False)
        self.assertTrue(all('owners' in u for u in payload['units']))

if __name__=='__main__':unittest.main()
