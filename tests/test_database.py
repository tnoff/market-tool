from datetime import datetime
import random
import unittest

import mock

from market_tool.database import StockDatabase
from tests import utils


class TestDatabase(unittest.TestCase):
    @mock.patch("pandas_datareader.data.DataReader")
    def test_historical(self, mock_datareader):
        start = datetime(2017, 5, 8)
        end = datetime(2017, 5, 12)
        instance = mock_datareader.return_value

        symbol = utils.random_string()


        fake_values = []
        for _ in range(10):
            high = random.uniform(2.5, 10.2)
            low = random.uniform(1.7, 22.4)
            openy = random.uniform(22.1, 92.7)
            close = random.uniform(102.3, 107.4)
            volume = random.randint(0, 100)
            date = utils.random_date(datetime(2014, 1, 1), datetime(2015, 1, 1))
            fake_values.append((utils.PandasDatetimeMock(date.strftime('%Y-%m-%d')),
                                utils.PandaStockMock(high, low, openy, close, volume)))
        instance.iterrows.return_value = fake_values

        db_schema = {
            'connection_type' : 'sqlite',
            'database_file' : None,
        }

        db = StockDatabase(db_schema)
        db.stock_update(symbol, start, end)
        # Run twice to check for integrity errors
        db.stock_update(symbol, start, end)
        prices = db.stock_show(symbol)
        self.assertEqual(len(prices), 10)
