from datetime import datetime
import random
import unittest

import mock

from market_tool.database import StockDatabase
from tests import utils


class TestCoefficient(unittest.TestCase):
    @mock.patch("pandas_datareader.data.DataReader")
    def test_coefficient(self, mock_datareader):
        start = datetime(2017, 5, 8)
        end = datetime(2017, 5, 12)
        instance = mock_datareader.return_value

        symbol = utils.random_string()


        fake_values = []
        for count in range(1, 11):
            high = random.uniform(2.5, 10.2)
            low = random.uniform(1.7, 22.4)
            openy = random.uniform(22.1, 92.7)
            close = random.uniform(102.3, 107.4)
            volume = random.randint(0, 100)
            date = datetime(2014, 1, count)
            fake_values.append((utils.PandasDatetimeMock(date.strftime('%Y-%m-%d')),
                                utils.PandaStockMock(high, low, openy, close, volume)))
        instance.iterrows.return_value = fake_values

        db_schema = {
            'sqlite' : {
                'database_file' : None,
            },
        }

        db = StockDatabase(db_schema)
        db.stock_update(symbol, start, end)

        results = db.stock_coefficient_determination()
        self.assertEqual(len(results), 1)
