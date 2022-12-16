import datetime
import logging
from dateutil.relativedelta import relativedelta


class Strategy:
    def __init__(self, open_positions, options_chain, num_open_positions, min_dte, date, absolute_profit=None, relative_profit=None, open_for=None):
        self.open_positions = open_positions
        self.options_chain = options_chain
        self.today_dt = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        self.date = date

    def get_min_dte(self):
        min_dte = min(
            [(datetime.datetime.strptime(el.expiration, "%Y-%m-%d").date() - self.today_dt).days
             for el in self.open_positions],
            default=-1)
        return min_dte

    def get_position_metrics(self):
        revenue = 0
        volume = 0
        position_open_for = 0
        for el in self.open_positions:
            strike = el.strike
            expiration = el.expiration
            price = el.open_price
            amount = el.amount
            open_at = el.open_at
            position_open_for = max(position_open_for, (self.today_dt - datetime.datetime.strptime(open_at, "%Y-%m-%d").date()).days)
            current_price = self.get_current_price(expiration=expiration, strike=strike)
            revenue_item = amount * (current_price - price)
            volume_item = price * amount
            volume = volume + volume_item
            revenue = revenue + revenue_item
        relative_rev = revenue / volume if volume > 0 else 0
        min_dte = self.get_min_dte()
        message = f"""Date: {self.date}, revenue: {round(revenue, 2)}, volume: {round(volume,2)}, relative_revenue: {round(relative_rev,2)}, dte: {min_dte}, open_for: {position_open_for}"""
        logging.info(message)
        return revenue, volume, position_open_for

    def get_current_price(self, expiration, strike):
        current_price = 0
        try:
            current_price = self.options_chain[(expiration, strike)][0]
        except:
            print("options hasn't found")
        return current_price


    def open_strat(self):
        nearest_expirations = self.get_expirations()
        if (self.num_open_positions == 0 and
                int(nearest_expirations[0][1].days) >= 13):
            return 1
        else:
            return 0

    def close_strat(self):
        if (self.num_open_positions > 0 and self.relative_profit > 0.9):
            return 1
        elif (self.open_for > 8 and self.relative_profit < -0.2):
            return 1
        elif (self.num_open_positions > 0 and self.relative_profit > .5 and self.min_dte < 9):
            return 1
        elif (self.num_open_positions > 0 and self.min_dte < 6):
            return 1
        else:
            return 0

    def get_expirations(self):
        expirations = []
        init_date = datetime.datetime.strptime(self.date, "%Y-%m-%d").date()
        for i in range(2):
            new_date = init_date + relativedelta(months=i)
            year = new_date.year
            month = new_date.month
            third = datetime.date(year, month, 15)
            # What day of the week is the 15th?
            w = third.weekday()
            # Friday is weekday 4
            if w != 2:
                # Replace just the day (of month)
                third = third.replace(day=(15 + (4 - w) % 7))
            expirations.append((third, third - init_date))
        return expirations
