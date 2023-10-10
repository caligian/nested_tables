from collections.abc import MutableMapping, MutableSequence, Callable

Table = MutableSequence | MutableMapping
Seq = MutableMapping
Map = MutableMapping

def get(
    x: Table,
    keys: list,
    make_path=False,
    include_level=False,
    default=lambda: None,
):
    out = None
    l: int = len(keys) - 1
    tp = type(x)
    is_map = lambda a: issubclass(type(a), Map)

    for n, key in enumerate(keys):
        found = False

        try:
            out = x[key]
            found = True
        except LookupError:
            found = False
        except:
            found = False

        if not found:
            if make_path and is_map(x):
                x[key] = tp()
                out = x[key]
            elif include_level:
                return (default(), x)
            else:
                return default()

        if not issubclass(type(out), Table):
            if n == l:
                if include_level:
                    return (out, x)
                else:
                    return out
            elif include_level:
                return (default(), x)
            else:
                return default()
        else:
            x = x[key]

    if include_level:
        return (out, x)

    return out


def get_and_update(
    x: Table,
    keys: list,
    f: Callable,
    make_path=False,
    include_level=False,
    default=lambda: None,
):
    out, d = get(x, keys, make_path=make_path, include_level=True)
    last = keys[-1]
    is_map = issubclass(type(x), Map)

    if out != None and is_map:
        d[last] = f(out)
    elif make_path and is_map:
        d[last] = f(default())
    elif out == None and include_level:
        return (default(), d)
    elif out == None:
        return default()

    if include_level:
        return (d[last], d)
    else:
        return d[last]
