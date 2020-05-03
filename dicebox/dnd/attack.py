from functools import partial

import numpy as np

from ..core import Dice, DiceExpr

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
                criticals=True, critical_hits=None, critical_misses=None, numeric=False, repeat=None):
    import pandas as pd
    n = 1 if repeat is None else repeat
    d20 = Dice(20)
    if adv:
        d20 = d20.adv
    if disadv:
        d20 = d20.disadv
    critical_misses = criticals if critical_misses is None else critical_misses
    critical_hits = criticals if critical_hits is None else critical_hits

    to_hit_base = d20(n)
    critical_miss = (to_hit_base == 1) & critical_misses
    critical_hit = (to_hit_base == 20) & critical_hits
    normal_roll = ~critical_miss & ~critical_hit
    to_hit_roll = to_hit_base + to_hit_bonus
    weapon_damage_roll = np.zeros(n, dtype=int)
    if normal_roll.any():
        weapon_damage_roll[normal_roll] = weapon_damage(normal_roll.sum())
    if critical_hit.any():
        critical_damage = critical_roll(weapon_damage)
        weapon_damage_roll[critical_hit] = critical_damage(critical_hit.sum())
    result = pd.DataFrame({
        "critical_miss": critical_miss,
        "critical_hit": critical_hit,
        "to_hit": str(d20 + to_hit_bonus),
        "to_hit_roll": to_hit_roll,
        "weapon_damage_roll": weapon_damage_roll,
        "weapon_damage": str(weapon_damage)
    })
    result.loc[result["critical_miss"], "weapon_damage"] = "0"
    if critical_hit.any():
        result.loc[result["critical_hit"], "weapon_damage"] = str(critical_damage)
    if not numeric:
        result = [_format_attack_roll_result(**row.to_dict(), name=name)
                  for _, row in result.iterrows()]
    if repeat is None:
        result = result[0]
    return result

def attack_roll_factory(weapon_name, weapon_damage, to_hit_bonus, **kwargs):
    return partial(attack_roll, to_hit_bonus=to_hit_bonus, weapon_damage=weapon_damage, name=weapon_name, **kwargs)
