import unittest
from pathlib import Path
from modstudio import read_text, money_options, faction_field_options, edit_money, edit_faction_field, settlement_options

class KIRSIRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = Path(__file__).parent / 'fixtures' / 'kirsi_descr_strat.txt'
        cls.text, cls.encoding=read_text(cls.fixture)

    def test_factions(self):
        entries=money_options(self.text)
        assert len(entries)==22, entries
        assert ('england',10000) in entries
    def test_purse(self):
        purse=dict(faction_field_options(self.text,'denari_kings_purse'))
        assert purse['england']==2500
    def test_edit_money(self):
        updated=edit_money(self.text,'england',123456)
        assert ('england',123456) in money_options(updated)
        assert updated!=self.text
    def test_edit_purse(self):
        updated=edit_faction_field(self.text,'england','denari_kings_purse',54321)
        assert dict(faction_field_options(updated,'denari_kings_purse'))['england']==54321
    def test_preserve_crlf(self):
        updated=edit_money(self.text,'england',123456)
        assert updated.count('\r\n')==self.text.count('\r\n')
    def test_regions(self):
        assert ('London_Region',3800) in [(x[0],x[1]) for x in settlement_options(self.text)]
if __name__=='__main__': unittest.main()
