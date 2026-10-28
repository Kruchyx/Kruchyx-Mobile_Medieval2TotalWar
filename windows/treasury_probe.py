"""Experimental strictly read-only treasury detection for three validated KIRSI England save variants.
Never guess offsets in arbitrary saves, and never write to SAV files.
"""
from pathlib import Path
import hashlib
import struct

# Structural marker verified in user's three England saves, not a universal save-file format.
AFTER_TREASURY = bytes.fromhex('c4090000d7380000640000002e1e1600')
KNOWN_VALUES = {10000, 20000, 25000}

def probe_treasury(path):
    path = Path(path)
    data = path.read_bytes()
    matches = []
    pos = 0
    while True:
        i = data.find(AFTER_TREASURY, pos)
        if i < 0: break
        if i >= 4:
            value = struct.unpack_from('<i', data, i-4)[0]
            if 0 <= value <= 2_147_483_647:
                matches.append((i - 4, value))
        pos = i + 1
    if len(matches) != 1:
        return {'status':'unavailable', 'value':None, 'reason': 'Nie znaleziono jednoznacznego wzorca dla skarbca tej kampanii.'}
    offset, value = matches[0]
    # Only trust validated local layout, amount and surrounding marker. Other campaigns must remain unknown.
    if offset != 1449502 or value not in KNOWN_VALUES:
        return {'status':'unavailable', 'value':None, 'reason':'Wzorzec podobny, ale zapis nie jest zgodny z trzema przebadanymi próbkami.'}
    return {'status':'experimental', 'value': value, 'offset':offset, 'reason':'Dopasowanie do struktury trzech testowych zapisów Anglii KIRSI (10 000 / 20 000 / 25 000). Niepotwierdzone dla innych kampanii.'}
