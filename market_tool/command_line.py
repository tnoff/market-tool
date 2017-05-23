import argparse
from datetime import datetime
import json

from market_tool import database

DATETIME_INPUT_FORMAT = '%Y-%m-%d'

def parse_args():
    p = argparse.ArgumentParser(description="Market Tool Command Line Client")

    sub = p.add_subparsers(dest="command", help="Command")

    db_update = sub.add_parser("database-update", help="Database Update")
    db_update.add_argument("database_schema", type=json.loads,
                           help="Database Schema to use")
    db_update.add_argument("start_date",
                           help="Start date in YYYY-MM-DD format")
    db_update.add_argument("end_date",
                           help="End date in YYYY-MM-DD format")
    db_update.add_argument("stock_symbols", nargs="+", help="Stock symbols")
    return vars(p.parse_args())

def database_update(args):
    db = database.StockDatabase(args['database_schema'])
    print 'Updating'
    start_date = datetime.strptime(args['start_date'], DATETIME_INPUT_FORMAT)
    end_date = datetime.strptime(args['end_date'], DATETIME_INPUT_FORMAT)
    db.stock_update(args['stock_symbols'], start_date, end_date)
    print 'Done updating'

COMMAND_DICT = {
    'database-update' : database_update,
}

def main():
    args = parse_args()
    method = COMMAND_DICT[args['command']]
    method(args)
