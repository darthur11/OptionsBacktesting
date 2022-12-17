from source.strategy import Strategy
from source.models.positions import InstrumentInfo

class VolatilityHedgeStrategy(Strategy):
    def open_strat(self):
        num_open_positions = self.get_num_open_positions()
        nearest_expirations = self.get_expirations()
        if (num_open_positions == 0 and int(nearest_expirations[0][1].days) >= 13):
            return 1
        else:
            return 0

    def close_strat(self):
        num_open_positions = self.get_num_open_positions()
        revenue, volume, position_open_for = self.get_position_metrics()
        relative_profit = revenue / volume if volume > 0 else 0
        if (num_open_positions > 0 and relative_profit > 0.9):
            return 1
        elif (position_open_for > 8 and relative_profit < -0.2):
            return 1
        elif (num_open_positions > 0 and relative_profit > .5 and self.get_min_dte() < 9):
            return 1
        elif (num_open_positions > 0 and self.get_min_dte() < 6):
            return 1
        else:
            return 0

    def get_instruments_for_strategy(self, cash_available):
        first_leg, second_leg = [], []
        expirations = self.options_chain.items()
        try:
            first_leg = [con for con in expirations if (con[1][2] == 1 and con[1][3] == 1)][0]
            print("first leg: ", first_leg)
        except:
            print("no first leg")
        try:
            second_leg = [con for con in expirations if (con[1][2] == 1 and con[1][3] == 2)][0]
            print("second leg: ", second_leg)
        except:
            print("no second leg")

        if len(first_leg) > 0 and len(second_leg) > 0:
            amount = round(0.2 * cash_available / (-first_leg[1][0] + second_leg[1][0]), -3)
            print(amount)

            instrument1 = InstrumentInfo(
                ticker="VIX",
                strike=first_leg[0][1],
                expiration=first_leg[0][0],  # .strftime('%Y-%m-%d'),
                put_call="C",
                amount=-amount,
                open_price=first_leg[1][0]
            )
            instrument2 = InstrumentInfo(
                ticker="VIX",
                strike=second_leg[0][1],
                expiration=second_leg[0][0],  # .strftime('%Y-%m-%d'),
                put_call="C",
                amount=amount,
                open_price=second_leg[1][0]
            )
            return [instrument1, instrument2]
        else:
            return []