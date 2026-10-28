# -*- coding: utf-8 -*-
"""Transparent, strictly arithmetic worksheets for Medieval II diplomacy/trade.

No payout/AI acceptance algorithm is known. Preset percentages are user-selected
what-if cases, not estimates of accepted tribute. Zero process interaction.
"""
from __future__ import annotations
from dataclasses import dataclass

MAX_CASH = 2_147_483_647
MAX_DURATION = 99_999_999


def amount(value):
    """Parse nonnegative integer florins; support usual formatted thousand groups."""
    if isinstance(value, bool):
        raise ValueError('Invalid money amount')
    if isinstance(value, int):
        number = value
    else:
        s = str(value).strip().replace('\u00a0', ' ').replace('\u202f', ' ')
        # Allow separators only in correctly grouped thousands or regular digits.
        if not s:
            raise ValueError('Empty money amount')
        if not s.isdecimal():
            import re
            if not re.fullmatch(r'\d{1,3}(?:[ ,.\u00a0\u202f]\d{3})+', s):
                raise ValueError('Enter whole florins, e.g. 3333333 or 3 333 333')
            s = s.replace(' ', '').replace(',', '').replace('.', '')
        number = int(s)
    if not 0 <= number <= MAX_CASH:
        raise ValueError('Amount must be 0 to 2,147,483,647')
    return number


def natural(value, *, low, high):
    s = str(value).strip()
    if not s.isdecimal():
        raise ValueError('Expected positive integer')
    number = int(s)
    if not low <= number <= high:
        raise ValueError(f'Value outside [{low},{high}]')
    return number


def spaced(value):
    return f'{value:,}'.replace(',', ' ')


@dataclass(frozen=True)
class TributeScenario:
    treasury: int
    reserve: int
    gift: int
    rate_percent: int
    per_turn: int
    turns: int
    initial_net: int
    after_one_payment: int
    after_five_payments: int
    break_even_payments: int | None
    full_duration_hypothetical: int


def tribute_scenario(treasury, reserve=0, rate_percent=30, turns=99_999_999):
    cash = amount(treasury)
    kept = amount(reserve)
    percent = natural(rate_percent, low=1, high=200)
    period = natural(turns, low=1, high=MAX_DURATION)
    if kept > cash:
        raise ValueError('Reserve cannot exceed treasury')
    gift = cash - kept
    if gift <= 0:
        raise ValueError('Gift must be positive; leave less in reserve')
    # Nearest florin, positive integer amounts: half-up, rather than bankers rounding.
    per_turn = (gift * percent + 50) // 100
    if per_turn > MAX_CASH:
        raise ValueError('Demand exceeds supported cash limit')
    breakeven = (gift + per_turn - 1)//per_turn if per_turn > 0 else None
    return TributeScenario(cash, kept, gift, percent, per_turn, period,
                           -gift, per_turn - gift, 5 * per_turn - gift,
                           breakeven, period * per_turn - gift)


def variants(treasury, reserve=0, rates=(10, 20, 30, 50)):
    return [tribute_scenario(treasury, reserve, r) for r in rates]


@dataclass(frozen=True)
class MerchantScenario:
    observed_per_merchant: int
    merchants: int
    efficiency_percent: int
    simple_upper_bound: int
    illustrative_income: int


def merchant_scenario(observed_per_merchant, merchants, efficiency_percent=100):
    actual = amount(observed_per_merchant)
    count = natural(merchants, low=1, high=40)
    efficiency = natural(efficiency_percent, low=0, high=100)
    # This is only a planning scenario. No assumption about game engine or diminishing returns.
    upper = actual * count
    return MerchantScenario(actual, count, efficiency, upper,
                            (upper * efficiency + 50)//100)


def clipboard_plan(s: TributeScenario, lang='pl'):
    if lang == 'en':
        return (f'KRUCHYX — TRIBUTE WHAT-IF WORKSHEET\n'
                f'Treasury: {spaced(s.treasury)} florins\n'
                f'Keep in reserve: {spaced(s.reserve)}\n'
                f'One-time gift to AI: {spaced(s.gift)}\n'
                f'Tribute to DEMAND from AI: {spaced(s.per_turn)} per turn\n'
                f'Duration to try: {spaced(s.turns)} turns\n'
                f'Illustrative ratio: {s.rate_percent}% of the gift\n'
                f'If payments actually arrive, break-even: {s.break_even_payments or "N/A"} payments\n'
                'WARNING: this is arithmetic only; the game may reject, cap or never pay.')
    return (f'KRUCHYX — KALKULATOR TRYBUTU (SYMULACJA)\n'
            f'Skarbiec: {spaced(s.treasury)} florenów\n'
            f'Zostaw w rezerwie: {spaced(s.reserve)}\n'
            f'Jednorazowy PREZENT dla AI: {spaced(s.gift)}\n'
            f'Trybut ŻĄDANY OD AI: {spaced(s.per_turn)} na turę\n'
            f'Liczba tur do przetestowania: {spaced(s.turns)}\n'
            f'Umowny współczynnik żądania: {s.rate_percent}% wartości prezentu\n'
            f'Zwrot kosztu (gdyby AI płaciła): {s.break_even_payments or "brak"} wpłat\n'
            'UWAGA: to tylko arytmetyka; AI może odmówić, ograniczyć kwotę lub nie zapłacić.')
