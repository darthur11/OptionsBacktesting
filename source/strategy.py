import datetime
from dateutil.relativedelta import relativedelta


class Strategy:
    def __init__(self,
                 num_open_positions,
                 min_dte,
                 date,
                 absolute_profit=None,
                 relative_profit=None):
        self.num_open_positions = num_open_positions
        self.min_dte = min_dte
        self.date = date
        self.absolute_profit = absolute_profit
        self.relative_profit = relative_profit

    def open_strat(self):
        nearest_expirations = self.get_expirations()
        if (self.num_open_positions == 0 and
                int(nearest_expirations[0][1].days) >= 13):
            return 1
        else:
            return 0

    def close_strat(self):
        if (self.num_open_positions > 0
                and self.min_dte < 7
                and self.absolute_profit > 100):
            return 1
        elif (self.num_open_positions > 0 and self.min_dte < 3):
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
            if w != 4:
                # Replace just the day (of month)
                third = third.replace(day=(15 + (4 - w) % 7))
            expirations.append((third, third - init_date))
        return expirations
