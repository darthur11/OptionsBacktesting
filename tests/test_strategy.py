import datetime
from unittest import TestCase

import strategy


class TestStrategy(TestCase):
    def test_get_expirations(self):
        obj = strategy.Strategy(0, None, "2022-12-01")
        test = obj.get_expirations()
        expected = [(datetime.date(2022, 12, 16), datetime.timedelta(days=15)),
                    (datetime.date(2023, 1, 20), datetime.timedelta(days=50))]
        self.assertEqual(test, expected)

    def test_open_strat(self):
        obj = strategy.Strategy(0, None, "2022-12-02")
        test = obj.open_strat()
        expected = 1
        self.assertEqual(test, expected)

    def test_close_strat_should_close_positions(self):
        obj = strategy.Strategy(2, 5, "2022-12-02", 200)
        test = obj.close_strat()
        expected = 1
        self.assertEqual(test, expected)

    def test_close_strat_should_stay_positions(self):
        obj = strategy.Strategy(2, 5, "2022-12-02", 90.0)
        test = obj.close_strat()
        expected = 0
        self.assertEqual(test, expected)
