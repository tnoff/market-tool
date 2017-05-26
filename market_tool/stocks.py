from datetime import datetime

import pandas_datareader.data

from market_tool.exceptions import MarketToolException
from market_tool import utils

COLUMNS = ["High", "Close", "Open", "Low", "Volume"]

def historical_data(stock_symbol, start_date, end_date, source="google", number_decimals=2):
    '''
    Use pandas to get stock/etf stock price information

    stock_symbols       :       Single stock symbol to lookup
    start_date          :       Start time for stock prices, uses python datetime object
    end_date            :       End time for stock prices, uses python datetime object
    source              :       Source for stock info, one of "google" or "yahoo"
    '''
    # Check data inputs
    if source not in ["google", "yahoo"]:
        raise MarketToolException("Invalid source type:%s" % source)

    if not isinstance(start_date, datetime):
        raise MarketToolException("Invalid start date type:%s" % start_date)

    if not isinstance(end_date, datetime):
        raise MarketToolException("Invalid start date type:%s" % end_date)

    try:
        data = pandas_datareader.data.DataReader(stock_symbol.lower(), source, start_date, end_date)
    except pandas_datareader._utils.RemoteDataError: #pylint:disable=protected-access
        return []

    return_data = []
    for time, row_data in data.iterrows():
        dict_data = {
            'datetime' : time.to_pydatetime(),
        }
        for column in COLUMNS:
            value = utils.round_decimal(getattr(row_data, column), number_decimals)
            dict_data[column.lower()] = value
        return_data.append(dict_data)
    return return_data
