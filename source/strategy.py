import datetime
import logging
from dateutil.relativedelta import relativedelta
from source.utils import *

class Strategy:
    def __init__(self, open_positions, instrument_data, timestamp):
        self.open_positions = open_positions
        self.options_chain = instrument_data
        self.timestamp = convert_timestamp_to_datetime(int(timestamp))
        self.timestamp_str = timestamp

    def get_min_dte(self):
        min_dte = min(
            [(convert_string_to_datetime(el.expiration, dateFormats.ddmmyyyy_point) - self.timestamp).days
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
            position_open_for = max(position_open_for, (int(self.timestamp_str) - int(open_at)))
            current_price = self.get_current_price(expiration=expiration, strike=strike)
            revenue_item = amount * (current_price - price)
            volume_item = price * amount
            volume = volume + volume_item
            revenue = revenue + revenue_item
        relative_rev = revenue / volume if volume > 0 else 0
        min_dte = self.get_min_dte()
        message = f"""Date: {self.timestamp_str}, revenue: {round(revenue, 2)}, volume: {round(volume, 2)}, relative_revenue: {round(relative_rev, 2)}, dte: {min_dte}, open_for: {position_open_for}"""
        logging.info(message)
        return revenue, volume, position_open_for

    def get_current_price(self, expiration, strike):
        current_price = 0
        try:
            current_price = self.options_chain[(expiration, str(strike))][0]
        except:
            print("options hasn't found")
        return current_price

    def get_num_open_positions(self):
        return len(self.open_positions)

    def get_expirations_depr(self):
        expirations = []
        init_date = self.timestamp
        for i in range(2):
            new_date = init_date + relativedelta(months=i)
            year = new_date.year
            month = new_date.month
            third = datetime.datetime(year, month, 15, tzinfo=datetime.timezone.utc)
            # What day of the week is the 15th?
            w = third.weekday()
            # Friday is weekday 4
            if w != 2:
                # Replace just the day (of month)
                third = third.replace(day=(15 + (4 - w) % 7))
            expirations.append((third, third - init_date))
        return expirations
