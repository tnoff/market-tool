import argparse
import json

import requests

BASE_URL = "http://dev.markitondemand.com/Api/v2/"
LOOKUP_URL = "%sLookup/" % BASE_URL
QUOTE_URL = "%sQuote/" % BASE_URL
HISTORICAL_URL = '%sInteractiveChart/' % BASE_URL


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

def lookup_resource(arguments):
    url = "%sjson?input=%s" % (LOOKUP_URL, arguments["stock"])
    req = requests.get(url)
    return json.loads(req.text)

def current_quote(arguments):
    url = "%sjson?symbol=%s" % (QUOTE_URL, arguments["stock_symbol"])
    req = requests.get(url)
    return json.loads(req.text)

def historical_data(arguments):
    data = {
        "Normalized" : arguments["normalized"],
        "DataPeriod" : arguments["data_period"],
        "Elements" : [],
    }
    for stock in arguments["symbols"]:
        data["Elements"].append({
            "Symbol" : stock,
            "Type" : arguments["data_type"],
            "Params" : [arguments["data_param"]],
        })
    if arguments["start_date"] is not None:
        data["StartDate"] = arguments["start_date"]
    if arguments["end_date"] is not None:
        data["EndDate"] = arguments["end_date"]
    if arguments["end_day_offset"] is not None:
        data["EndOffsetDays"] = arguments["end_day_offset"]
    if arguments["number_of_days"] is not None:
        data["NumberOfDays"] = arguments["number_of_days"]

    url = "%sjson?parameters=%s" % (HISTORICAL_URL, json.dumps(data))
    req = requests.get(url)
    return json.loads(req.text)

COMMAND_HASH = {
    "lookup" : lookup_resource,
    "quote" : current_quote,
    "historical" : historical_data,
}

def main():
    args = parse_args()
    method = COMMAND_HASH[args["module"]]
    print json.dumps(method(args), indent=4)

if __name__ == '__main__':
    main()
