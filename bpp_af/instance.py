import random
from dataclasses import dataclass

__all__ = ['Instance']


@dataclass
class Instance:
    c: list[int]
    cap: int
    prefilled: list[int] | None = None

    @property
    def n(self):
        return len(self.c)

    def sorted(self):
        return Instance(sorted(self.c, reverse=True), self.cap)

    @staticmethod
    def random(n: int, cap: int, max_c: int = None):
        assert n > 0, 'n should be positive'
        assert cap > 1,  'cap should be greater than one'
        if max_c is None:
            max_c = cap - 1
        assert max_c < cap, 'max_c should not exceed cap'
        return Instance([random.randint(1, max_c) for i in range(n)], cap)

    def check_feasible(self, sol: list[set[int]]):
        # all items present?
        sorted_items = sorted(i for pat in sol for i in pat)
        assert sorted_items == list(range(self.n)), 'items not matching'
        # capacity constraint satisfied?
        for j, pat in enumerate(sol):
            cap_j = sum(self.c[i] for i in pat)
            assert cap_j <= self.cap, f'capacity constraint violated at bin {j}: {cap_j} > {self.cap}'