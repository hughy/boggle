#! usr/bin/env python3
from functools import reduce
from pathlib import Path
import random
from typing import List, Set, Tuple

import pygtrie


CUBES = [
    ["a", "a", "e", "e", "g", "n"],
    ["a", "b", "b", "j", "o", "o"],
    ["a", "c", "h", "o", "p", "s"],
    ["a", "f", "f", "k", "p", "s"],
    ["a", "o", "o", "t", "t", "w"],
    ["c", "i", "m", "o", "t", "u"],
    ["d", "e", "i", "l", "r", "x"],
    ["d", "e", "l", "r", "v", "y"],
    ["d", "i", "s", "t", "t", "y"],
    ["e", "e", "g", "h", "n", "w"],
    ["e", "e", "i", "n", "s", "u"],
    ["e", "h", "r", "t", "v", "w"],
    ["e", "i", "o", "s", "s", "t"],
    ["e", "l", "r", "r", "t", "y"],
    ["h", "i", "m", "n", "qu", "u"],
    ["h", "l", "n", "n", "r", "z"],
]


DEFAULT_WORD_LIST_PATH = './sowpods.txt'


def main():
    word_list = _read_word_list()
    grid = _scramble_grid()


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


def _depth_first_search(grid: List[List[str]], word_list: pygtrie.Trie) -> List[str]:
    words_found = set()
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            words_found = words_found.union(_dfs_visit((i, j), grid, word_list, "", set()))
    return words_found


def _dfs_visit(cube: Tuple[int, int], grid: List[List[str]], word_list: pygtrie.Trie, word: str,
               cubes_visited: Set[Tuple[int, int]]) -> Set[str]:
    i, j = cube
    word += grid[i][j]
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
