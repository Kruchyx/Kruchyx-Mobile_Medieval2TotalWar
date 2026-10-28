"""Safe, offline Medieval II console command planning (no game process access)."""
import re
from dataclasses import dataclass
from pathlib import Path

MAX_CASH = 40000
MAX_COMMANDS = 500

class CommandError(ValueError):
    pass

@dataclass(frozen=True)
class Plan:
    label: str
    commands: tuple
    caveat: str
    def as_text(self):
        return '\n'.join(self.commands)


def positive(value, name, maximum=None, minimum=1):
    try: n=int(str(value).strip())
    except (TypeError, ValueError): raise CommandError(f'{name}: wpisz liczbę całkowitą.')
    if n < minimum or (maximum is not None and n > maximum):
        raise CommandError(f'{name}: dozwolony zakres {minimum}–{maximum if maximum is not None else "bez górnego limitu"}.')
    return n


def name(value, label='Nazwa'):
    text = str(value).strip()
    if not text or len(text)>100 or any(c in text for c in '\r\n\x00";\\'):
        raise CommandError(f'{label}: podaj poprawną nazwę bez znaków sterujących i cudzysłowu.')
    return f'"{text}"'


def identifier(value, label):
    text=str(value).strip()
    if not re.fullmatch(r'[a-zA-Z][a-zA-Z_0-9]*',text):
        raise CommandError(f'{label}: dozwolone są litery, cyfry i podkreślniki.')
    return text


def money(amount):
    total=positive(amount,'Pieniądze', MAX_CASH*MAX_COMMANDS)
    chunks=[MAX_CASH]*(total//MAX_CASH)
    if total%MAX_CASH: chunks.append(total%MAX_CASH)
    return Plan('Dodaj pieniądze',tuple(f'add_money {x}' for x in chunks),
                'Gra standardowo ogranicza pojedynczą komendę do 40 000. Wklej/wykonaj każdą linię osobno w konsoli gry; to nie jest automatyczna aplikacja do pamięci procesu.')


def unit(target,unit_name,count,experience,armor,weapon):
    q_target=name(target,'Miasto/generał')
    q_unit=name(unit_name,'Identyfikator jednostki')
    count=positive(count,'Oddziały',5)
    exp=positive(experience,'Doświadczenie',9,0)
    armor=positive(armor,'Pancerz',3,0)
    weapon=positive(weapon,'Broń',3,0)
    return Plan('Dodaj jednostki',(f'create_unit {q_target} {q_unit} {count} {exp} {armor} {weapon}',),
                'Dokładne ID jednostki musi istnieć w modzie. Gra może odmówić, jeśli armia jest pełna lub jednostka jest niedostępna.')


def building(city):
    return Plan('Natychmiastowa budowa',(f'process_cq {name(city,"Miasto")}',),
                'Budynek musi znajdować się w kolejce budowy. Możliwe jest naliczenie normalnego kosztu.')


def population(city,amount):
    n=positive(amount,'Ludność',1000000)
    return Plan('Dodaj ludność',(f'add_population {name(city,"Miasto")} {n}',),
                'Zmiana populacji może mieć skutki dla porządku publicznego i poziomu osady.')


def movement(character):
    return Plan('Odnów ruch',(f'character_reset {name(character,"Postać")}',),
                'Działanie zależy od sytuacji jednostki w turze; gra może odmówić.')


def teleport(character,x,y):
    x=positive(x,'X',10000,0); y=positive(y,'Y',10000,0)
    return Plan('Przesuń postać',(f'move_character {name(character,"Postać")} {x} {y}',),
                'Sprawdź współrzędne poleceniem show_cursorstat. Nie wszystkie pola mapy są poprawnymi miejscami docelowymi.')


def trait(character,trait_id,level):
    return Plan('Nadaj cechę',(f'give_trait {name(character,"Postać")} {identifier(trait_id,"ID cechy")} {positive(level,"Poziom",10)}',),
                'ID cechy i maksymalny poziom są zależne od moda. Sprawdź export_descr_character_traits.txt.')


def quick(action):
    options={
        'fog':('Odkryj/ukryj mapę','toggle_fow','Przełącza mgłę wojny.'),
        'coords':('Współrzędne kursora','show_cursorstat','Wynik pokazuje konsola gry.'),
        'win_attack':('Wygrana atakującego','auto_win attacker','Wykonaj w odpowiednim momencie przed automatycznym rozstrzygnięciem bitwy.'),
        'win_defend':('Wygrana obrońcy','auto_win defender','Wykonaj w odpowiednim momencie przed automatycznym rozstrzygnięciem bitwy.'),
    }
    if action not in options: raise CommandError('Nieznany skrót.')
    label,command,caveat=options[action]
    return Plan(label,(command,),caveat)


def export_plan(destination,plan):
    """Export cheats as text only; never edit game files or SAV."""
    dest=Path(destination)
    if dest.suffix.lower()!='.txt': raise CommandError('Eksport wymaga pliku .txt.')
    dest.write_text('# Kruchyx Medieval Mod Studios v0.9.1 — komendy do ręcznego uruchomienia\n'
                    '# '+plan.caveat+'\n'+plan.as_text()+'\n',encoding='utf-8')
    return dest
