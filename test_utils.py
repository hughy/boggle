import unittest

import utils


class TestUtils(unittest.TestCase):
    def test_partition(self):
        numbers = [1, 2, 3, 4, 5, 6, 7, 8]
        evens, odds = utils.partition(numbers, lambda x: x % 2 == 0)
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
        self.assertEqual(joined, utils.list_outer_join(left, right))

    def test_list_outer_join_unequal(self):
        long = [1, 2, 3, 4, 5]
        short = [6]
        joined = [(1, None), (2, None), (3, None), (4, None), (5, None), (None, 6)]
        self.assertEqual(joined, utils.list_outer_join(long, short))

    def test_list_outer_join_side_effects(self):
        left = [1, 3, 5, 7]
        right = [2, 4, 6, 7]

        utils.list_outer_join(left, right)
        self.assertEqual([1, 3, 5, 7], left)
        self.assertEqual([2, 4, 6, 7], right)
