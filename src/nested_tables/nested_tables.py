from collections import namedtuple

TableInfo = namedtuple('TableInfo', ['ok', 'result', 'index', 'parent']) 

__all__ = [
    "is_table",
    "is_map",
    "is_seq",
    "get_in",
    "get_and_update_in",
    "update_in",
    "filter_map",
    "grep",
    "append_in",
    "pop_in",
    "extend_in",
]

from collections.abc import (
    Mapping,
    Sequence,
    MutableMapping,
    MutableSequence,
    Callable,
    Iterable,
)

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
    except:
        return (False, None)


def put_key(x, key, value) -> bool:
    try:
        x[key] = value
    except:
        return False

    return True


def get_in(
    x: Table,
    keys: list[Any],
    default: DefaultCallable = lambda: None,
    level=False,
    update: Optional[Transformer] = None,
) -> Optional[Any | TableInfo]:
    y = x
    limit = len(keys) - 1
    i, k = None, None

    for i, k in enumerate(keys):
        ok, out = get_key(y, k)

        if not ok:
            if level:
                return TableInfo(False, None, i, y)
            else:
                return default()
        elif i == limit:
            if update:
                if not put_key(y, k, update(out)):
                    return False
                else:
                    out = y[k]

            if level:
                return TableInfo(True, out, i, y)
            else:
                return out
        elif not is_table(out):
            if level:
                return TableInfo(False, None, i, y)
            else:
                return default()
        else:
            y = out

    if level:
        return TableInfo(False, None, i, y)
    else:
        return default()


def get_and_update_in(
    x: MutTable, keys: list[Any], value: Any, default=lambda: None, level=False
) -> Optional[Any | TableInfo]:
    return get_in(x, keys, update=value, default=default, level=level)


def update_in(
    x: MutTable,
    keys: list[Any],
    f: Callable[[Any], Any],
    force: bool = False,
    default: Optional[Callable[[], Any]] = None,
) -> bool | MutTable:
    mut = is_mut(x)

    if not mut:
        return False

    y = x
    kind = type(x)

    for i, k in enumerate(keys[:-1]):
        ok, out = get_key(y, k)

        if not ok:
            if force:
                if not put_key(y, k, kind()):
                    return False
                else:
                    y = y[k]
            else:
                return False
        elif not is_mut(out):
            if force:
                if not put_key(y, k, kind()):
                    return False
                else:
                    y = y[k]
            else:
                return False
        else:
            y = out

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


def filter_map(
    f: Transformer, xs: Iterable | Mapping, cond: CondCallable = lambda x: x
) -> tuple[Any] | dict:
    if is_map(xs):
        res = {}

        for k, v in xs.items():
            if cond(k, v):
                res[k] = f(v)

        return res
    else:
        return tuple(f(x) for x in xs if cond(x))


def extend_in(xs: MutSeq, keys: list[Any], *args) -> list[Any] | bool:
    d: MutSeq
    ok, out, _, d = get_in(xs, keys, level=True)

    if not ok or not is_mut_seq(d):
        return False

    for x in args:
        if is_seq(x):
            d.extend(x)
        else:
            d.append(x)

    return d


def append_in(xs: Sequence, keys: list[Any], *args) -> MutSeq | bool:
    ok, out, _, d = get_in(xs, keys, level=True)

    if not ok or not is_mut_seq(d):
        return False

    for x in args:
        d.append(x)

    return d


def pop_in(xs: Table, keys: list[Any]) -> tuple[bool, MutTable | Any]:
    ok, out, i, d = get_in(xs, keys, level=True)

    if not ok or (not is_mut_map(d) and not is_mut_seq(d)):
        return (False, i)

    last = keys[-1]

    if is_map(d):
        return (True, d.pop(last))
    else:
        item = d.pop(last)
        return (True, item)
