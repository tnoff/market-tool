import json
import unittest

import httpretty

from market_tool import urls
from market_tool.database import StockDatabase

from tests.data import historical, lookup

class TestDatabase(unittest.TestCase):

    @httpretty.activate
    def test_historical(self):
        data = {
            'Normalized' : False,
            'DataPeriod' : 'Day',
            'Elements' : [
                {
                    'Symbol' : 'XYZ',
                    'Type' : 'price',
                    'Params' : ['c'],
                },
            ],
            'NumberOfDays' : 10,
        }
        url = "%sjson?parameters=%s" % (urls.STOCK_HISTORICAL_URL, json.dumps(data))
        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(historical.DATA))
        symbol = "xyz"
        url = "%sjson?input=%s" % (urls.STOCK_LOOKUP_URL, symbol)
        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(lookup.DATA))
        database = StockDatabase()
        database.stock_update(10, ["xyz"])

        stock, prices = database.stock_get_prices("xyz")
        self.assertEqual(len(prices), 10)
        self.assertEqual(stock['stock_symbol'], 'xyz')

        # Run update again to check for integrity errors
        url = "%sjson?parameters=%s" % (urls.STOCK_HISTORICAL_URL, json.dumps(data))
        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(historical.DATA))
        symbol = "xyz"
        url = "%sjson?input=%s" % (urls.STOCK_LOOKUP_URL, symbol)
        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(lookup.DATA))
        database.stock_update(10, ["xyz"])
