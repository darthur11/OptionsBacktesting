import datetime

from source.strategy import Strategy
from source.models.positions import InstrumentInfo
from ast import literal_eval
from collections import Counter
import time
class VolatilityHedgeStrategyCall(Strategy):


    def open_strat(self):
        hours_to_open = tuple((4, 5, 6, 7, 8, 9))
        num_open_positions = self.get_num_open_positions()
        nearest_expirations = self.get_expirations_depr()
        hour_flag, open_positions_flag, expirations_flag = 0, 0, 0
        if self.timestamp.hour in hours_to_open:
            hour_flag = 1
        if int(nearest_expirations[0][1].days) >= 13:
            expirations_flag = 1
        if num_open_positions == 0:
            open_positions_flag = 1
        return hour_flag * expirations_flag * open_positions_flag

    def close_strat(self):
        num_open_positions = self.get_num_open_positions()
        revenue, volume, position_open_for = self.get_position_metrics()
        relative_profit = revenue / volume if volume > 0 else 0
        if (num_open_positions > 0 and relative_profit > 0.9):
            return 1
        elif (self.get_min_dte() < 10 and relative_profit < -0.5):
            return 1
        elif (position_open_for > 8 and relative_profit < -0.2):
            return 1
        elif (num_open_positions > 0 and relative_profit > .5 and self.get_min_dte() < 9):
            return 1
        elif (num_open_positions > 0 and self.get_min_dte() < 6):
            return 1
        else:
            return 0

    def get_expirations(self, x, strike):
        lst = [val[0] for val in x if val[1] == strike]
        lst.sort(key=lambda x: time.mktime(datetime.datetime.strptime(x, "%d.%m.%Y").timetuple()))
        return lst

    def get_earliest_expirations(self, input_value, strike):
        filtered = [(key, value) for (key, value) in input_value.items() if key[1] == strike]
        sorted(filtered, key=lambda x: x[1][3])
        return filtered

    def get_available_diagonal_strikes(self):
        strikes_counter = Counter([val for val in map(lambda x: x[1], self.options_chain.keys())])
        diagonal_strikes = set(
            [val for val in map(lambda x: x[0] if x[1] > 1 else None, strikes_counter.most_common(10))])
        return diagonal_strikes
    def get_instruments_for_strategy(self, cash_available):
        lst = []
        first_leg, second_leg = [], []
        #underlying = self.instrument_data['underlying']
        diagonal_strikes = self.get_available_diagonal_strikes()
        strike_first_leg, strike_second_leg, first_expiration, second_expiration = -1, -1, '', ''
        for strike in diagonal_strikes:
            if strike is not None:
                expiration_keys = self.get_expirations(self.options_chain.keys(), strike)
                first_leg = self.options_chain[(expiration_keys[0], strike)]
                second_leg = self.options_chain[(expiration_keys[1], strike)]
                #if first_leg[2] < 8.0 and second_leg[2] < 8.0:
                lst.append((strike, expiration_keys[0], first_leg, expiration_keys[1], second_leg, -first_leg[2]+second_leg[2]))
                lst.sort(key = lambda x: x[5])
        try:
            #first_leg = [con for con in expirations if (con[1][2] == 1 and con[1][3] == 1)][0]
            first_leg = lst[0][2]
            strike_first_leg = lst[0][0] if len(first_leg) > 0 else -1
            first_expiration = lst[0][1]
            #strike_first_leg = first_leg[0][1] if len(first_leg) > 0 else -1
            print("first leg: ", first_leg)
        except:
            print("no first leg")
        try:
            #second_leg = [con for con in expirations if (con[1][2] == 1 and con[1][3] == 2)][0]
            second_leg = lst[0][4]
            strike_second_leg = lst[0][0] if len(second_leg) > 0 else -1
            second_expiration = lst[0][3]
            print("second leg: ", second_leg)
            #strike_second_leg = second_leg[0][1] if len(second_leg) > 0 else -1
        except:
            print("no second leg")

        print(strike_first_leg,strike_second_leg,strike_first_leg == strike_second_leg)
        if len(first_leg) > 0 and len(second_leg) > 0 and strike_first_leg == strike_second_leg and float(strike_first_leg) > -1:
            #print(first_leg[1][0], second_leg[1][0])
            #amount = round(0.2 * cash_available / (-first_leg[1][0] + second_leg[1][0]), -3)
            if -first_leg[2] + second_leg[2] == 0:
                amount = abs(round(0.2 * cash_available / first_leg[2], -3))
            else:
                amount = abs(round(0.2 * cash_available / (-first_leg[2] + second_leg[2]), -3))
            instrument1 = InstrumentInfo(
                ticker="VIX",
                #strike=first_leg[0][1],
                #expiration=first_leg[0][0],  # .strftime('%Y-%m-%d'),
                strike=strike_first_leg,
                expiration=first_expiration,
                put_call="C",
                amount=-amount,
                #open_price=first_leg[1][0]
                open_price=first_leg[2]
            )
            instrument2 = InstrumentInfo(
                ticker="VIX",
                #strike=second_leg[0][1],
                #expiration=second_leg[0][0],  # .strftime('%Y-%m-%d'),
                strike=strike_second_leg,
                expiration=second_expiration,
                put_call="C",
                amount=amount,
                #open_price=second_leg[1][0]
                open_price=second_leg[2]
            )
            return [instrument1, instrument2]
        else:
            return []