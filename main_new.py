import csv
import datetime
import math

from source.black_scholes import BlackScholes
from source.models.positions import Position, StrategyPosition, InstrumentInfo
from source.portfolio import Portfolio
from source.strategy import Strategy

import matplotlib.pyplot as plt
import pandas as pd

def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def show_chart(dates, y_axis):
    fig = plt.figure(figsize=(3, 6))
    data = pd.DataFrame({'period':dates, 'cash':y_axis})
    data['period'] = pd.to_datetime(data['period'])
    data.plot.line(x='period', y='cash', linewidth=.5, style='-')
    plt.savefig('./resources/temp.png', dpi=250)

def show_chart_ggplot(dates, y_axis):
    from plotnine import ggplot, aes, geom_line, theme_minimal, geom_point, labs, scale_x_datetime
    data = pd.DataFrame({'period': dates, 'cash': y_axis})
    data['period'] = pd.to_datetime(data['period'])
    myPlot = (
            ggplot(data) +
            aes(x="period", y="cash", group = "1") +
            scale_x_datetime(date_breaks="1 month") +
            geom_line() +
            geom_point() +
            theme_minimal()
    )
    myPlot.save("./resources/myplot.png", dpi=600)


def itertuples_impl(df):
  return pd.Series(
    row.cash if row.diff == True else None
    for row in df.itertuples()
  )

def show_chart_plotly(dates, y_axis):
    import plotly.express as px
    import plotly.graph_objects as go
    data = pd.DataFrame({'period': dates, 'cash': y_axis})
    data.to_csv("./resources/for_chart_data.csv")
    data['period'] = pd.to_datetime(data['period'])
    data['diff'] = (data.cash - data.cash.shift(1) != 0)
    data['movement'] = itertuples_impl(data)
    print(data)
    fig1 = px.line(data, x='period', y='cash')

    fig2 = px.scatter(data, x='period', y='movement', color_discrete_sequence=['red'], size_max=3.5)
    fig2.update_traces(marker={'size': 7.5})
    layout = go.Layout(
        title='Cash account value',
        xaxis=dict(
            title = 'period',
            dtick="M1",
            tickformat="%b %Y",
            linecolor='#636363',
            linewidth=2,
        ),
        yaxis=dict(
            title='Cash',
            zeroline=True,
            showline=True,
            dtick=100000,
            tick0 = 50000,
            tickformat = 'B',
            linecolor = '#636363',
            linewidth = 2,
        )
    )
    fig3 = go.Figure(data=fig1.data + fig2.data, layout=layout)
    fig3.write_image("./resources/plotly.png", width = 2000, height = 1500)


def read_input_dataset():
    output = {}
    dates = []
    "quote_date", "underlying_last", "expire_date", "dte", "strike", "c_mid", "p_mid", "rn_buy", "rn_expiration", "strike_distance_pct"
    with open(f'./resources/VIX_options_.csv', 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i > 0:
                date = row[0]
                underlying = float(row[1])
                expire_date = row[2]
                strike = int(round(float(row[4])))
                key = (expire_date, strike)
                value = (float(row[5]), float(row[6]), int(row[7]), int(row[8]), float(row[9]))
                if not(date in output.keys()):
                    output.update({date: {key: value}})
                else:
                    output[date][key] = value
    dates_fin = list(output.keys())
    dates_fin.sort()
    return output, dates_fin


if __name__ == '__main__':
    init_cash_position = 100000
    r = 0.03
    print("Init portfolio.....")
    portfolio = Portfolio(init_cash_position=init_cash_position)
    print("Read input dataset:")
    input, dates = read_input_dataset()
    print(len(dates))
    str_dates = []
    for row in dates:
        str_dates.append(str(row))
    dates_fo_plot = []
    print("Move through each day to decide what's next")
    for row in str_dates:
        num_open_positions = len(portfolio.open_positions)
        today_str = str(row)
        today_dt = datetime.datetime.strptime(str(row), "%Y-%m-%d").date()

        min_dte = min(
            [(datetime.datetime.strptime(el.expiration, "%Y-%m-%d").date() - today_dt).days
             for el in portfolio.open_positions],
            default=-1)
        revenue = 0
        volume = 0
        for el in portfolio.open_positions:
            strike = el.strike
            expiration = el.expiration
            price = el.open_price
            amount = el.amount
            put_call = el.put_call
            current_price = 0
            try:
                current_price = input[row][(expiration, strike)][0]
            except:
                print("options hasn't found")

            #bs = BlackScholes(K=strike, S=row[4], r=r, T_start=row[0], T_end=expiration, sig=row[6])
            #current_price = bs.get_price(put_call)
            revenue_item = amount * (current_price - price)
            volume_item = price * amount
            volume = volume + volume_item
            revenue = revenue + revenue_item
        relative_rev = revenue / volume if volume > 0 else 0

        strat = Strategy(num_open_positions, min_dte, today_str, revenue, relative_rev)
        if (strat.open_strat()):
            expirations = input[row].items()
            try:
                first_leg = [con for con in expirations if (con[1][2] == 1 and con[1][3] == 1)][0]
            except:
                print("no first leg")
            try:
                second_leg = [con for con in expirations if (con[1][2] == 1 and con[1][3] == 2)][0]
            except:
                print("no second leg")
            print("first leg: ", first_leg)
            print("second leg: ", second_leg)
            if len(first_leg)>0 and len(second_leg)>0:
                amount = round(0.2 * portfolio.accounts['cash'] / (-first_leg[1][0] + second_leg[1][0]),-3)
                print(amount)

                instrument1 = InstrumentInfo(
                    ticker="VIX",
                    strike=first_leg[0][1],
                    expiration=first_leg[0][0],#.strftime('%Y-%m-%d'),
                    put_call="C",
                    amount=-amount,
                    open_price=first_leg[1][0]
                )
                instrument2 = InstrumentInfo(
                    ticker="VIX",
                    strike=second_leg[0][1],
                    expiration=second_leg[0][0],#.strftime('%Y-%m-%d'),
                    put_call="C",
                    amount=amount,
                    open_price=second_leg[1][0]
                )
                # Open strategy position:
                portfolio.open_strategy_position([instrument1, instrument2], open_at=today_str)
            else:
                print("one or more leg is not here")

        if (strat.close_strat()):
            get_mapping_id_strategy = portfolio.get_mapping_id_strategy_id()
            for id_strategy_map in get_mapping_id_strategy:
                for id in id_strategy_map['ids']:
                    array_position = portfolio.find_relevant_positions_by_id(id)
                    position = portfolio.open_positions[array_position]
                    strike = position.strike
                    expiration = position.expiration
                    price = position.open_price
                    amount = position.amount
                    put_call = position.put_call
                    liquidation_price = 0
                    try:
                        liquidation_price = input[row][(expiration, strike)][0]
                    except:
                        print("options hasn't found")

                    #bs = BlackScholes(K=strike, S=row[4], r=r, T_start=today_str, T_end=expiration, sig=row[6])
                    portfolio.close_position(id=id, liquidation_price=liquidation_price, closed_at=today_str)

        portfolio.accounts_snapshot.append(portfolio.accounts['cash'])
        dates_fo_plot.append(today_dt)
    print(portfolio.accounts_snapshot)
    import dataclasses
    with open("./resources/portfolio.csv", "w") as p:
        writer = csv.writer(p)
        writer.writerow([str(field.name) for field in dataclasses.fields(Position)])
        for row in portfolio.closed_positions:
            writer.writerow(dataclasses.astuple(row))
    print(portfolio.open_positions)
    #show_chart(dates_fo_plot, portfolio.accounts_snapshot)
    show_chart_plotly(dates_fo_plot, portfolio.accounts_snapshot)
