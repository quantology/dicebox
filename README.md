<img src="https://raw.githubusercontent.com/quantology/dicebox/master/diceset.svg" width="200" height="200">

# dicebox
A simple dsl for dice.


```python
>>> import pandas as pd
>>> from dicebox import d
```


```
>>> d(100) + 5
<DiceExpr(1d100 + 5)>
```



```python
>>> str(d(6) + d(6)) == str(d({6: 2})) == str(d(6, 6)) == "(2d6)"
True
```



```
>>> d(8, 6, 6, 6) // 2
<DiceExpr((1d8 + 3d6) // 2)>
```



```
>>> d({8: 1, 6: 3})
<Dice(1d8 + 3d6)>
```



```
>>> d(10) + 5 + (d(20) + d(8))
<DiceExpr(1d10 + 5 + 1d8 + 1d20)>
```




```python
>>> d(20).adv.roll(2)
array([17, 17])
```




```python
>>> n = 100000
>>> adv = (pd.Series(d(20).adv.roll(n)).value_counts().sort_index() / n)
>>> disadv = (pd.Series(d(20).disadv.roll(n)).value_counts().sort_index() / n)
>>> norm = (pd.Series(d(20).roll(n)).value_counts().sort_index() / n)
```





```
>>> (d(20).adv - d(20).disadv) * 2
<DiceExpr((adv(1d20) - disadv(1d20)) * 2)>
```



**todo:**
 - [ ] pdist (incl composability)
 - [ ] roll logging
 - [ ] better expr collapse (sympy?)
 - [ ] better DiceExpr str rendering
 - [ ] DiceExpr.parse
 - [ ] visual output (w/ scavegr)

---


```python
>>> from dicebox.dnd import attack_roll_factory, critical_roll
>>> rapier_attack = attack_roll_factory("Rapier", d(8) + 4, 3)
>>> rapier_sneak_attack = attack_roll_factory("Rapier", d(8, 6, 6, 6) + 4, 3)
>>> rapier_assassinate_attack = attack_roll_factory("Rapier", critical_roll(d(8, 6, 6, 6) + 4), 3, critical_hits=False)
```


```
>>> for i in range(20):
>>>    print(rapier_assassinate_attack(adv=True))
Rapier: 17 to hit (adv(1d20) + 3); 39 damage (2d8 + 6d6 + 4)
Rapier: 17 to hit (adv(1d20) + 3); 36 damage (2d8 + 6d6 + 4)
Rapier: 12 to hit (adv(1d20) + 3); 25 damage (2d8 + 6d6 + 4)
Rapier: 21 to hit (adv(1d20) + 3); 37 damage (2d8 + 6d6 + 4)
Rapier: 10 to hit (adv(1d20) + 3); 32 damage (2d8 + 6d6 + 4)
Rapier: 22 to hit (adv(1d20) + 3); 36 damage (2d8 + 6d6 + 4)
Rapier: 17 to hit (adv(1d20) + 3); 37 damage (2d8 + 6d6 + 4)
Rapier: 14 to hit (adv(1d20) + 3); 29 damage (2d8 + 6d6 + 4)
Rapier: 10 to hit (adv(1d20) + 3); 39 damage (2d8 + 6d6 + 4)
Rapier: 15 to hit (adv(1d20) + 3); 37 damage (2d8 + 6d6 + 4)
Rapier: 23 to hit (adv(1d20) + 3); 27 damage (2d8 + 6d6 + 4)
Rapier: 8 to hit (adv(1d20) + 3); 36 damage (2d8 + 6d6 + 4)
Rapier: 15 to hit (adv(1d20) + 3); 31 damage (2d8 + 6d6 + 4)
Rapier: 20 to hit (adv(1d20) + 3); 38 damage (2d8 + 6d6 + 4)
Rapier: 12 to hit (adv(1d20) + 3); 34 damage (2d8 + 6d6 + 4)
Rapier: 15 to hit (adv(1d20) + 3); 31 damage (2d8 + 6d6 + 4)
Rapier: 18 to hit (adv(1d20) + 3); 35 damage (2d8 + 6d6 + 4)
Rapier: 14 to hit (adv(1d20) + 3); 41 damage (2d8 + 6d6 + 4)
Rapier: 21 to hit (adv(1d20) + 3); 38 damage (2d8 + 6d6 + 4)
Rapier: 19 to hit (adv(1d20) + 3); 34 damage (2d8 + 6d6 + 4)
```

```
>>> turn = [rapier_sneak_attack(), rapier_attack()]
>>> print("\n".join(turn))
Rapier: 19 to hit (1d20 + 3); 9 damage (1d8 + 3d6 + 4)
Rapier: 9 to hit (1d20 + 3); 5 damage (1d8 + 4)
```
