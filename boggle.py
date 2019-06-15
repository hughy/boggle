#! usr/bin/env python3
from functools import reduce
from pathlib import Path
import random
import _thread
import threading
from time import sleep
from typing import Callable, Iterable, List, Set, Tuple, TypeVar
import sys

import pygtrie
import prompt_toolkit.output as pyout


CUBES = [
    ["A", "A", "E", "E", "G", "N"],
    ["A", "B", "B", "J", "O", "O"],
    ["A", "C", "H", "O", "P", "S"],
    ["A", "F", "F", "K", "P", "S"],
    ["A", "O", "O", "T", "T", "W"],
    ["C", "I", "M", "O", "T", "U"],
    ["D", "E", "I", "L", "R", "X"],
    ["D", "E", "L", "R", "V", "Y"],
    ["D", "I", "S", "T", "T", "Y"],
    ["E", "E", "G", "H", "N", "W"],
    ["E", "E", "I", "N", "S", "U"],
    ["E", "H", "R", "T", "V", "W"],
    ["E", "I", "O", "S", "S", "T"],
    ["E", "L", "R", "R", "T", "Y"],
    ["H", "I", "M", "N", "Qu", "U"],
    ["H", "L", "N", "N", "R", "Z"],
]


DEFAULT_TIME_LIMIT = 60
DEFAULT_WORD_LIST_PATH = "./sowpods.txt"


def main():
    print("Reading word list...")
    word_list = _read_word_list()
    print("Scrambling grid...")
    grid = _animated_scramble_grid()
    player_entries = _play(grid)
    possible_words = _depth_first_search(grid, word_list)
    _display_results(player_entries, possible_words)


def _prompt_number_of_players() -> int:
    print("How many players? (1 or 2)")
    try:
        players = int(input())
        if players not in {1, 2}:
            raise ValueError
        return players
    except ValueError:
        return _prompt_number_of_players()
    finally:
        _clear_lines(2)


def _animated_scramble_grid():
    for _ in range(10):
        grid = _scramble_grid()
        _render_grid(grid)
        sleep(0.2)
        _clear_grid(grid)
    return _scramble_grid()


def _read_word_list(word_list_filepath: str = DEFAULT_WORD_LIST_PATH) -> pygtrie.Trie:
    word_list = pygtrie.Trie()
    with open(word_list_filepath, mode="r") as word_list_file:
        for word in word_list_file:
            word_list[word.strip()] = True
    return word_list


def _scramble_grid(cubes: List[List[str]] = CUBES) -> List[List[str]]:
    random.shuffle(cubes)
    return [
        [random.choice(cube) for cube in row] for row in [cubes[i::4] for i in range(4)]
    ]


def _play(grid: List[List[int]], time_limit: int = DEFAULT_TIME_LIMIT) -> List[str]:
    _conceal_grid(grid)
    print(
        "You will have {} seconds to find as many words as you can. Ready?".format(
            time_limit
        )
    )
    input()
    _clear_lines(2)
    _clear_grid(grid)
    _render_grid(grid)
    return _prompt_player(time_limit)


def _prompt_player(time_limit: int = DEFAULT_TIME_LIMIT) -> List[str]:
    print(
        "Enter as many words as you can find in the next {} seconds".format(time_limit)
    )
    timer = threading.Timer(time_limit, _thread.interrupt_main)
    player_entries = []
    try:
        timer.start()
        while True:
            # Capitalize all inputs
            player_entries.append(input().upper())
            _clear_lines(1)
    except KeyboardInterrupt:
        pass
    timer.cancel()
    print("Time's up!")
    return player_entries


def _render_grid(grid: List[List[str]]) -> None:
    row_separator = "\n---------------\n"
    rows = ["|".join([_pad_cube(c) for c in row]) for row in grid]
    print(row_separator.join(rows))


def _pad_cube(cube: str) -> str:
    right_padded = cube.ljust(3 - len(cube))
    return right_padded.rjust(len(right_padded) + 1)


def _conceal_grid(grid: List[List[str]]) -> None:
    concealed_grid = [[chr(9608) for cube in row] for row in grid]
    _render_grid(concealed_grid)


def _clear_lines(n: int) -> None:
    output = pyout.create_output(sys.stdout)
    output.cursor_up(n)
    output.erase_down()
    output.flush()


def _clear_grid(grid: List[List[int]]) -> None:
    _clear_lines(2 * len(grid) - 1)


def _depth_first_search(grid: List[List[str]], word_list: pygtrie.Trie) -> List[str]:
    words_found = set()
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            words_found = words_found.union(
                _dfs_visit((i, j), grid, word_list, "", set())
            )
    return words_found


def _dfs_visit(
    cube: Tuple[int, int],
    grid: List[List[str]],
    word_list: pygtrie.Trie,
    word: str,
    cubes_visited: Set[Tuple[int, int]],
) -> Set[str]:
    i, j = cube
    # Capitalize all words
    word += grid[i][j].upper()
    if not word_list.has_node(word):
        return set()
    words_found = {word} if word_list.has_key(word) and len(word) > 2 else set()
    neighbors = _get_neighboring_cubes(cube, grid, cubes_visited)
    neighboring_words = [
        _dfs_visit(n, grid, word_list, word, cubes_visited.union({cube}))
        for n in neighbors
    ]
    return reduce(lambda x, y: x.union(y), neighboring_words, words_found)


def _get_neighboring_cubes(cube, grid, cubes_visited) -> List[Tuple[int, int]]:
    i, j = cube
    neighbors = [
        (i - 1, j - 1),
        (i - 1, j),
        (i - 1, j + 1),
        (i, j - 1),
        (i, j + 1),
        (i + 1, j - 1),
        (i + 1, j),
        (i + 1, j + 1),
    ]
    return [
        (x, y)
        for (x, y) in neighbors
        if (
            x >= 0
            and y >= 0
            and x < len(grid)
            and y < len(grid[0])
            and (x, y) not in cubes_visited
        )
    ]


def _display_results(player_entries: List[str], possible_words: Set[str]) -> None:
    valid_entries, invalid_entries = _partition(
        player_entries, lambda e: e in possible_words
    )
    result_join = _list_outer_join(valid_entries, list(possible_words))
    result_table = [
        "{:16} {}".format(found or "", possible) for found, possible in result_join
    ]
    print("\n".join(result_table))
    print(
        "You found {} of {} possible words".format(
            len(valid_entries), len(possible_words)
        )
    )


T = TypeVar("T")


def _partition(
    iterable: Iterable[T], predicate: Callable[[T], bool]
) -> Tuple[List[T], List[T]]:
    a, b = [], []
    for i in iterable:
        (a if predicate(i) else b).append(i)
    return a, b


def _list_outer_join(left: List[T], right: List[T]) -> List[Tuple[T, T]]:
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


if __name__ == "__main__":
    main()
