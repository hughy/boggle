#! /usr/bin/env python3
import tempfile
import unittest

import pygtrie

import boggle


class TestBoggle(unittest.TestCase):

    TEST_CUBES = list("0123456789ABCDEF")
    TEST_WORDS = {"TEST", "SET"}
    TEST_WORD_LIST = pygtrie.Trie.fromkeys(TEST_WORDS, True)
    TEST_GRID = [
        ["T", "-", "-", "-"],
        ["-", "E", "-", "-"],
        ["-", "-", "S", "-"],
        ["-", "-", "-", "T"],
    ]

    def test_scramble_grid(self):
        grid = boggle._scramble_grid(self.TEST_CUBES)
        self.assertEqual(4, len(grid))
        self.assertTrue(all(len(row) == 4 for row in grid))
        self.assertEqual(
            sorted(self.TEST_CUBES), sorted([cube for row in grid for cube in row])
        )

    def test_read_word_list(self):
        temp_word_list_file = tempfile.NamedTemporaryFile(mode="w+")
        temp_word_list_file.write("\n".join(self.TEST_WORDS))
        temp_word_list_file.flush()
        word_list = boggle._read_word_list(word_list_filepath=temp_word_list_file.name)
        self.assertEqual(self.TEST_WORD_LIST, word_list)

    def test_dfs_visit(self):
        words_found = boggle._dfs_visit(
            (0, 0), self.TEST_GRID, self.TEST_WORD_LIST, "", set()
        )
        self.assertEqual({"TEST"}, words_found)

    def test_depth_first_search(self):
        words_found = boggle._depth_first_search(self.TEST_GRID, self.TEST_WORD_LIST)
        self.assertEqual(self.TEST_WORDS, words_found)

    def test_partition(self):
        numbers = [1, 2, 3, 4, 5, 6, 7, 8]
        evens, odds = boggle._partition(numbers, lambda x: x % 2 == 0)
        self.assertEqual([2, 4, 6, 8], evens)
        self.assertEqual([1, 3, 5, 7], odds)

    def test_list_outer_join(self):
        left = [1, 3, 5, 7]
        right = [2, 4, 6, 7]
        joined = [
            (1, None),
            (None, 2),
            (3, None),
            (None, 4),
            (5, None),
            (None, 6),
            (7, 7),
        ]
        self.assertEqual(joined, boggle._list_outer_join(left, right))
        # Ensure that _list_outer_join does not modify input
        self.assertEqual([1, 3, 5, 7], left)
        self.assertEqual([2, 4, 6, 7], right)
