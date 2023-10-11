from collections.abc import Mapping, Sequence, MutableMapping, MutableSequence, Callable
from functools import reduce
from typing import Any, Optional

MutTable = MutableSequence | MutableMapping
Table = Sequence | Mapping
Seq = Sequence
Map = Mapping
MutSeq = MutableSequence
MutMap = MutableMapping


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


def get(
    x: Table,
    keys: list,
    default: Callable[[], Any] = lambda: None,
    level=False,
    update: Optional[Callable[[Any], Any]] = None,
) -> Optional[Any | tuple[bool, Any, Any]]:
    y = x
    limit = len(keys) - 1
    i, k = None, None

    for i, k in enumerate(keys):
        ok, out = get_key(y, k)

        if not ok:
            if level:
                return (False, i, k)
            else:
                return default()
        elif i == limit:
            if update:
                if not put_key(y, k, update(out)):
                    return False
                else:
                    out = y[k]

            if level:
                return (True, i, k)
            else:
                return out
        elif not is_table(out):
            if level:
                return (False, i, k)
            else:
                return default()
        else:
            y = out

    if level:
        return (False, i, k)
    else:
        return default()


def get_and_update(
    x: MutTable, keys: list, value: Any, default=lambda: None, level=False
) -> Any:
    return get(x, keys, update=value, default=default, level=level)


def update(
    x: MutTable,
    keys: list,
    f: Callable[[Any], Any],
    force: bool = False,
    default: Optional[Callable[[], Any]] = None,
) -> bool | MutTable:
    mut = is_mut(x)
    if not mut:
        return False

    y = x
    kind = type(x)
    last = None

    for i, k in enumerate(keys[:-1]):
        last = i
        ok, out = get_key(y, k)

        if not ok:
            break
        elif is_mut(out):
            y = out
        else:
            break

    for k in keys[last:-1]:
        if force:
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

def grep(cond: Callable[[Any], bool], X: tuple | list) -> tuple | list:
    kind = type(X)
    return kind(x for x in X if cond(x))

def filtermap(f: Callable[[Any], Any],
              X: tuple | list, 
              cond: Callable[[Any], bool]=lambda x: x) -> tuple | list:
    kind = type(X)
    return kind(f(x) for x in X if cond(x))

def rpartial(f, *outer_args, **outer_kwargs):
    def g(*args, **kwargs):
        all_args =  list(args) + list(outer_args)
        outer_kwargs.update(kwargs)

        return f(*all_args, **outer_kwargs)

    return g

def partial(f, *outer_args, **outer_kwargs):
    def g(*args, **kwargs):
        all_args = list(outer_args) + list(args)
        kwargs.update(outer_kwargs)

        return f(*all_args, **kwargs)

    return g
