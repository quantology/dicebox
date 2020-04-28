from collections.abc import Iterable, Mapping
from collections import Counter
from functools import partialmethod, partial
import operator

import numpy as np

OP_STRS = {
    "add": "+",
    "sub": "-",
    "truediv": "/",
    "mul": "*",
    "floordiv": "//",
    "eq": "==",
    "gt": ">",
    "ge": ">=",
    "lt": "<",
    "le": "<="
}

class DiceExpr:
    # todo -- expand to multiple alt args (for add and mul)
    # todo -- gt/lt/ge/le for thresholding
    def __init__(self, op, left, right=None):
        assert op in OP_STRS
        self.op = op
        self.left = left
        self.right = right
    def roll(self, repeat=None):
        # todo -- how to handle seeds here?
        try:
            
            left = self.left.roll(repeat=repeat)
        except AttributeError:
            left = self.left
        try:
            right = self.right.roll(repeat=repeat)
        except AttributeError:
            right = self.right
        op = getattr(operator, self.op)
        return op(left, right)
    __call__ = roll

    def simplify(self):
        # sympy?
        try:
            left = self.left.simplify()
        except AttributeError:
            left = self.left
        try:
            right = self.right.simplify()
        except AttributeError:
            right = self.right
        if self.op != "add":
            return DiceExpr(self.op, left, right)
        if not hasattr(left, "dice_sides") or not hasattr(right, "dice_sides"):
            return DiceExpr(self.op, left, right)
        if left.agg != right.agg:
            return DiceExpr(self.op, left, right)
        new_sides = {k: left.dice_sides.get(k, 0) + right.dice_sides.get(k, 0)
                     for k in set(left.dice_sides.keys()) | set(right.dice_sides.keys())}
        return Dice(new_sides, agg=left.agg)

    def expr(self, other=None, *, op):
        return DiceExpr(op, self, other).simplify()
    def rexpr(self, other, *, op):
        return DiceExpr(op, other, self).simplify()
    __add__ = partialmethod(expr, op="add")
    __sub__ = partialmethod(expr, op="sub")
    __mul__ = partialmethod(expr, op="mul")
    __truediv__ = partialmethod(expr, op="truediv")
    __floordiv__ = partialmethod(expr, op="floordiv")
    __eq__ = partialmethod(expr, op="eq")
    __lt__ = partialmethod(expr, op="lt")
    __le__ = partialmethod(expr, op="le")
    __gt__ = partialmethod(expr, op="gt")
    __ge__ = partialmethod(expr, op="ge")
    __radd__ = partialmethod(rexpr, op="add")
    __rsub__ = partialmethod(rexpr, op="sub")
    __rmul__ = partialmethod(rexpr, op="mul")
    __rtruediv__ = partialmethod(rexpr, op="truediv")
    __rfloordiv__ = partialmethod(rexpr, op="floordiv")

    def __str__(self):
        opstr = OP_STRS[self.op]
        left = str(self.left)
        if getattr(self.left, "op", None) == "add" and getattr(self.left, "agg", "sum") == "sum" and self.op == "add":
            left = left.strip("()")
        if self.right is None:
            return f"({opstr} {left})"
        right = str(self.right)
        if getattr(self.right, "op", None) == "add" and getattr(self.right, "agg", "sum") == "sum" and self.op == "add":
            right = right.strip("()")
        return f"({left} {opstr} {right})"
    def __repr__(self):
        return f"<DiceExpr{self}>"

class Dice(DiceExpr):
    def __init__(self, sides=6, *other_sides, agg="sum"):
        if not isinstance(sides, Iterable):
            sides = (sides,)
        if other_sides:
            sides += other_sides
        if not isinstance(sides, Mapping):
            sides = dict(Counter(sides))
        self.dice_sides = sides
        assert agg in {"sum", "adv", "disadv"}
        self.agg = agg
        self.op = "add"

    def roll(self, repeat=None, *, seed=None):
        n = 1 if repeat is None else repeat
        rng = np.random.default_rng(seed=seed)
        n_dice = sum(self.dice_sides.values())
        multi = self.agg != "sum"
        shape = (n, n_dice, 2) if multi else (n, n_dice)
        dice_range = np.empty(n_dice)
        i = 0
        for dice_max, n_dice in self.dice_sides.items():
            dice_range[i:i+n_dice] = dice_max
            i += n_dice
        dice_range = dice_range[np.newaxis, :, np.newaxis] if multi else dice_range[np.newaxis, :]
        randint = 1 + (rng.random(shape) * dice_range).astype(int)
        if self.agg == "adv":
            randint = np.max(randint, axis=2)
        elif self.agg == "disadv":
            randint = np.min(randint, axis=2)
        result = np.sum(randint, axis=1)
        if repeat is None:
            return result[0]
        return result
    __call__ = roll

    @property
    def adv(self):
        assert self.agg != "adv"
        agg = {"disadv": "sum", "sum": "adv"}[self.agg]
        return Dice(sides=self.dice_sides, agg=agg)
    @property
    def disadv(self):
        assert self.agg != "disadv"
        agg = {"adv": "sum", "sum": "disadv"}[self.agg]
        return Dice(sides=self.dice_sides, agg=agg)

    def __str__(self):
        collect = [f"{n_dice}d{n_sides}" for n_sides, n_dice
                   in self.dice_sides.items()]
        result = " + ".join(collect)
        agg = "" if self.agg == "sum" else self.agg
        return f"{agg}({result})"
    def __repr__(self):
        return f"<Dice{self}>"

d = Dice
