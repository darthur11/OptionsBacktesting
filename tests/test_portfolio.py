import unittest
from unittest import TestCase

from source import portfolio
from source.models import positions


class TestPortfolio(TestCase):
    init_cash = 1000
    obj = portfolio.Portfolio(init_cash)
    instrument = positions.InstrumentInfo(
        ticker='CIX',
        expiration='2022-12-16',
        strike=30,
        put_call='C',
        amount=2,
        open_price=4.5
    )
    instrument2 = positions.InstrumentInfo(
        ticker='CIX',
        expiration='2023-01-15',
        strike=31,
        put_call='C',
        amount=2,
        open_price=3.5
    )

    def test_generate_open_position(self):
        position_to_insert = self.obj.generate_open_position(self.instrument)
        self.assertEqual(self.instrument.ticker, position_to_insert.ticker)
        self.assertEqual(self.instrument.expiration,
                         position_to_insert.expiration)
        self.assertEqual(self.instrument.strike, position_to_insert.strike)
        self.assertEqual(self.instrument.put_call, position_to_insert.put_call)
        self.assertEqual(self.instrument.open_price, position_to_insert.open_price)
        self.assertEqual(self.instrument.amount, position_to_insert.amount)

    def test_generate_strategy_open_position_same_strategy(self):
        positions = self.obj.generate_open_strategy_position(
            [self.instrument, self.instrument2])
        self.assertEqual(positions[0].strategy_id, positions[1].strategy_id)

    def test_generate_strategy_open_position_elements_correctly_mapped(self):
        positions = self.obj.generate_open_strategy_position(
            [self.instrument, self.instrument2])
        self.assertEqual(positions[0].ticker, self.instrument.ticker)
        self.assertEqual(positions[0].expiration, self.instrument.expiration)
        self.assertEqual(positions[0].strike, self.instrument.strike)
        self.assertEqual(positions[0].put_call, self.instrument.put_call)
        self.assertEqual(positions[0].amount, self.instrument.amount)
        self.assertEqual(positions[0].open_price, self.instrument.open_price)
        self.assertEqual(positions[1].ticker, self.instrument2.ticker)
        self.assertEqual(positions[1].expiration, self.instrument2.expiration)
        self.assertEqual(positions[1].strike, self.instrument2.strike)
        self.assertEqual(positions[1].put_call, self.instrument2.put_call)
        self.assertEqual(positions[1].amount, self.instrument2.amount)
        self.assertEqual(positions[1].open_price, self.instrument2.open_price)

    def test_change_position_1_buy(self):
        print(self.obj.accounts)
        instrument = positions.InstrumentInfo(
            ticker='VIX',
            expiration='2022-12-16',
            strike=30,
            put_call='C',
            amount=2,
            open_price=4.5
        )
        self.obj.open_position(instrument)
        remaining_cash = self.init_cash - instrument.amount * instrument.open_price
        print(self.obj.accounts)
        self.assertEqual(remaining_cash, self.obj.accounts['cash'])
        self.assertEqual(instrument.amount,
                         self.obj.accounts['options'][0].amount)


    def test_change_position_1_sell(self):
        print("test_change_position_1_sell")
        init_cash = 1000
        init_portfolio = portfolio.Portfolio(init_cash)
        print(init_portfolio.accounts)
        instrument = positions.InstrumentInfo(
            ticker='VIX',
            expiration='2022-12-16',
            strike=30,
            put_call='C',
            amount=-2,
            open_price=4.5
        )
        init_portfolio.open_position(instrument)
        print(init_portfolio.accounts)
        remaining_cash = init_cash - instrument.amount * instrument.open_price
        print(init_portfolio.accounts)
        self.assertEqual(remaining_cash, init_portfolio.accounts['cash'])
        self.assertEqual(instrument.amount, init_portfolio.accounts['options'][0].amount)


    def test_change_positions_close_should_correctly_change_balance(self):
        """
        Init portfolio, add instrument then change balance assuming we close
        position. Should correctly calculate final cash balance
        """
        init_cash = 1000
        init_portfolio = portfolio.Portfolio(init_cash)
        print("Init balances: \n", init_portfolio.accounts)
        initial_cash = init_portfolio.accounts['cash']
        instrument = positions.InstrumentInfo(
            ticker='MIX',
            expiration='2022-12-16',
            strike=30,
            put_call='C',
            amount=2,
            open_price=4.5
        )
        init_portfolio.open_position(instrument)  # Decrease cash on 2*4.5 = 9
        print("Open positions: \n", init_portfolio.open_positions)
        print("Balance after changes: \n", init_portfolio.accounts) # Show balances
        init_portfolio.change_positions_close(14.5, instrument) # Increase cash on 2*14.5 = 29
        expected_cash = initial_cash - 9 + 29
        test_cash = init_portfolio.accounts['cash']
        print("Final balance: \n", init_portfolio.accounts)
        self.assertEqual(test_cash, expected_cash)


    def test_change_positions_close_should_correctly_change_balance_short(self):
        """
        Init portfolio, add instrument then change balance assuming we close
        position. Should correctly calculate final cash balance
        """
        init_cash = 1000
        init_portfolio = portfolio.Portfolio(init_cash)
        print("Init balances: \n", init_portfolio.accounts)
        initial_cash = init_portfolio.accounts['cash']
        instrument = positions.InstrumentInfo(
            ticker='MIX',
            expiration='2022-12-16',
            strike=30,
            put_call='C',
            amount=-2,
            open_price=4.5
        )
        init_portfolio.open_position(instrument)  # Increase cash on 2*4.5 = 9
        print("Open positions: \n", init_portfolio.open_positions)
        print("Balance after changes: \n", init_portfolio.accounts) # Show balances
        init_portfolio.change_positions_close(1.5, instrument) # Decrease cash on 2*1.5 = 3
        expected_cash = initial_cash + 9 - 3
        test_cash = init_portfolio.accounts['cash']
        print("Final balance: \n", init_portfolio.accounts)
        self.assertEqual(test_cash, expected_cash)


    def test_close_position(self):
        """
        Init portfolio, open position then close the position.
        Should correctly calculate final cash balance
        """
        init_cash = 1000
        init_portfolio = portfolio.Portfolio(init_cash)
        print("Init balances: \n", init_portfolio.accounts)
        initial_cash = init_portfolio.accounts['cash']
        instrument = positions.InstrumentInfo(
            ticker='MIX',
            expiration='2022-12-16',
            strike=30,
            put_call='C',
            amount=2,
            open_price=4.5
        )
        init_portfolio.open_position(instrument)  # Decrease cash on 2*4.5 = 9
        print("Open positions: \n", init_portfolio.open_positions)
        print("Closed positions: \n", init_portfolio.closed_positions)
        print("Balance after changes: \n", init_portfolio.accounts)
        id = init_portfolio.open_positions[0].id
        init_portfolio.close_position(id, 14.5)  # Inc cash 2*14.5 = 29
        expected_cash = initial_cash - 9 + 29
        test_cash = init_portfolio.accounts['cash']
        print("Open positions: \n", init_portfolio.open_positions)
        print("Closed positions: \n", init_portfolio.closed_positions)
        print("Final balance: \n", init_portfolio.accounts)
        expected_len_open = 0
        test_len_open = len(init_portfolio.open_positions)
        expected_len_closed = 1
        test_len_closed = len(init_portfolio.closed_positions)
        self.assertEqual(test_cash, expected_cash)
        self.assertEqual(test_len_open, expected_len_open)
        self.assertEqual(test_len_closed, expected_len_closed)


    def test_close_position_short(self):
        """
        Init portfolio, open position then close the position.
        Should correctly calculate final cash balance
        """
        init_cash = 1000
        init_portfolio = portfolio.Portfolio(init_cash)
        print("Init balances: \n", init_portfolio.accounts)
        initial_cash = init_portfolio.accounts['cash']
        instrument = positions.InstrumentInfo(
            ticker='MIX',
            expiration='2022-12-16',
            strike=30,
            put_call='C',
            amount=-2,
            open_price=4.5
        )
        init_portfolio.open_position(instrument)  # Increase cash on 2*4.5 = 9
        print("Open positions: \n", init_portfolio.open_positions)
        print("Closed positions: \n", init_portfolio.closed_positions)
        print("Balance after changes: \n", init_portfolio.accounts)
        id = init_portfolio.open_positions[0].id
        init_portfolio.close_position(id, 1.5)  # Dec cash 2*1.5 = 3
        expected_cash = initial_cash + 9 - 3
        test_cash = init_portfolio.accounts['cash']
        print("Open positions: \n", init_portfolio.open_positions)
        print("Closed positions: \n", init_portfolio.closed_positions)
        print("Final balance: \n", init_portfolio.accounts)
        expected_len_open = 0
        test_len_open = len(init_portfolio.open_positions)
        expected_len_closed = 1
        test_len_closed = len(init_portfolio.closed_positions)
        self.assertEqual(test_cash, expected_cash)
        self.assertEqual(test_len_open, expected_len_open)
        self.assertEqual(test_len_closed, expected_len_closed)

    def test_strategy_open(self):
        init_cash = 1000
        init_portfolio = portfolio.Portfolio(init_cash)
        print("Init balances: \n", init_portfolio.accounts)
        initial_cash = init_portfolio.accounts['cash']
        instrument1 = positions.InstrumentInfo(
            ticker='MIX',
            expiration='2022-12-16',
            strike=30,
            put_call='C',
            amount=-2,
            open_price=4.5
        )
        instrument2 = positions.InstrumentInfo(
            ticker='MIX',
            expiration='2023-01-15',
            strike=30,
            put_call='C',
            amount=+2,
            open_price=6.5
        )
        init_portfolio.open_strategy_position([instrument1, instrument2])
        test_num_elements = len(init_portfolio.open_positions)
        expected_num_elements = 2
        strategy_id_1 = init_portfolio.open_positions[0].strategy_id
        strategy_id_2 = init_portfolio.open_positions[1].strategy_id
        self.assertEqual(test_num_elements, expected_num_elements)
        self.assertEqual(strategy_id_1, strategy_id_2)


    def test_strategy_close(self):
        init_cash = 1000
        init_portfolio = portfolio.Portfolio(init_cash)
        print("Init balances: \n", init_portfolio.accounts)
        initial_cash = init_portfolio.accounts['cash']
        instrument1 = positions.InstrumentInfo(
            ticker='MIX',
            expiration='2022-12-16',
            strike=30,
            put_call='C',
            amount=-2,
            open_price=4.5
        )
        instrument2 = positions.InstrumentInfo(
            ticker='MIX',
            expiration='2023-01-15',
            strike=30,
            put_call='C',
            amount=+2,
            open_price=6.5
        )
        instrument3 = positions.InstrumentInfo(
            ticker='VIX',
            expiration='2023-02-15',
            strike=30,
            put_call='C',
            amount=+2,
            open_price=6.5
        )
        init_portfolio.open_strategy_position([instrument1, instrument2])
        init_portfolio.open_position(instrument3)
        from itertools import groupby
        from operator import attrgetter
        print(init_portfolio.open_positions)
        groups = groupby(init_portfolio.open_positions, attrgetter("strategy_id"))
        print(
            [{"strategy": key, "ids": [ item.id  for item in data]} for (key, data) in groups]
        )



if __name__ == '__main__':
    unittest.main()
