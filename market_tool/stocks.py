import argparse
import json

import requests

from market_tool import urls

def parse_args():
    p = argparse.ArgumentParser(description="Stock API Interface")
    sub = p.add_subparsers(description="Module", dest="module")

    lookup = sub.add_parser("lookup", help="Lookup Stock Info")
    lookup.add_argument("stock", help="Company name or symbol")

    quote = sub.add_parser("quote", help="Get a Current Stock Quote")
    quote.add_argument("stock_symbol", help="Comapny Symbol")

    historical = sub.add_parser("historical", help="Get Historical Quote Info")
    historical.add_argument("--symbols", nargs="+", required=True,
                            help="Stock symbols")
    historical.add_argument("--data-type", choices=["price", "volume", "sma"],
                            required=True, help="Data type to return")
    historical.add_argument("--data-param", choices=["o", "h", "l", "c"],
                            required=True,
                            help="Return data param for data type: (o)pen, (h)igh"
                                 ", (l)ow, and (c)lose")
    historical.add_argument('--normalized', action="store_true",
                            help="If set, show percentages, if not set, show price units")
    historical.add_argument('--data-period', required=True,
                            choices=["Minute", "Hour", "Day",
                                     "Week", "Month", "Quarter", "Year"],
                            help="Data period for return data")
    historical.add_argument('--start-date', help="Start date for return data, only for interday requests")
    historical.add_argument('--end-date', help="End date for return data, only for interday requests")
    historical.add_argument('--end-day-offset', type=int,
                            help="Number of days back return data should end")
    historical.add_argument('--number-of-days', type=int,
                            help="Number of days that should be shown in return data, only for intraday requests")


    return vars(p.parse_args())

def lookup_resource(stock_symbol):
    url = "%sjson?input=%s" % (urls.STOCK_LOOKUP_URL, stock_symbol)
    req = requests.get(url)
    return json.loads(req.text)

def _lookup_resource(arguments):
    return lookup_resource(arguments["stock"])

def current_quote(stock_symbol):
    url = "%sjson?symbol=%s" % (urls.STOCK_QUOTE_URL, stock_symbol)
    req = requests.get(url)
    return json.loads(req.text)

def _current_quote(arguments):
    return current_quote(arguments["stock_symbol"])

def historical_data(normalized, data_period, stock_symbols, data_type, data_param,
                    start_date=None, end_date=None, end_day_offset=None,
                    number_of_days=None):
    data = {
        "Normalized" : normalized,
        "DataPeriod" : data_period,
        "Elements" : [],
    }
    for stock in stock_symbols:
        data["Elements"].append({
            "Symbol" : stock,
            "Type" : data_type,
            "Params" : [data_param],
        })
    optional_args = {
        'StartDate' : start_date,
        'EndDate' : end_date,
        'EndOffsetDays' : end_day_offset,
        'NumberOfDays' : number_of_days,
    }
    for key, value in optional_args.items():
        if value is not None:
            data[key] = value

    url = "%sjson?parameters=%s" % (urls.STOCK_HISTORICAL_URL, json.dumps(data))
    req = requests.get(url)

    historical_data = json.loads(req.text)

    # Data returned meant to be used directly for graphing
    # Dont care about key/values specifically for graphing
    historical_data.pop("Positions", None)
    historical_data.pop("Labels", None)

    return historical_data

def _historical_data(arguments):
    return historical_data(arguments["normalized"],
                           arguments["data_period"],
                           arguments["symbols"],
                           arguments["data_type"],
                           arguments["data_param"],
                           start_date=arguments["start_date"],
                           end_date=arguments["end_date"],
                           end_day_offset=arguments["end_day_offset"],
                           number_of_days=arguments["number_of_days"])
COMMAND_HASH = {
    "lookup" : _lookup_resource,
    "quote" : current_quote,
    "historical" : _historical_data,
}

def main():
    args = parse_args()
    method = COMMAND_HASH[args["module"]]
    print json.dumps(method(args), indent=4)

if __name__ == '__main__':
    main()
