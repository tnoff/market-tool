from datetime import datetime
import random
import unittest

import mock

from market_tool import stocks, utils
from tests import utils as test_utils


class TestStocks(unittest.TestCase):
    @mock.patch("pandas_datareader.data.DataReader")
    def test_historical(self, mock_datareader):
        start = datetime(2017, 5, 8)
        end = datetime(2017, 5, 12)
        instance = mock_datareader.return_value

        symbol = test_utils.random_string()
        number_decimals = random.randint(0, 5)

        fake_values = []
        for _ in range(10):
            high = random.uniform(2.5, 10.2)
            low = random.uniform(1.7, 22.4)
            openy = random.uniform(22.1, 92.7)
            close = random.uniform(102.3, 107.4)
            volume = random.randint(0, 100)
            date = test_utils.random_date(datetime(2014, 1, 1), datetime(2015, 1, 1))
            fake_values.append((test_utils.PandasDatetimeMock(date.strftime('%Y-%m-%d')),
                                test_utils.PandaStockMock(high, low, openy, close, volume)))
        instance.iterrows.return_value = fake_values
        data = stocks.historical_data(symbol, start, end, number_decimals=number_decimals)[-1]
        self.assertEqual(data['high'],
                         utils.round_decimal(high, number_decimals))
        self.assertEqual(data['low'],
                         utils.round_decimal(low, number_decimals))
        self.assertEqual(data['close'],
                         utils.round_decimal(close, number_decimals))
        self.assertEqual(data['open'],
                         utils.round_decimal(openy, number_decimals))
        self.assertEqual(data['volume'], volume)
        self.assertEqual(data['datetime'].strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'))
