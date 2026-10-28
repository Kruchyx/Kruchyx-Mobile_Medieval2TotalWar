# -*- coding: utf-8 -*-
"""Heuristic AI tribute offer planner for Medieval II (not an AI acceptance predictor)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Offer:
    treasury: int
    gift: int
    demand_per_turn: int
    reserve: int
    break_even_payments: int
    preset: str
    adjustment: int

PRESETS={'ostrozny':0.20,'zrownowazony':1/3,'agresywny':0.50}

def suggest_offer(treasury: int | str,preset='zrownowazony',adjustment=0) -> Offer:
    """Take 20%, 1/3 or 50% of treasury and ask 40% of gift per turn.

    All arithmetic is deterministic, not a claim about game's hidden AI logic.
    Lower quote by 10% of baseline per rejected attempt, to a 10% floor.
    """
    try: amount=int(str(treasury).replace(' ', '').strip())
    except (ValueError,TypeError): raise ValueError('Podaj liczbę całkowitą.') from None
    if not 0<=amount<=2_000_000_000: raise ValueError('Skarbiec musi mieścić się w granicach 0–2 000 000 000.')
    if preset not in PRESETS:raise ValueError('Nieznany wariant.')
    if type(adjustment) is not int or not 0<=adjustment<=9:raise ValueError('Nieprawidłowa liczba odrzuceń.')
    gift=int(amount*PRESETS[preset]//100)*100
    initial=int(gift*0.40//100)*100
    demand=(initial*(10-adjustment)//10//100)*100
    reserve=amount-gift
    return Offer(amount,gift,demand,reserve,(gift+demand-1)//demand if demand else 0,preset,adjustment)

if __name__=='__main__':
    print(suggest_offer(30000))
