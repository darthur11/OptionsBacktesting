import uuid
from typing import List

from source.models import positions


class Portfolio:
    def __init__(self, init_cash_position):
        self.accounts = {
            'cash': init_cash_position,
            'options': []
        }
        self.open_positions = []
        self.closed_positions = []
        self.accounts_snapshot = []
        self.strategy_mapping = {}

    def find_account(self, instrument: positions.Position):
        is_found = False
        i = 0
        account_amount = 0
        account_price = 0
        for i, element in enumerate(self.accounts['options']):
            # print("Find accs: ", i, element)
            if (element.ticker == instrument.ticker
                    and element.expiration == instrument.expiration
                    and element.strike == instrument.strike
                    and element.put_call == instrument.put_call):
                account_amount = element.amount
                account_price = element.open_price
                is_found = True
                break
        return is_found, i, account_amount, account_price

    def change_positions_open(self, instrument: positions.Position):
        is_found, i, account_amount, account_price = self.find_account(
            instrument)
        instrument_volume = instrument.amount * instrument.open_price
        cash_remaining = self.accounts['cash']
        if (is_found):
            if (instrument_volume > cash_remaining):
                print("No enough money to trade")
            else:
                total_amount = instrument.amount + account_amount
                account_volume = account_amount * account_price
                weighted_price = 0 if total_amount == 0 else (instrument_volume + account_volume) / total_amount
                print(weighted_price)
                self.accounts['options'][i].open_price = weighted_price
                self.accounts['options'][i].amount = total_amount
                self.accounts['cash'] = cash_remaining - instrument_volume
        else:
            self.accounts['cash'] = cash_remaining - instrument_volume
            self.accounts['options'].append(instrument)
        return self.accounts

    def generate_open_position(self, instrument: positions.InstrumentInfo,
                               open_at=None, strategy_id=None):
        position_to_insert = positions.Position(
            id=uuid.uuid4().hex,
            ticker=instrument.ticker,
            expiration=instrument.expiration,
            strike=instrument.strike,
            put_call=instrument.put_call,
            amount=instrument.amount,
            open_price=instrument.open_price,
            liquidation_price=None,
            open_at=open_at,
            closed_at=None,
            strategy_id=strategy_id,
            profit=None
        )
        return position_to_insert

    def open_position(self, instrument: positions.InstrumentInfo, open_at=None):
        position_to_insert = self.generate_open_position(instrument, open_at=open_at)
        self.change_positions_open(position_to_insert)
        self.open_positions.append(position_to_insert)
        return self.accounts

    def generate_open_strategy_position(self, instruments: List[positions.InstrumentInfo], open_at=None):
        strategy_id = uuid.uuid4().hex
        opened_positions = []
        for instrument in instruments:
            opened_positions.append(
                self.generate_open_position(
                    positions.InstrumentInfo(
                        ticker=instrument.ticker,
                        expiration=instrument.expiration,
                        strike=instrument.strike,
                        put_call=instrument.put_call,
                        amount=instrument.amount,
                        open_price=instrument.open_price
                    ),
                    open_at=open_at,
                    strategy_id=strategy_id,
                )
            )
        return opened_positions

    def open_strategy_position(self, instruments: List[positions.InstrumentInfo], open_at = None):
        positions = self.generate_open_strategy_position(instruments, open_at=open_at)
        for position_to_insert in positions:
            self.change_positions_open(position_to_insert)
            self.open_positions.append(
                position_to_insert
            )
        return self.accounts

    def find_relevant_positions_by_id(self, id, strategy_id=None):
        for i, element in enumerate(self.open_positions):
            if (element.id == id):
                return i
        return None

    def find_relevant_positions_by_strategy_id(self, strategy_id):
        position_numbers = []
        for i, element in enumerate(self.open_positions):
            if (element.strategy_id == strategy_id):
                position_numbers.append(i)
        return position_numbers

    def change_positions_close(self, liquidation_price, instrument: positions.Position):
        is_found, i, account_amount, account_price = self.find_account(
            instrument)
        instrument_liquidation_volume = instrument.amount * liquidation_price
        cash_remaining = self.accounts['cash']
        if (is_found):
            self.accounts['cash'] = cash_remaining + instrument_liquidation_volume
            self.accounts['options'].pop(i)
        return self.accounts

    def close_position(self, id, liquidation_price, closed_at=None, strategy_id=None):
        position_based_on_id = self.find_relevant_positions_by_id(id)
        open_position = self.open_positions[position_based_on_id]
        open_position.closed_at = closed_at
        open_position.liquidation_price = liquidation_price
        open_position.profit = (liquidation_price - open_position.open_price) * open_position.amount
        self.change_positions_close(liquidation_price, open_position)
        self.closed_positions.append(open_position)
        self.open_positions.pop(position_based_on_id)
        return self.closed_positions

    def get_mapping_id_strategy_id(self):
        from itertools import groupby
        from operator import attrgetter
        groups = groupby(self.open_positions, attrgetter("strategy_id"))
        return [{"strategy_id": key, "ids": [item.id for item in data]} for (key, data) in groups]

