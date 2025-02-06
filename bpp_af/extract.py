def extract(m):
    inst = m._inst
    its = m._its
    arcs = m._arcs
    x = m._x
    vals = {
        arc: val
        for arc in arcs
        if (val := round(x[arc].x)) != 0
    }
    paths = []
    def _get_arc(u, v=None):
        arc, val = next(
            (arc, val)
            for arc, val in vals.items()
            if arc[0] == u and (v is None or arc[1] == v)
        )
        if val == 1:
            del vals[arc]
        else:
            vals[arc] -= 1
        return arc
    for j in range(inst.n + (len(inst.prefilled) if inst.prefilled is not None else 0)):
        if not vals:
            break
        u = 0
        path = []
        if inst.prefilled is not None and j < len(inst.prefilled):
            u = inst.prefilled[j]
            _get_arc(0, u)
        while True:
            try:
                u, v = _get_arc(u)
                path.append(v - u)
                u = v
            except StopIteration:
                break
        if u == 0:
            break
        paths.append(path)
    ids = {ci: [] for ci, bi in its}
    for idx, ci in enumerate(inst.c):
        ids[ci].append(idx)
    return [
        { ids_i.pop(0) for ci in path if ci in ids and (ids_i := ids[ci]) }
        for path in paths
    ]