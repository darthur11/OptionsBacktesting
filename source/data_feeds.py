import csv

import requests

def read_input_dataset():
    output = {}
    dates = []
    "quote_date", "underlying_last", "expire_date", "dte", "strike", "c_mid", "p_mid", "rn_buy", "strike_distance_pct"
    with open(f'./resources/VIX_options_.csv', 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i > 0:
                date = row[0]
                underlying = float(row[1])
                expire_date = row[2]
                strike = int(round(float(row[3])))
                key = (expire_date, strike)
                value = (float(row[4]), float(row[5]), float(row[6]), int(row[7]), float(row[8]))
                output.update(
                    {date: {
                        'underlying_price': underlying,
                        key: value
                    }}
                )
    dates_fin = list(output.keys())
    dates_fin.sort()
    return output, dates_fin


def get_vix_data_cme():
    cme_url = "https://cdn.cboe.com/api/global/delayed_quotes/charts/historical/_VIX.json"
    req = requests.get(url=cme_url)
    return req.json()

def process_data(input_json):
    final_list = []
    for el in input_json['data']:
        row = (el['date'], el['open'], el['high'], el['low'], el['close'])
        final_list.append(row)
    return final_list

def save_csv(symbol, data, header = ('date', 'open', 'high', 'low', 'close')):
    with open(f'../resources/{symbol}.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        # write the data
        writer.writerows(data)

def add_prcnt_change(symbol):
    output = []
    with open(f'../resources/{symbol}.csv', 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        # write the header
        prev_close = 10.
        for i, row in enumerate(reader):
            if i>7000:
                diff = float(row[4]) / prev_close - 1
                output.append((row[0], float(row[1]), float(row[2]), float(row[3]), float(row[4]), diff))
                prev_close = float(row[4])
    return output

def add_std(dataset):
    final_output = []
    import statistics
    for i, val in enumerate(dataset):
        if i>250:
            std = statistics.stdev([el[5] for el in dataset][i-250:i])
            final_output.append((val[0], val[1], val[2], val[3], val[4], val[5], std))
        else:
            std = None
            final_output.append((val[0], val[1], val[2], val[3], val[4], val[5], std))
    return final_output

if __name__ == "__main__":
    #elements = get_vix_data_cme()
    #processed = process_data(elements)
    #save_csv('VIX', processed)
    dataset = add_prcnt_change("VIX")
    output = add_std(dataset)
    save_csv("VIX_processed", output, ['date', 'open', 'high', 'low', 'close', 'chng', 'std'])