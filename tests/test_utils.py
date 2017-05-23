import unittest

from market_tool import utils

class TestUtils(unittest.TestCase):
    def test_round_decimal(self):
        self.assertEqual(utils.round_decimal(12.12, 1), 12.1)
        self.assertEqual(utils.round_decimal(12.14, 1), 12.1)
        self.assertEqual(utils.round_decimal(12.15, 1), 12.2)
        self.assertEqual(utils.round_decimal(12.19, 1), 12.2)
        self.assertEqual(utils.round_decimal(7.45, 1), 7.5)

        self.assertEqual(utils.round_decimal(12.12, 2), 12.12)
        self.assertEqual(utils.round_decimal(12.14, 2), 12.14)
        self.assertEqual(utils.round_decimal(12.15, 2), 12.15)
        self.assertEqual(utils.round_decimal(12.19, 2), 12.19)



        self.assertEqual(utils.round_decimal(12.12, 5), 12.12)
        self.assertEqual(utils.round_decimal(12.14, 7), 12.14)
