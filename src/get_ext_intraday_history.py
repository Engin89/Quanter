#!/bin/sh
import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries
import time
import sys
import json
import logging
from kafka import KafkaProducer
from utils.util_functions import myconverter, openloghistory, replaceloghistory, get_keys

"""
This script feeds extended intraday data from Alpha Vantage to Elasticsearch. You need wait for the kafka-connect is up and running. 
"""


logging.basicConfig(level=logging.INFO)
sys.path.append('../data')
sys.path.append('/utils')

tickers = pd.read_csv('../data/nasdaq_screener_1621413935960.csv')[['Symbol',
                                                                    'Name',
                                                                    'Country',
                                                                    'IPO Year',
                                                                    'Sector',
                                                                    'Industry',
                                                                    'Market Cap']]
tickers = tickers[(tickers['IPO Year'] < 2015) &
                  (tickers['Country'] == 'United States') &
                  (tickers['Market Cap'] > 10e8)]

symbols = tickers[tickers['Industry'].isin(tickers.Industry.value_counts()[lambda x: x > 5].index)]['Symbol'].tolist()

# Historical Prices
return_dict = {}
price_dict = {}
# TODO: Make it functional, maybe too much data storing here

start, end = openloghistory()
apikey, api_url = get_keys()

for sym in symbols[start:end]:
    symbol = sym
    test_df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])

    for i in range(1, 3):
        for j in range(1, 13):
            ts = TimeSeries(key=apikey, output_format='csv')
            totalData = ts.get_intraday_extended(symbol=symbol, interval='15min', slice=f'year{i}month{j}')
            test_data = pd.DataFrame(list(totalData[0]))
            cols = test_data.iloc[0].values.tolist()
            test_data.columns = cols
            temp = test_data.iloc[1:]
            test_df = test_df.append(temp)
            time.sleep(20)  # Alpha Vantage free version has threshold of 5 API calls per minute!!!

    test_df = test_df.set_index('time')
    test_df = test_df.apply(pd.to_numeric)
    test_df = test_df.sort_index(ascending=True)
    test_df = test_df.reset_index()
    test_df['time'] = pd.to_datetime(test_df['time'])
    price_dict[f'{sym}'] = test_df.set_index('time')
    test_df['next_time'] = test_df['time'] + pd.offsets.DateOffset(years=1)
    next_df = test_df.loc[:, 'open': 'next_time']
    test_df = test_df.drop(columns='next_time')
    next_df = next_df.rename(columns={'next_time': 'time',
                                      'high': 'prev_high',
                                      'open': 'prev_open',
                                      'low': 'prev_low',
                                      'close': 'prev_close',
                                      'volume': 'prev_volume'})

    return_df = test_df.merge(next_df, on='time')
    return_df['yoy_return_open'] = return_df['open'] / return_df['prev_open'] - 1
    return_dict[f'{sym}'] = return_df[['time', 'yoy_return_open']]
    print(f'{sym} extended data collected')


# TODO: Decouple the Return Calculations and Embed the Mean Variance Opt (see notebook for the code)
ix = np.argmax(np.array(map(lambda x: x.shape[0], return_dict)))
returns_df = return_dict[list(return_dict.keys())[ix]]
returns_df = returns_df.rename(columns={'yoy_return_open': list(return_dict.keys())[ix]})
for k, v in return_dict.items():
    if k != list(return_dict.keys())[ix]:
        v = v.rename(columns={'yoy_return_open': k})
        returns_df = returns_df.merge(v, on='time')

returns_df = returns_df.set_index('time')

# Produce Data to Kafka Topic, Kafka-Connect will deliver it to the Elasticsearch Index, each ticker has its own index.
producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda m: json.dumps(m, default=myconverter).encode('ascii'))

for k, v in price_dict.items():
    topic = k
    for index, row in v.reset_index().iterrows():
        producer.send(topic, row.to_dict())

replaceloghistory(start, end)
