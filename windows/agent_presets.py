"""Validated conservative agent trait presets for Medieval II console."""
from trainer_core import Plan, CommandError, name

# Explicit values drawn from documented vanilla traits, conservative curated combinations.
PRESETS = {
 'general': ('Generał — MAX dowodzenie', [('GoodCommander',5),('GoodAttacker',5),('GoodDefender',5),('Loyal',4),('HighPersonalSecurity',3)]),
 'priest': ('Kapłan — MAX pobożność', [('StrongFaith',4),('PublicFaith',4),('NaturalPriestSkill',3),('Righteous',3)]),
 'merchant': ('Kupiec — MAX handel', [('GoodMerchant',4),('NaturalMerchantSkill',3),('WorldlyMerchant',2),('SecureMerchant',2),('LegalDealer',2)]),
 'spy': ('Szpieg — MAX szpiegostwo', [('GoodSpy',5),('NaturalSpySkill',3),('GoodConspirator',3)]),
 'assassin': ('Zabójca — MAX skuteczność', [('GoodAssassin',5),('GoodSaboteur',3),('NaturalAssassinSkill',3)]),
 'diplomat': ('Dyplomata — MAX wpływy', [('GoodDiplomat',5),('NaturalDiplomatSkill',3),('Multilingual',3),('SmoothTalker',3)]),
 'princess': ('Księżniczka — MAX dyplomacja', [('GoodPrincess',4),('NaturalPrincess',3),('PrettyWoman',3),('EducatedWoman',3),('BraveWoman',3)]),
}

def agent_plan(agent, character, selected=True):
    if agent not in PRESETS:raise CommandError('Nieznany typ postaci.')
    label, traits=PRESETS[agent]
    target='this' if selected else name(character,'Postać')
    commands=tuple(f'give_trait {target} {trait} {level}' for trait,level in traits)
    return Plan(label,commands,'Zaznacz właściwą postać w grze (przy this). Zestaw jest oparty na cechach vanilla. KIRSI/M2EX może mieć inne ograniczenia, konflikty cech lub limity. Nie jest to gwarancja maksymalnych statystyk ani automatyczna edycja gry.')
