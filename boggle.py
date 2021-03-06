#! usr/bin/env python3
from functools import reduce
from pathlib import Path
import random
import _thread
import threading
from time import sleep
from typing import List, Set, Tuple

import pygtrie

import utils


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
DEFAULT_WORD_LIST_PATH = Path("sowpods.txt")


def main() -> None:
    print("Reading word list...")
    word_list = _read_word_list()
    print("Scrambling grid...")
    grid = _animated_scramble_grid()
    player_entries = _play(grid)
    possible_words = _depth_first_search(grid, word_list)
    _display_results(player_entries, possible_words)


def _animated_scramble_grid() -> List[List[str]]:
    """
    Iteratively generate, display, and clear a grid to animate grid scrambling/randomization.

    :return: the final scrambled grid
    :rtype: List[List[str]]
    """
    for _ in range(10):
        grid = _scramble_grid()
        _render_grid(grid)
        sleep(0.2)
        _clear_grid(len(grid))
    return _scramble_grid()


def _read_word_list(word_list_filepath: Path = DEFAULT_WORD_LIST_PATH) -> pygtrie.Trie:
    """
    :param Path word_list_filepath: Path to a file containing the list of valid words
    :return: Trie containing all valid words
    :rtype: pygtrie.Trie
    """
    word_list = pygtrie.Trie()
    with open(word_list_filepath, mode="r") as word_list_file:
        # Word list file must contain one word per line
        for word in word_list_file:
            word_list[word.strip()] = True
    return word_list


def _scramble_grid(cubes: List[List[str]] = CUBES) -> List[List[str]]:
    """
    :param List[List[str]] cubes: a list of lists of strings with each string representing a face
    of a Boggle cube
    :return: a random arrangement of the input cubes, with one side of each cube randomly chosen
    :rtype: List[List[str]]
    """
    random.shuffle(cubes)
    return [
        [random.choice(cube) for cube in row] for row in [cubes[i::4] for i in range(4)]
    ]


def _play(grid: List[List[str]], time_limit: int = DEFAULT_TIME_LIMIT) -> List[str]:
    """
    Play a single-player game of Boggle with the given grid of letters. The player has time_limit
    seconds to find as many words in the grid as possible and enter them in the prompt.

    :param [List[List[str]]] grid: grid of letters to find words in
    :param int time_limit: time limit (in seconds) for player entries
    :return: list of all player entries within the time limit.
    :rtype: List[str]
    """
    # Conceal the grid until player ready
    _render_concealed_grid(grid)
    print(
        "You will have {} seconds to find as many words as you can. Ready?".format(
            time_limit
        )
    )
    input()
    utils.clear_lines(2)
    _clear_grid(len(grid))
    _render_grid(grid)
    return _prompt_player(time_limit)


def _prompt_player(time_limit: int = DEFAULT_TIME_LIMIT) -> List[str]:
    """
    :param int time_limit: time limit (in seconds) for player entries
    :return: list of all player entries within the time limit
    :rtype: List[str]
    """
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
            # Clear user input to avoid pushing grid out of view
            utils.clear_lines(1)
    except KeyboardInterrupt:
        pass
    timer.cancel()
    print("Time's up!")
    return player_entries


def _render_grid(grid: List[List[str]]) -> None:
    """
    :param List[List[str]] grid: grid of letters to display
    :return: None
    """
    row_separator = "\n---------------\n"
    rows = ["|".join([_pad_cube(c) for c in row]) for row in grid]
    print(row_separator.join(rows))


def _pad_cube(cube: str) -> str:
    """
    Pad letter cube with whitespace to improve rendering.

    :param str cube: a single letter from the grid (or "Qu")
    :return: input cube string with right and left padding
    :rtype: str
    """
    right_padded = cube.ljust(3 - len(cube))
    return right_padded.rjust(len(right_padded) + 1)


def _render_concealed_grid(grid: List[List[str]]) -> None:
    """
    :param List[List[str]] grid: a grid of letters
    :return: None
    """
    # chr(9608): full block character
    concealed_grid = [[chr(9608) for cube in row] for row in grid]
    _render_grid(concealed_grid)


def _clear_grid(grid_size: int) -> None:
    """
    Clear the grid from the console output by clearing lines equal to the number of rows in the
    grid plus row separators.

    :param int grid_size: number of rows in the grid to clear
    :return: None
    """
    utils.clear_lines(2 * grid_size - 1)


def _depth_first_search(grid: List[List[str]], word_list: pygtrie.Trie) -> Set[str]:
    """
    Perform depth-first search according to Boggle rules to identify all valid words found within
    the given grid. A word is valid if it is present in the word list and can be constructed from
    the letters in the grid according to the following rules:
        1. The word is three or more letters long
        2. The word can be constructed from adjacent cubes, where "adjacent" cubes neighbor one
           another horizontally, vertically, or diagonally
        3. A given letter cube is used at most once to construct the word

    :param List[List[str]] grid: grid of letters to search for words
    :param pygtrie.Trie word_list: a Trie containing all valid words
    :return: set of all valid words findable in the given grid
    :rtype: Set[str]
    """
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
    """
    Visit the next state in a depth-first search for words in the letter grid.

    :param Tuple[int, int] cube: grid indices of a letter cube
    :param List[List[str]] grid: a grid of letter cubes to search
    :param pygtrie.Trie word_list: a Trie containing all valid words
    :param str word: a string of letters representing the current search path
    :param Set[Tuple[int, int]] cubes_visited: set of cube indices already visited
    :return: set of valid words found from the current search state
    :rtype: Set[str]
    """
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


def _get_neighboring_cubes(
    cube: Tuple[int, int], grid: List[List[str]], cubes_visited: Set[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """
    :param Tuple[int, int] cube: a tuple representing the indices of a given cube within the grid
    :param List[List[str]] grid: grid of letter cubes
    :param Set[Tuple[int, int]] cubes_visited: set of cubes already visited in a depth-first
    search path
    :return: list of valid neighboring indices of the given cube
    :rtype: List[Tuple[int, int]]
    """
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
    """
    Display the results of a single-player Boggle game. Print valid player entries alongside all
    possible words for comparison.

    :param List[str] player_entries: the list of all player entries
    :param Set[str] possible_words: the set of all valid words found within the grid
    :return: None
    """
    valid_entries, invalid_entries = utils.partition(
        player_entries, lambda e: e in possible_words
    )
    result_join = utils.list_outer_join(valid_entries, list(possible_words))
    result_table = [
        "{:16} {}".format(found or "", possible) for found, possible in result_join
    ]
    print("\n".join(result_table))
    print(
        "You found {} of {} possible words".format(
            len(valid_entries), len(possible_words)
        )
    )


if __name__ == "__main__":
    main()
