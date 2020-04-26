from functools import partial

from .core import Dice, DiceExpr

def critical_roll(initial_roll):
    if initial_roll is None:
        return
    if isinstance(initial_roll, (int, float)):
        return initial_roll
    try:
        sides = initial_roll.dice_sides
    except AttributeError:
        return DiceExpr(op=initial_roll.op, left=critical_roll(initial_roll.left), right=critical_roll(initial_roll.right))
    else:
        return Dice({sides: n*2 for sides, n in sides.items()}, agg=initial_roll.agg)

def attack_roll(to_hit_bonus, weapon_damage, adv=False, disadv=False, name=None,
                criticals=True, critical_hits=None, critical_misses=None, numeric=False):
    d20 = Dice(20)
    if adv:
        d20 = d20.adv
    if disadv:
        d20 = d20.disadv
    to_hit_base = d20()
    critical_misses = criticals if critical_misses is None else critical_misses
    critical_hits = criticals if critical_hits is None else critical_hits
    if to_hit_base == 1 and critical_misses:
        to_hit_roll = to_hit_base
        result = "critical miss"
    else:
        if to_hit_base == 20 and critical_hits:
            to_hit_text = "critical hit!"
            weapon_damage = critical_roll(weapon_damage)
        else:
            to_hit_roll = to_hit_base + to_hit_bonus
            to_hit = d20 + to_hit_bonus
            to_hit_text = f"{to_hit_roll} to hit {to_hit};"
        result = f"{to_hit_text} {weapon_damage()} damage {weapon_damage}"
    if name:
        result = f"{name}: {result}"
    if numeric:
        # todo
        return tuple()
    return result

def attack_roll_factory(weapon_name, weapon_damage, to_hit_bonus, **kwargs):
    return partial(attack_roll, to_hit_bonus=to_hit_bonus, weapon_damage=weapon_damage, name=weapon_name, **kwargs)
