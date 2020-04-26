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
    "floordiv": "//"
}

class DiceExpr:
    # todo -- expand to multiple alt args (for add and mul)
    # todo -- gt/lt/ge/le for thresholding
    def __init__(self, op, left, right=None):
        assert op in OP_STRS
        self.op = op
        self.left = left
        self.right = right
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
    def roll(self, repeat=None):
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
    def simplify(self):
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
    __call__ = roll
    def expr(self, other=None, *, op):
        return DiceExpr(op, self, other).simplify()
    __add__ = partialmethod(expr, op="add")
    __sub__ = partialmethod(expr, op="sub")
    __mul__ = partialmethod(expr, op="mul")
    __truediv__ = partialmethod(expr, op="truediv")
    __floordiv__ = partialmethod(expr, op="floordiv")

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
    def roll(self, repeat=None, agg=None):
        agg = self.agg if agg is None else agg
        if repeat is not None:
            result = np.empty(repeat, dtype=np.int64)
            for i in range(repeat):
                result[i] = self.roll(agg=agg)
            return result
        if agg == "adv":
            return self.roll(repeat=2, agg="sum").max()
        if agg == "disadv":
            return self.roll(repeat=2, agg="sum").min()
        result = np.empty(sum(self.dice_sides.values()), dtype=np.int64)
        i = 0
        for n_sides, n_dice in self.dice_sides.items():
            result[i:i+n_dice] = np.random.randint(1, n_sides + 1, size=n_dice, dtype=np.int64)
            i += n_dice
        if agg == "sum":
            return result.sum()
    def __str__(self):
        collect = [f"{n_dice}d{n_sides}" for n_sides, n_dice
                   in self.dice_sides.items()]
        result = " + ".join(collect)
        agg = "" if self.agg == "sum" else self.agg
        return f"{agg}({result})"
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

    def __repr__(self):
        return f"<Dice{self}>"
    __call__ = roll

d = Dice

