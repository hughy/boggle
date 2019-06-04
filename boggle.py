#! usr/bin/env python3
from functools import reduce
from pathlib import Path
import random
from typing import List, Set


CUBES = [
    "DTYTSI",
    "JBOABO",
    "WEGHEN",
    "SIENUE",
    "VLREYD",
    "TUICMO",
    "XRDILE",
    "ANEGAE",
    "FKFPSA",
    "POCSHA",
    "OOATTW",
    "LNRZNH",
    "TIOSSE",
    "RYELTT",
    "WHTVER",
    "MNHQIU"
]


DEFAULT_WORD_LIST_PATH = './sowpods.txt'


def main():
    word_list = _read_word_list()
    grid = _scramble_grid()


def _read_word_list(word_list_filepath = DEFAULT_WORD_LIST_PATH) -> Set[str]:
    with open(word_list_filepath, mode='r') as word_list:
        lexicon = {word.strip() for word in word_list}
    return lexicon


def _scramble_grid(cubes = CUBES) -> List[List[str]]:
    random.shuffle(cubes)
    return [
        [random.choice(cube) for cube in row]
        for row in [cubes[i::4] for i in range(4)]
    ]


def _depth_first_search(grid, word_list) -> List[str]:
    words_found = set()
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            words_found = words_found.union(_dfs_visit((i, j), grid, word_list, "", set()))
    return words_found


def _dfs_visit(cube, grid, word_list, word, cubes_visited):
    i, j = cube
    word += grid[i][j]
    words_found = {word} if word in word_list else set()
    neighbors = _get_neighboring_cubes(cube, grid, cubes_visited)
    neighboring_words = [_dfs_visit(n, grid, word_list, word, cubes_visited.union({cube})) for n in neighbors]
    return reduce(lambda x, y: x.union(y), neighboring_words, words_found)


def _get_neighboring_cubes(cube, grid, cubes_visited):
    i, j = cube
    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                 (i, j - 1), (i, j + 1),
                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
    return [(x, y) for (x, y) in neighbors
            if (x >= 0 and y >= 0 and x < len(grid) and y < len(grid[0])
            and (x, y) not in cubes_visited)]


if __name__ == "__main__":
    main()
