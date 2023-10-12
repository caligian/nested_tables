__all__ = [
    "is_table",
    "is_map",
    "get_in",
    "get_and_update_in",
    "update_in",
    "filter_map",
    "grep",
]

from collections.abc import (
    Mapping,
    Sequence,
    MutableMapping,
    MutableSequence,
    Callable,
    Iterable,
)

from functools import reduce
from typing import Any, Optional

CondCallable = Callable[[Any], bool]
MutTable = MutableSequence | MutableMapping
Table = Sequence | Mapping
Seq = Sequence
Map = Mapping
MutSeq = MutableSequence
MutMap = MutableMapping
DefaultCallable = Callable[[], Any]
Transformer = Callable[[Any], Any] | Callable[[Any, Any], Any]


def is_table(x: Table):
    kind = type(x)
    return issubclass(kind, Table)


def is_mut_seq(x: Table) -> bool:
    kind = type(x)
    return issubclass(kind, MutSeq)


def is_seq(x: Table) -> bool:
    kind = type(x)
    return issubclass(kind, Seq)


def is_map(x: Table) -> bool:
    kind = type(x)
    return issubclass(kind, Map)


def is_mut_map(x: Table) -> bool:
    kind = type(x)
    return issubclass(kind, MutMap)


def is_mut(x: Table) -> bool:
    return is_mut_map(x) or is_mut_seq(x)


def get_key(x: Table, key: Any):
    try:
        return (True, x[key])
    except LookupError:
        return (False, None)


def put_key(x, key, value) -> bool:
    try:
        x[key] = value
    except:
        return False

    return True


def get_in(
    x: Table,
    keys: list,
    default: DefaultCallable = lambda: None,
    level=False,
    update: Optional[Transformer] = None,
) -> Optional[Any | tuple[bool, Any, int, Table]]:
    y = x
    limit = len(keys) - 1
    i, k = None, None

    for i, k in enumerate(keys):
        ok, out = get_key(y, k)

        if not ok:
            if level:
                return (False, None, i, y)
            else:
                return default()
        elif i == limit:
            if update:
                if not put_key(y, k, update(out)):
                    return False
                else:
                    out = y[k]

            if level:
                return (True, out, i, y)
            else:
                return out
        elif not is_table(out):
            if level:
                return (False, None, i, y)
            else:
                return default()
        else:
            y = out

    if level:
        return (False, None, i, y)
    else:
        return default()


def get_and_update_in(x: MutTable, keys: list, value: Any, default=lambda: None, level=False) -> Any:
    return get_in(x, keys, update=value, default=default, level=level)


def update_in(
    x: MutTable,
    keys: list,
    f: Callable[[Any], Any],
    force: bool = False,
    default: Optional[Callable[[], Any]] = None) -> bool | MutTable:
    mut = is_mut(x)
    if not mut:
        return False

    y = x
    kind = type(x)
    last = None

    for i, k in enumerate(keys[:-1]):
        last = i
        ok, out = get_key(y, k)

        if not ok or not is_mut(out):
            break
        else:
            y = out

    if i != len(keys) - 2 and not force:
        return False

    for k in keys[last:-1]:
        if not put_key(y, k, kind()):
            return False
        else:
            y = y[k]

    match get_key(y, keys[-1]):
        case (True, v):
            y[keys[-1]] = f(v)
        case (False, _):
            if default:
                if not put_key(y, keys[-1], default()):
                    return False
            else:
                if not put_key(y, keys[-1], kind()):
                    return False

    return x


def grep(cond: CondCallable, xs: Iterable | Mapping) -> tuple | dict:
    if is_map(xs):
        res = {}

        for k, v in xs.items(): 
            if cond(k, v):
                res[k] = v

        return res
    else:
        return tuple(x for x in xs if cond(x))


def filter_map(f: Transformer, 
               xs: Iterable | Mapping, 
               cond: CondCallable = lambda x: x) -> tuple | dict:
    if is_map(xs):
        res = {}

        for k, v in xs.items(): 
            if cond(k, v):
                res[k] = f(v)

        return res
    else:
        return tuple(f(x) for x in xs if cond(x))
        

def extend_in(xs: MutSeq, keys: list, *args) -> list | bool:
    d: MutSeq
    ok, out, _, d = get_in(xs, keys, level=True)

    if not ok or not is_mut_seq(xs):
        return False

    for x in args:
        if is_seq(x):
            d.extend(x)
        else:
            d.append(x)

    return d


def append_in(xs: Sequence, keys: list, *args) -> MutSeq | bool:
    ok, out, _, d = get_in(xs, keys, level=True)

    if not ok or not is_mut_seq(d):
        return False

    for x in args:
        d.append(x)

    return d


def pop_in(xs: Table, keys: list) -> tuple[Any, MutTable] | bool:
    ok, out, _, d = get_in(xs, keys, level=True)

    if not ok or (not is_mut_map(d) and not is_mut_seq(d)):
        return False

    last = keys[-1]

    if is_map(d):
        return d.pop(last)
    else:
        item = d.pop(last)
        return (item, d)


test = {'aa': {'b': {'c': {'d': [0]}}}}
ks = ['aa', 'b', 'c', 'd', 0]
ok, out, i, d = get_in(test, ks, level=True, update=lambda x: x * 10)

print(append_in(test, ks, 1, 2, 3, 4))
print(pop_in(test, ks))
print(test)
