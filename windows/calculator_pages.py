# -*- coding: utf-8 -*-
"""Medieval Premium scenario calculators. No writes to campaign/game."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from tribute_calculator import tribute_scenario, variants, merchant_scenario, spaced, clipboard_plan
from diplomacy_auto import suggest_offer

BG='#0c1116';PANEL='#172129'; GOLD='#d4af72'; GOLD_BRIGHT='#f0cd91'
INK='#efeadf'; MUTED='#a3b2b8'; EMERALD='#70c7ad'; RED='#e4a39b'


def L(lang,pl,en):
    return en if lang=='en' else pl


def field(a, parent, label, var, width=20):
    col=tk.Frame(parent,bg=PANEL)
    col.pack(side='left',fill='x',expand=True,padx=(0,15),pady=(0,8))
    a.lbl(col,label,10,MUTED,bg=PANEL).pack(anchor='w',pady=(0,5))
    entry=ttk.Entry(col,textvariable=var,style='Premium.TEntry',width=width)
    entry.pack(anchor='w',fill='x')
    return entry


def page_calculators(a, root):
    lang=a.lang
    a.heading(root,L(lang,'WARSZTAT STRATEGII','STRATEGY WORKSHOP'),
              L(lang,'Kalkulatory: trybut i kupcy','Calculators: tribute and merchants'),
              L(lang,'Wpisz, ile masz pieniędzy. Kruchyx przeliczy warianty żądań i dochodów — bez udawania, że zna decyzję AI.',
                'Enter your current funds. Kruchyx computes possible demands and trade examples — without pretending to predict AI decisions.'))
    build_auto_offer(a,root)
    build_tribute_calculator(a,root)
    build_merchant_calculator(a,root)



def build_auto_offer(a, root):
    """User enters 30 000 florins, gets 10 000 gift / 4 000 demand proposal."""
    lang=a.lang
    a.section(root,L(lang,'♛  AUTOMATYCZNY DORADCA TRYBUTU','♛  AUTOMATIC TRIBUTE ASSISTANT'))
    outer,box=a.card(root,pad=20);outer.pack(fill='x',pady=(0,17))
    a.lbl(box,L(lang,'Wpisz tylko swój skarbiec — Kruchyx zaproponuje kwoty do testu.',
                'Enter only your treasury; Kruchyx suggests experimental amounts.'),
          11,INK,bg=PANEL,wraplength=930,justify='left').pack(anchor='w',pady=(0,11))
    state=getattr(a,'auto_tribute_state',None)
    if state is None:
        state={'treasury':'30000','preset':'zrownowazony','rejected':0}
        a.auto_tribute_state=state
    var=tk.StringVar(value=state['treasury'])
    entry=field(a,box,L(lang,'Skarbiec (floreny)','Treasury (florins)'),var)
    entry.master.pack_configure(fill='none',expand=False)
    modes=tk.Frame(box,bg=PANEL);modes.pack(anchor='w',pady=(3,11))
    result=a.lbl(box,'',17,GOLD_BRIGHT,'bold',PANEL,wraplength=970,justify='left')
    result.pack(anchor='w',pady=(6,12))
    caution=a.lbl(box,L(lang,
        'Heurystyka: prezent 20% / ok. 33% / 50% skarbca; żądanie 40% prezentu na turę. Brak potwierdzonego wzoru akceptacji AI.',
        'Heuristic: gift 20% / about 33% / 50% of treasury; demand 40% of gift per turn. This does not predict AI acceptance.'),
        10,RED,bg=PANEL,wraplength=970,justify='left')
    caution.pack(anchor='w',pady=(0,10))
    def calculate(*_):
        state['treasury']=var.get()
        try:
            p=suggest_offer(state['treasury'],state['preset'],state['rejected'])
            result.configure(text=L(lang,
                f'PREZENT DLA AI: {spaced(p.gift)} fl.  |  ŻĄDAJ / TURĘ: {spaced(p.demand_per_turn)} fl.\n'
                f'Zostanie: {spaced(p.reserve)} fl.  •  Zwrot: {p.break_even_payments} wpłat',
                f'GIVE AI: {spaced(p.gift)} fl.  |  DEMAND / TURN: {spaced(p.demand_per_turn)} fl.\n'
                f'Reserve: {spaced(p.reserve)} fl.  •  Break even: {p.break_even_payments} payments'),fg=GOLD_BRIGHT)
            return p
        except ValueError:
            result.configure(text=L(lang,'Podaj skarbiec 0–2 000 000 000.','Enter treasury 0–2,000,000,000.'),fg=RED)
            return None
    def switch(preset):
        state['preset']=preset;state['rejected']=0;calculate()
    for preset,label in [('ostrozny',L(lang,'Ostrożny','Conservative')),
                         ('zrownowazony',L(lang,'Zrównoważony','Balanced')),
                         ('agresywny',L(lang,'Agresywny','Aggressive'))]:
        a.btn(modes,label,lambda m=preset:switch(m),small=True,variant='dark').pack(side='left',padx=(0,8))
    actions=tk.Frame(box,bg=PANEL);actions.pack(anchor='w')
    def reject():
        state['rejected']=min(9,state['rejected']+1)
        calculate()
    def copy():
        p=calculate()
        if p is None:return
        a.clipboard_clear()
        a.clipboard_append(f'Kruchyx v0.9.6 — propozycja eksperymentalna\n'
            f'Skarbiec: {spaced(p.treasury)} fl.\nDaj AI jednorazowo: {spaced(p.gift)} fl.\n'
            f'Zażądaj od AI: {spaced(p.demand_per_turn)} fl./turę\nCzas: 99999999 tur\n'
            f'Rezerwa: {spaced(p.reserve)} fl.\nBrak gwarancji akceptacji AI.')
    a.btn(actions,L(lang,'AI odrzuciło: obniż żądanie','AI rejected: lower demand'),reject,small=True,variant='dark').pack(side='left',padx=(0,8))
    a.btn(actions,L(lang,'KOPIUJ PROPOZYCJĘ','COPY PROPOSAL'),copy,small=True,variant='gold').pack(side='left')
    var.trace_add('write',calculate)
    calculate()

def build_tribute_calculator(a,root):
    lang=a.lang
    a.section(root,L(lang,'♛  Kalkulator żądanego trybutu','♛  Tribute demand calculator'))
    outer,box=a.card(root,pad=20)
    outer.pack(fill='x',pady=(0,14))
    a.lbl(box,L(lang,'WPROWADŹ WŁASNY SKARBIEC','ENTER YOUR TREASURY'),12,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
    a.lbl(box,L(lang,'Najpierw wpisz pieniądze, które masz. Rezerwa zostanie u ciebie. Resztę kalkulator potraktuje jako planowany jednorazowy prezent dla AI.',
                 'Enter the money you have. The reserve stays in your treasury. The remaining amount becomes a planned one-time gift to AI.'),
          10,MUTED,bg=PANEL,wraplength=910,justify='left').pack(anchor='w',pady=(6,14))
    state=getattr(a,'tribute_form',None)
    if state is None:
        state={'treasury':'3333333','reserve':'0','percent':'30','turns':'99999999'}
        a.tribute_form=state
    vars={k:tk.StringVar(value=v) for k,v in state.items()}
    inp=tk.Frame(box,bg=PANEL);inp.pack(fill='x')
    field(a,inp,L(lang,'Twój skarbiec (floreny)','Your treasury (florins)'),vars['treasury'])
    field(a,inp,L(lang,'Zachowaj na własne wydatki','Keep as a reserve'),vars['reserve'])
    row=tk.Frame(box,bg=PANEL);row.pack(fill='x',pady=(0,8))
    field(a,row,L(lang,'Żądaj / wartość prezentu (%)','Demand / gift amount (%)'),vars['percent'])
    field(a,row,L(lang,'Liczba tur do próby','Duration to try (turns)'),vars['turns'])
    rrow=tk.Frame(box,bg=PANEL);rrow.pack(fill='x',pady=(0,14))
    a.lbl(rrow,L(lang,'PRZYKŁADOWE WARIANTY:','WHAT-IF PRESETS:'),10,MUTED,'bold',PANEL).pack(side='left',padx=(0,12))
    for p in (10,20,30,50):
        a.btn(rrow,f'{p}%',lambda v=p:vars['percent'].set(str(v)),
              variant='gold' if p==30 else 'dark',small=True).pack(side='left',padx=(0,7))
    a.lbl(box,L(lang,'Nie ma potwierdzonego przelicznika „tyle mam → tyle AI zapłaci”. Procenty to TWOJE ustawienia scenariusza, a nie szansa akceptacji.',
                'No proven formula converts your treasury into an amount the AI will accept. These percentages are YOUR scenarios, not acceptance probabilities.'),
          10,RED,bg=PANEL,wraplength=900,justify='left').pack(anchor='w',pady=(0,16))

    stats=tk.Frame(box,bg=PANEL);stats.pack(fill='x')
    cards=[]
    for idx,label in enumerate([
        L(lang,'PREZENT DLA AI','GIFT TO AI'),
        L(lang,'ŻĄDANY TRYBUT / TURA','DEMANDED / TURN'),
        L(lang,'ZWROT PREZENTU','GIFT BREAK-EVEN')]):
        co=tk.Frame(stats,bg='#26323a',padx=15,pady=11,highlightbackground='#465151',highlightthickness=1)
        co.pack(side='left',fill='both',expand=True,padx=(0 if idx==0 else 5,5))
        a.lbl(co,label,9,MUTED,'bold','#26323a').pack(anchor='w')
        val=a.lbl(co,'—',18,GOLD_BRIGHT,'bold','#26323a')
        val.pack(anchor='w',pady=(7,0));cards.append(val)
    caption=a.lbl(box,'',11,INK,bg=PANEL,wraplength=970,justify='left')
    caption.pack(anchor='w',pady=(18,8))
    scenarios=a.lbl(box,'',10,MUTED,bg=PANEL,wraplength=970,justify='left')
    scenarios.pack(anchor='w',pady=(0,10))
    feedback=a.lbl(box,'',10,EMERALD,bg=PANEL,wraplength=890,justify='left')
    feedback.pack(anchor='w',pady=(7,3))
    current={'plan':None}
    def calc(*_):
        state.update({k:v.get() for k,v in vars.items()})
        try:
            plan=tribute_scenario(vars['treasury'].get(),vars['reserve'].get(),
                                   vars['percent'].get(),vars['turns'].get())
            current['plan']=plan
            cards[0].configure(text=spaced(plan.gift),fg=GOLD_BRIGHT)
            cards[1].configure(text=spaced(plan.per_turn),fg=EMERALD)
            cards[2].configure(text=L(lang,f'{plan.break_even_payments} wpłat' if plan.break_even_payments else 'Brak wpłat',
                                           f'{plan.break_even_payments} payments' if plan.break_even_payments else 'No payments'),fg=GOLD_BRIGHT)
            caption.configure(text=(
                L(lang,'Gdyby AI faktycznie zapłaciła jeden raz: ', 'If AI actually paid once: ')
                +spaced(plan.after_one_payment)+L(lang,' fl. (bilans prezentu i otrzymanego trybutu).\n',
                                                     ' florins (gift minus/plus tribute).\n')
                +L(lang,'Po 5 rzeczywistych wpłatach: ', 'After 5 actual payments: ')
                +spaced(plan.after_five_payments)+L(lang,' fl.\nDługi okres jest ustawieniem exploitu, NIE obietnicą miliona wpłat.',
                                                       ' florins.\nThe long duration is an exploit test setting, NOT a promise of millions of payments.')
                ),fg=INK)
            try:
                examples=variants(plan.treasury,plan.reserve)
                scenarios.configure(text=L(lang,'Dla tej samej kwoty prezentu: ','For the same gift amount: ')+
                                         '    ·    '.join(f'{v.rate_percent}% → {spaced(v.per_turn)}' for v in examples),fg=MUTED)
            except ValueError:scenarios.configure(text='')
        except ValueError:
            current['plan']=None
            for c in cards:c.configure(text='—',fg=RED)
            caption.configure(text=L(lang,'Sprawdź kwoty: użyj liczb całkowitych 0–2 147 483 647; rezerwa nie może przekroczyć skarbca. Procent 1–200, liczba tur 1–99 999 999.',
                                        'Check entries: integer money 0–2,147,483,647; reserve cannot exceed treasury. Ratio 1–200%, duration 1–99,999,999.'),fg=RED)
            scenarios.configure(text='')
    for var in vars.values():var.trace_add('write',calc)
    def copy_plan():
        p=current['plan']
        if p is None:
            feedback.configure(text=L(lang,'Popraw dane przed kopiowaniem.','Correct the values before copying.'),fg=RED)
            return
        a.clipboard_clear();a.clipboard_append(clipboard_plan(p,lang))
        feedback.configure(text=L(lang,'Skopiowano plan! Wklej go do notatnika — niczego nie wysłano do gry.',
                                        'Plan copied! Paste into a note — nothing was sent to the game.'),fg=EMERALD)
    a.btn(box,L(lang,'KOPIUJ PLAN TRYBUTU','COPY TRIBUTE PLAN'),copy_plan,variant='gold').pack(anchor='w',pady=(7,12))
    a.lbl(box,L(lang,'PAMIĘTAJ: w negocjacjach wybierz trybut PŁACONY PRZEZ AI, nie przez ciebie. Osobno sprawdź oceny oferty i faktyczny przelew po turze. Zrób wcześniej zapis kampanii.',
                'REMEMBER: demand payment FROM the AI, not from yourself. Check offer evaluation and the actual treasury change after a turn. Make a separate save first.'),
          10,RED,bg=PANEL,wraplength=930,justify='left').pack(anchor='w')
    calc()


def build_merchant_calculator(a,root):
    lang=a.lang
    a.section(root,L(lang,'♞  Kalkulator kupców i zasobów','♞  Merchant trade calculator'))
    outer,box=a.card(root,pad=20)
    outer.pack(fill='x',pady=(0,14))
    a.lbl(box,L(lang,'DOCHÓD Z KUPCÓW — PORÓWNANIE WARIANTÓW','MERCHANT INCOME — WHAT-IF COMPARISON'),12,GOLD_BRIGHT,'bold',PANEL).pack(anchor='w')
    a.lbl(box,L(lang,'Sprawdź W GRZE rzeczywisty dochód jednego kupca na konkretnym zasobie, a następnie wpisz go tutaj. Nie zakładamy, że pozostali kupcy zarobią tyle samo.',
                 'Look up the actual income of ONE merchant on a specific resource IN GAME, then enter it here. We do not assume additional merchants earn the same.'),
          10,MUTED,bg=PANEL,wraplength=910,justify='left').pack(anchor='w',pady=(7,13))
    state=getattr(a,'merchant_form',None)
    if state is None:
        state={'income':'500','count':'5','efficiency':'70'}
        a.merchant_form=state
    vars={k:tk.StringVar(value=v) for k,v in state.items()}
    inputs=tk.Frame(box,bg=PANEL);inputs.pack(fill='x')
    field(a,inputs,L(lang,'Dochód jednego kupca / turę','Observed income per merchant / turn'),vars['income'])
    field(a,inputs,L(lang,'Liczba kupców','Number of merchants'),vars['count'])
    field(a,inputs,L(lang,'Przyjęta średnia efektywność (%)','Assumed average efficiency (%)'),vars['efficiency'])
    result=a.lbl(box,'',13,GOLD_BRIGHT,'bold',PANEL,wraplength=910,justify='left')
    result.pack(anchor='w',pady=(14,9))
    a.lbl(box,L(lang,'Przykładowa efektywność służy jedynie do planowania. Silnik Medieval II może inaczej liczyć wielu kupców, ich umiejętności i odległość surowca.',
                'Efficiency is only an illustrative assumption. Medieval II may calculate multiple merchants differently based on skills, distance and engine rules.'),
          10,RED,bg=PANEL,wraplength=940,justify='left').pack(anchor='w')
    def calc(*_):
        state.update({k:v.get() for k,v in vars.items()})
        try:
            m=merchant_scenario(vars['income'].get(),vars['count'].get(),vars['efficiency'].get())
            result.configure(text=(L(lang,'Proste pomnożenie (górny wariant): ','Simple multiplication (upper scenario): ')+
                                   spaced(m.simple_upper_bound)+L(lang,' fl. / turę\nPrzykład ze wskazaną efektywnością: ',
                                                                 ' florins / turn\nIllustrative adjusted scenario: ')+
                                   spaced(m.illustrative_income)+L(lang,' fl. / turę', ' florins / turn')),fg=GOLD_BRIGHT)
        except ValueError:
            result.configure(text=L(lang,'Podaj nieujemny dochód, 1–40 kupców i efektywność 0–100%.',
                                            'Enter non-negative income, 1–40 merchants and efficiency 0–100%.'),fg=RED)
    for var in vars.values():var.trace_add('write',calc)
    calc()
