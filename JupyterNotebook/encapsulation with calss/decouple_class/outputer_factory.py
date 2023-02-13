from typing import Callable, Any

from outputer import Outputer

creation_funcs: dict[str, Callable[..., Outputer]] = {}


def register(kind: str, creation_func: Callable[..., Outputer]) -> None:
    creation_funcs[kind] = creation_func


def unregister(kind: str) -> None:
    creation_funcs.pop(kind, None)


def create(args: dict[str, Any]) -> Outputer:
    the_args = args.copy()
    kind = the_args.pop('kind')
    try:
        creation_func = creation_funcs[kind]
        return creation_func(**the_args)
    except KeyError:
        raise ValueError(f'未知的Outputer {kind}') from None
