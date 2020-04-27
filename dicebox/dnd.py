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

def _format_attack_roll_result(to_hit, to_hit_roll, critical_miss, critical_hit,
                               weapon_damage, weapon_damage_roll, name=None):
    if critical_miss:
        result = "critical miss!"
    else:
        if critical_hit:
            hit_text = f"critical hit! ({to_hit})"
        else:
            hit_text = f"{to_hit_roll} to hit ({to_hit})"
        result = f"{hit_text}; {weapon_damage_roll} damage ({weapon_damage})"
    if name is not None:
        result = f"{name}: {result}"
    return result

def attack_roll(to_hit_bonus, weapon_damage, adv=False, disadv=False, name=None,
                criticals=True, critical_hits=None, critical_misses=None, numeric=False, n=None):
    # todo -- batching for n?
    if n is not None:
        return [attack_roll(to_hit_bonus, weapon_damage, adv, disadv, name,
                               criticals, critical_hits, critical_misses, numeric)
                  for i in range(n)]
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
        weapon_damage_roll = float('nan')
    else:
        to_hit_roll = to_hit_base + to_hit_bonus
        if to_hit_base == 20 and critical_hits:
            weapon_damage = critical_roll(weapon_damage)
        else:
            to_hit = d20 + to_hit_bonus
            to_hit_text = f"{to_hit_roll} to hit {to_hit};"
        weapon_damage_roll = weapon_damage()
    result = {
            "to_hit_roll": to_hit_roll,
            "to_hit": str(d20 + to_hit_bonus),
            "critical_miss": critical_misses and to_hit_base == 1,
            "critical_hit": critical_hits and to_hit_base == 20,
            "weapon_damage": str(weapon_damage),
            "weapon_damage_roll": weapon_damage_roll
    }
    if not numeric:
        result = _format_attack_roll_result(**result, name=name)
    return result

def attack_roll_factory(weapon_name, weapon_damage, to_hit_bonus, **kwargs):
    return partial(attack_roll, to_hit_bonus=to_hit_bonus, weapon_damage=weapon_damage, name=weapon_name, **kwargs)
