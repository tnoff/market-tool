import json
import unittest

import httpretty

from market_tool import stocks, urls

from tests.data import historical, lookup, quote

class TestStocks(unittest.TestCase):
    @httpretty.activate
    def test_lookup(self):
        symbol = "xyz"
        url = "%sjson?input=%s" % (urls.STOCK_LOOKUP_URL, symbol)
        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(lookup.DATA))
        data = stocks.lookup_resource(symbol)
        self.assertEqual(data, lookup.DATA)

    @httpretty.activate
    def test_quote(self):
        symbol = "xyz"
        url = "%sjson?symbol=%s" % (urls.STOCK_QUOTE_URL, symbol)
        httpretty.register_uri(httpretty.GET, url,
                               body=json.dumps(quote.DATA))
        data = stocks.current_quote(symbol)
        self.assertEqual(data, quote.DATA)

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
        data = stocks.historical_data(False, 'Day', ['xyz'], 'price', 'c', number_of_days=10)
        self.assertEqual(data, historical.DATA)
