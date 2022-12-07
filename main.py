import csv
import datetime
import math

from source.black_scholes import BlackScholes
from source.models.positions import Position, StrategyPosition, InstrumentInfo
from source.portfolio import Portfolio
from source.strategy import Strategy

#from plotnine import ggplot, aes, geom_line, ggsave, geom_point, scale_x_timedelta, labs
import matplotlib.pyplot as plt

import pandas as pd


def read_input_dataset():
    output = []
    with open(f'./resources/VIX_processed.csv', 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i > 0:
                std = row[6] if row[6] != '' else 0
                output.append((row[0], float(row[1]), float(row[2]),
                               float(row[3]), float(row[4]), float(row[5]),
                               float(std)))
    return output[251:]  # Since first 250 rows have no std


def show_chart(dates, y_axis):
    fig = plt.figure(figsize=(3, 6))
    data = pd.DataFrame({'period':dates, 'cash':y_axis})
    data['period'] = pd.to_datetime(data['period'])
    data.plot.line(x='period', y='cash', linewidth=.5, style='o')
    plt.savefig('./resources/temp.png', dpi=250)



if __name__ == '__main__':
    init_cash_position = 100000
    r = 0.03
    print("Init portfolio.....")
    portfolio = Portfolio(init_cash_position=init_cash_position)
    print("Read input dataset:")
    input = read_input_dataset()
    print(input[-20:-10])

    print("Move through each day to decide what's next")
    dates = []
    for row in input[900:]:
        num_open_positions = len(portfolio.open_positions)
        today_str = row[0]
        today_dt = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
        min_dte = min(
            [(today_dt - datetime.datetime.strptime(el.expiration, "%Y-%m-%d").date()).days
             for el in portfolio.open_positions],
            default=-1)
        revenue = 0
        volume = 0
        for el in portfolio.open_positions:
            strike = el.strike
            expiration = el.expiration
            price = el.price
            amount = el.amount
            put_call = el.put_call
            bs = BlackScholes(K=strike, S=row[4], r=r, T_start=row[0], T_end=expiration, sig=row[6])
            current_price = bs.get_price(put_call)
            revenue_item = amount * (current_price - price)
            volume_item = price * amount
            volume = volume + volume_item
            revenue = revenue + revenue_item
        relative_rev = revenue / volume if volume > 0 else 0
        strat = Strategy(num_open_positions, min_dte, today_str, revenue, relative_rev)

        # Strategy:
        if (strat.open_strat()):
            expirations = strat.get_expirations()
            bs_leg1 = BlackScholes(
                K=math.ceil(row[4]),
                S=row[4],
                r=r,
                T_start=today_str,
                T_end=expirations[0][0].strftime('%Y-%m-%d'),
                sig=row[6])
            bs_leg2 = BlackScholes(
                K=math.ceil(row[4]) - 1,
                S=row[4],
                r=r,
                T_start=today_str,
                T_end=expirations[1][0].strftime('%Y-%m-%d'),
                sig=row[6])
            instrument1 = InstrumentInfo(
                ticker="VIX",
                strike=math.ceil(row[4]),
                expiration=expirations[0][0].strftime('%Y-%m-%d'),
                put_call="P",
                amount=-2000,
                price=bs_leg1.get_price("P"),
            )
            instrument2 = InstrumentInfo(
                ticker="VIX",
                strike=math.ceil(row[4]),
                expiration=expirations[1][0].strftime('%Y-%m-%d'),
                put_call="P",
                amount=2000,
                price=bs_leg2.get_price("P")
            )
            portfolio.open_position(instrument=instrument1, open_at=today_str)
            portfolio.open_position(instrument=instrument2, open_at=today_str)

        if (strat.close_strat()):
            for el in portfolio.open_positions:
                id = el.id
                strike = el.strike
                expiration = el.expiration
                price = el.price
                amount = el.amount
                put_call = el.put_call
                bs = BlackScholes(K=strike, S=row[4], r=r,
                                  T_start=today_str,
                                  T_end=expiration,
                                  sig=row[6])
                current_price = bs.get_price(put_call)
                portfolio.close_position(id=id, liquidation_price=bs.get_price(put_call), closed_at=today_str)
        portfolio.accounts_snapshot.append(portfolio.accounts['cash'])
        dates.append(today_dt)
    print(portfolio.accounts_snapshot)
    import dataclasses
    with open("./resources/portfolio.csv", "w") as p:
        writer = csv.writer(p)
        writer.writerow([str(field.name) for field in dataclasses.fields(Position)])
        for row in portfolio.closed_positions:
            writer.writerow(dataclasses.astuple(row))
    show_chart(dates, portfolio.accounts_snapshot)

