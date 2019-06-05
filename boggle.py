#! usr/bin/env python3
from functools import reduce
from pathlib import Path
import random
from typing import List, Set, Tuple

import pygtrie


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


DEFAULT_WORD_LIST_PATH = './sowpods.txt'


def main():
    word_list = _read_word_list()
    grid = _scramble_grid()
    _render_grid(grid)
    words_found = list(_depth_first_search(grid, word_list))
    words_found.sort(key=lambda w: (len(w), w[0]))
    print("\n".join(words_found))


def _read_word_list(word_list_filepath: str = DEFAULT_WORD_LIST_PATH) -> pygtrie.Trie:
    word_list = pygtrie.Trie()
    with open(word_list_filepath, mode='r') as word_list_file:
        for word in word_list_file:
            word_list[word.strip()] = True
    return word_list


def _scramble_grid(cubes: List[List[str]] = CUBES) -> List[List[str]]:
    random.shuffle(cubes)
    return [
        [random.choice(cube) for cube in row]
        for row in [cubes[i::4] for i in range(4)]
    ]


def _render_grid(grid: List[List[str]]) -> None:
    row_separator = "\n---------------\n"
    rows = ["|".join([_pad_cube(c) for c in row]) for row in grid]
    print("\n" + row_separator.join(rows) + "\n")


def _pad_cube(cube: str) -> str:
    right_padded = cube.ljust(3 - len(cube))
    return right_padded.rjust(len(right_padded) + 1)


def _depth_first_search(grid: List[List[str]], word_list: pygtrie.Trie) -> List[str]:
    words_found = set()
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            words_found = words_found.union(_dfs_visit((i, j), grid, word_list, "", set()))
    return words_found


def _dfs_visit(cube: Tuple[int, int], grid: List[List[str]], word_list: pygtrie.Trie, word: str,
               cubes_visited: Set[Tuple[int, int]]) -> Set[str]:
    i, j = cube
    word += grid[i][j].upper()
    if not word_list.has_node(word):
        return set()
    words_found = {word} if word_list.has_key(word) else set()
    neighbors = _get_neighboring_cubes(cube, grid, cubes_visited)
    neighboring_words = [_dfs_visit(n, grid, word_list, word, cubes_visited.union({cube}))
                         for n in neighbors]
    return reduce(lambda x, y: x.union(y), neighboring_words, words_found)


def _get_neighboring_cubes(cube, grid, cubes_visited) -> List[Tuple[int, int]]:
    i, j = cube
    neighbors = [(i - 1, j - 1),
                 (i - 1, j),
                 (i - 1, j + 1),
                 (i, j - 1),
                 (i, j + 1),
                 (i + 1, j - 1),
                 (i + 1, j),
                 (i + 1, j + 1)]
    return [(x, y) for (x, y) in neighbors
            if (x >= 0 and y >= 0 and x < len(grid) and y < len(grid[0])
            and (x, y) not in cubes_visited)]


if __name__ == "__main__":
    main()
