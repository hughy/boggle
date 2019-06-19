from typing import Callable, Iterable, List, Tuple, TypeVar
import sys

import prompt_toolkit.output as pyout


T = TypeVar("T")


def partition(
    iterable: Iterable[T], predicate: Callable[[T], bool]
) -> Tuple[List[T], List[T]]:
    a, b = [], []
    for i in iterable:
        (a if predicate(i) else b).append(i)
    return a, b


def list_outer_join(left: List[T], right: List[T]) -> List[Tuple[T, T]]:
    joined = []
    ls = sorted(left)
    rs = sorted(right)
    l = ls.pop(0) if ls else None
    r = rs.pop(0) if rs else None
    while l or r:
        if l == r or l is None or r is None:
            joined.append((l, r))
            l = ls.pop(0) if ls else None
            r = rs.pop(0) if rs else None
        elif l < r:
            joined.append((l, None))
            l = ls.pop(0) if ls else None
        else:
            joined.append((None, r))
            r = rs.pop(0) if rs else None
    return joined


def clear_lines(n: int) -> None:
    output = pyout.create_output(sys.stdout)
    output.cursor_up(n)
    output.erase_down()
    output.flush()
