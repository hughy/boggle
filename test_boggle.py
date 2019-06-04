#! /usr/bin/env python3
import tempfile
import unittest

import boggle


class TestBoggle(unittest.TestCase):

    TEST_CUBES = list("0123456789ABCDEF")
    TEST_WORD_LIST = {"TEST", "SET"}
    TEST_GRID = [
        ["T", "-", "-", "-"],
        ["-", "E", "-", "-"],
        ["-", "-", "S", "-"],
        ["-", "-", "-", "T"]
    ]

    def test_scramble_grid(self):
        grid = boggle._scramble_grid(self.TEST_CUBES)
        self.assertEqual(4, len(grid))
        self.assertTrue(all(len(row) == 4 for row in grid))
        self.assertEqual(sorted(self.TEST_CUBES), sorted([cube for row in grid for cube in row]))

    def test_read_word_list(self):
        temp_word_list_file = tempfile.NamedTemporaryFile(mode="w+")
        temp_word_list_file.write("\n".join(self.TEST_WORD_LIST))
        temp_word_list_file.flush()
        word_list = boggle._read_word_list(word_list_filepath=temp_word_list_file.name)
        self.assertEqual(self.TEST_WORD_LIST, word_list)

    def test_dfs_visit(self):
        words_found = boggle._dfs_visit((0, 0), self.TEST_GRID, self.TEST_WORD_LIST, "", set())
        self.assertEqual({"TEST"}, words_found)

    def test_depth_first_search(self):
        words_found = boggle._depth_first_search(self.TEST_GRID, self.TEST_WORD_LIST)
        self.assertEqual(self.TEST_WORD_LIST, words_found)
