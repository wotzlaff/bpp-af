import collections

has_gurobipy = False
try:
    import gurobipy as gp
    has_gurobipy = True
except ImportError:
    import mip

from .instance import Instance
from .extract import extract


def build(inst: Instance):
    cnt = collections.Counter(inst.c)
    its = sorted(cnt.items(), reverse=True)

    verts = {0}
    item_arcs = []
    arcs = set()

    if inst.prefilled is not None:
        cnt_prefilled = collections.Counter(inst.prefilled)
        for lj in cnt_prefilled.keys():
            arcs.add((0, lj))
            verts.add(lj)

    for ci, bi in its:
        arcs_i = set()
        for u in sorted(verts, reverse=True):
            for _ in range(bi):
                v = u + ci
                if v > inst.cap:
                    break
                verts.add(v)
                arcs_i.add((u, v))
                u = v
        item_arcs.append(arcs_i)
        arcs |= arcs_i

    if has_gurobipy:
        m = gp.Model()
        m._inst = inst
        m._its = its
        x = m.addVars(arcs, name='x', vtype=gp.GRB.INTEGER)
        m._x = x
        m._arcs = arcs
        m._item_arcs = item_arcs

        m.addConstrs((
            gp.quicksum(x[arc] for arc in item_arcs[i]) >= bi + (sum([1 for ck in inst.prefilled if ck == ci]) if inst.prefilled is not None else 0)
            for i, (ci, bi) in enumerate(its)
        ), name='sat')
        m.addConstrs((
            x.sum('*', u) >= x.sum(u, '*')
            for u in verts if u > 0
        ), name='conserve')

        if inst.prefilled is not None:
            for lj, nj in cnt_prefilled.items():
                m.addConstr(x[0, lj] >= nj)

        m.setObjective(x.sum(0, '*'))
    else:
        m = mip.Model()
        m._inst = inst
        m._its = its
        x = {
            arc: m.add_var(var_type=mip.INTEGER)
            for arc in arcs
        }
        m._x = x
        m._arcs = arcs
        m._item_arcs = item_arcs

        for i, (ci, bi) in enumerate(its):
            pre_bi = sum([1 for ck in inst.prefilled if ck == ci]) if inst.prefilled is not None else 0
            m.add_constr(mip.xsum(x[arc] for arc in item_arcs[i]) >= bi + pre_bi)

        for u in verts:
            if u == 0:
                continue
            m.add_constr(
                mip.xsum(x[arc] for arc in arcs if u == arc[1])
                >=
                mip.xsum(x[arc] for arc in arcs if u == arc[0])
            )

        if inst.prefilled is not None:
            for lj, nj in cnt_prefilled.items():
                m.add_constr(x[0, lj] >= nj)

        m.objective = mip.xsum(x[arc] for arc in arcs if arc[0] == 0)
    return m


def solve(inst: Instance):
    m = build(inst)
    if has_gurobipy:
        m.setParam('OutputFlag', 0)
    else:
        m.verbose = 0
    m.optimize()
    return extract(m)