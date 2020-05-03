def avg_attack_vs_ac(sim, AC):
    hit = ((sim["to_hit_roll"] > AC) | sim["critical_hit"]) & ~ sim["critical_miss"]
    return (hit * sim["weapon_damage_roll"]).mean()

def battlesim(team1, team2):
    teams = (team1, team2)
    # step 1 -- sim out the weapon attacks, store for later
    attack_sims = {
        attack: attack(numeric=True, repeat=10000)
        for team in teams for char in team.values() for attack in char["attacks"].values()
    }
    # step 2 -- greedy DPS strat: calculate damage/hp for each char on opponent team (vs lowest AC on own team)
    # team1 goes first
    active_team = team1
    other_team = team2
    step = 0
    while any(char["HP"] > 0 for char in team1.values()) and any(char["HP"] > 0 for char in team2.values()):
        min_ac = min(char["AC"] for char in active_team.values())
        other_dphp = {}
        for name, char in other_team.items():
            if char["HP"] <= 0:
                continue
            max_avg_attack_vs_ac = max(
                avg_attack_vs_ac(attack_sims[attack], min_ac)
                for attack in char["attacks"].values()
            )
            other_dphp[name] = max_avg_attack_vs_ac / char["HP"]
        for name, char in active_team.items():
            if char["HP"] <= 0:
                continue
            target = None
            chosen_attack = None
            objective = float("-inf")
            for other_name, other_char in other_team.items():
                if other_char["HP"] <= 0:
                    continue
                avg_dmg = {
                    attack_name: avg_attack_vs_ac(attack_sims[attack], other_char["AC"])
                    for attack_name, attack in char["attacks"].items()
                }
                best_dmg = max(avg_dmg.values())
                plan_objective = other_dphp[other_name] * min(other_char["HP"], best_dmg)
                if plan_objective > objective:
                    target = other_name
                    objective = plan_objective
                    chosen_attack = [attack_name for attack_name, dmg in avg_dmg.items() if dmg >= best_dmg][0]
            if target is None:
                continue
            targeting_info = f"{name} attacks {target} with {chosen_attack}"
            target_char = other_team[target]
            calc_attack = char["attacks"][chosen_attack](numeric=True, repeat=1).iloc[0]
            if calc_attack["to_hit_roll"] <= target_char["AC"]:
                attack_info = f"attack misses! ({calc_attack['to_hit_roll']} vs {target_char['AC']})"
                damage_info = "no damage"
                damage = 0
            else:
                if calc_attack["critical_hit"]:
                    attack_info = "CRITICL HIT!"
                else:
                    attack_info = "attack hits!"
                attack_info += f" ({calc_attack['to_hit_roll']} vs {target_char['AC']})"
                damage = calc_attack['weapon_damage_roll']
                new_hp = target_char["HP"] - damage
                damage_info = f"{calc_attack['weapon_damage_roll']} damage ({target_char['HP']} -> {new_hp})"
                target_char["HP"] = new_hp
            print(targeting_info)
            print(attack_info)
            print(damage_info)
            print()
        active_team, other_team = other_team, active_team
        step += 1
    return team1, team2
