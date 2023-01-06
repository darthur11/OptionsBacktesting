import csv
import datetime

import ujson
from ast import literal_eval
from source.models.positions import Position, StrategyPosition, InstrumentInfo
from source.portfolio import Portfolio
from source.volatility_hedge_strategy_call import VolatilityHedgeStrategyCall
import matplotlib.pyplot as plt
import pandas as pd
import logging
from source.utils import *

logging.basicConfig(filename='./resources/log.log', level=logging.INFO)


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
    row.total_account if abs(row.delta) > 0.01 else None
    for row in df.itertuples()
  )

def show_chart_plotly(dataset):
    import plotly.express as px
    import plotly.graph_objects as go
    data = pd.DataFrame(dataset, columns=['period', 'cash', 'open_positions'])
    data['total_account'] = data['cash'] + data['open_positions']
    data['period'] = pd.to_datetime(data['period'])
    data['delta'] = (data.total_account - data.total_account.shift(1))
    data['delta_relative'] = (data.delta / data.total_account.shift(1))
    data['movement'] = itertuples_impl(data)
    data.to_csv("./resources/for_chart_data.csv")

    drawdown, drawdown_rel = data[['delta', 'delta_relative']].agg(['min']).values[0]
    init, end = data.iloc[[1,-1], 3].values
    start_date, end_date = data.iloc[[1,-1], 0].values
    print(start_date, end_date)
    num_days = float((end_date - start_date)/10**9)/3600/24
    print(num_days)
    print(f"""Max drawdown: {drawdown}, 
Relative drawdown: {drawdown_rel}, 
Compounded growth: {end/init}, 
Monthly average growth: {(end/init) ** (30/num_days) - 1}""")



    fig1 = px.line(data, x='period', y='total_account')

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
    #"quote_date", "underlying_last", "expire_date", "dte", "strike", "c_mid", "p_mid", "rn_buy", "rn_expiration", "strike_distance_pct"
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
                    output.update({date: {"options": {key: value}, "underlying": underlying}})
                else:
                    output[date]["options"][key] = value
    dates_fin = list(output.keys())
    dates_fin.sort()
    return output, dates_fin

def read_input():
    with open("/Users/dossatayev/PycharmProjects/OptionsDataGrabber/input_data.json", 'r') as f:
        output = ujson.load(f)
    dates_fin = list(output.keys())
    dates_fin.sort()
    return output, dates_fin

if __name__ == '__main__':
    init_cash_position = 100000
    r = 0.03
    print("Init portfolio.....")
    portfolio = Portfolio(init_cash_position=init_cash_position)
    print("Read input dataset:")
    input, dates = read_input()
    print(len(dates))
    str_dates = []
    for row in dates:
        str_dates.append(str(row))
    print("Move through each day to decide what's next")

    for row in str_dates:
        today_str = str(row)
        today_dt = datetime.datetime.fromtimestamp(int(row))
        options_data = {literal_eval(k): v for k, v in input[row].items() if k!='underlying'}
        strat = VolatilityHedgeStrategyCall(portfolio.open_positions, options_data, today_str, input[row]['underlying'])
        #strat = VolatilityHedgeStrategyPut(portfolio.open_positions, input[row], today_str)
        if (strat.open_strat()):
            list_instruments = strat.get_instruments_for_strategy(portfolio.accounts['cash'])
            # Open strategy position:
            if len(list_instruments)>0:
                portfolio.open_strategy_position(list_instruments, open_at=today_str)
            else:
                print("one or more leg is not here")

        if (strat.close_strat()):
            get_mapping_id_strategy = portfolio.get_mapping_id_strategy_id()
            #print('Get mapping id strategy: ', get_mapping_id_strategy)
            for id_strategy_map in get_mapping_id_strategy:
                #print('Open positions: ', portfolio.open_positions)
                for id in id_strategy_map['ids']:
                    array_position = portfolio.find_relevant_positions_by_id(id)
                    position = portfolio.open_positions[array_position]
                    strike = position.strike
                    expiration = position.expiration
                    price = position.open_price
                    amount = position.amount
                    put_call = position.put_call
                    liquidation_price = 0
                    if strike in strat.get_available_diagonal_strikes():
                        try:
                            liquidation_price = options_data[(expiration, str(strike))][2]
                        except:
                            print("options hasn't found")

                        if liquidation_price != 0:
                            #bs = BlackScholes(K=strike, S=row[4], r=r, T_start=today_str, T_end=expiration, sig=row[6])
                            portfolio.close_position(id=id, liquidation_price=liquidation_price, closed_at=today_str)
                    else:
                        break
        portfolio.accounts_snapshot.append(
            (today_dt, portfolio.accounts['cash'], strat.get_position_metrics()[1])
        )
    #print(portfolio.accounts_snapshot)
    import dataclasses
    with open("./resources/portfolio.csv", "w") as p:
        writer = csv.writer(p)
        writer.writerow([str(field.name) for field in dataclasses.fields(Position)])
        for row in portfolio.closed_positions:
            writer.writerow(dataclasses.astuple(row))
    print(portfolio.open_positions)
    #show_chart(dates_fo_plot, portfolio.accounts_snapshot)
    show_chart_plotly(portfolio.accounts_snapshot)
