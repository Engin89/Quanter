#!/bin/sh
import pandas as pd
import sys
import os
import logging
import subprocess
from utils.util_functions import openloghistory

logging.basicConfig(level=logging.INFO)
sys.path.append('../data')

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

# You need label loghistory data with * then the process runs automatically.
start, end = openloghistory()

if not os.path.exists('changeTopic.sh'):
    os.chdir("..")

subprocess.call("./changeTopic.sh '%s' '%s'" % ('test-elasticsearch-sink',
                                                ','.join(symbols[start:end])), shell=True)
