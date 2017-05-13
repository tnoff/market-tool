import argparse
from datetime import datetime
import json

from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from market_tool import stocks

INPUT_DATETIME_FORMAT = "%Y-%m-%dT00:00:00"
OUTPUT_DATETIME_FORMAT = "%Y-%m-%d"

# Set up tables for database
BASE = declarative_base()

def as_dict(row, datetime_output_format):
    data = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        if isinstance(value, datetime):
            value = value.strftime(datetime_output_format)
        data[column.name] = value
    return data

def inject_function(func):
    def decorated_class(cls):
        setattr(cls, func.__name__, func)
        return cls
    return decorated_class


@inject_function(as_dict)
class Exchange(BASE):
    __tablename__ = 'exchange'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)


@inject_function(as_dict)
class Stock(BASE):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String(32), unique=True)
    company_name = Column(String(256))
    exchange_id = Column(Integer, ForeignKey('exchange.id'))


@inject_function(as_dict)
class Currency(BASE):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)


@inject_function(as_dict)
class StockPrice(BASE):
    __tablename__ = 'stockprice'
    __table_args__ = (UniqueConstraint('stock_id', 'date',
                                       name='_stock_date_price'),)
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stock.id'))
    date = Column(Date)
    price = Column(Float)
    currency_id = Column(Integer, ForeignKey('currency.id'))


# Now make class to use for syncing up database
class StockDatabase(object):
    def __init__(self, database_file=None):
        if database_file is None:
            engine = create_engine('sqlite:///', encoding='utf-8')
        else:
            engine = create_engine('sqlite:///%s' % database_file, encoding='utf-8')
        BASE.metadata.create_all(engine)
        BASE.metadata.bind = engine
        self.db_session = sessionmaker(bind=engine)()

    def __ensure_currency(self, currency):
        curr = self.db_session.query(Currency).filter(Currency.name == currency).first()
        if curr is None:
            new_currency = Currency(name=currency)
            self.db_session.add(new_currency)
            self.db_session.commit()
            return new_currency.id
        return curr.id

    def __ensure_exchange(self, exchange):
        ex = self.db_session.query(Exchange).filter(Exchange.name == exchange).first()
        if ex is None:
            new_exchange = Exchange(name=exchange)
            self.db_session.add(new_exchange)
            self.db_session.commit()
            return new_exchange.id
        return ex.id

    def __ensure_stock(self, symbol):
        stock = self.db_session.query(Stock).filter(Stock.stock_symbol == symbol).first()
        if stock is None:
            code, stock_data = stocks.lookup_resource(symbol)
            if code is False:
                return False, "Issue getting stock information for symbol:%s", symbol
            # Check if exchange already in database, if not create
            exchange = stock_data[0]["Exchange"].lower()
            exchange_id = self.__ensure_exchange(exchange)
            new_stock = Stock(stock_symbol=symbol, exchange_id=exchange_id,
                              company_name=stock_data[0]["Name"].lower())
            self.db_session.add(new_stock)
            self.db_session.commit()
            return new_stock.id
        return stock.id


    def stock_update(self, number_of_days, stock_symbols):
        code, historical_data = stocks.historical_data(False, 'Day', stock_symbols,
                                                       'price', 'c', number_of_days=number_of_days)
        if code is False:
            return False, historical_data
        for element in historical_data["Elements"]:
            # Get currency if already in database, else create
            currency = element["Currency"].lower()
            currency_id = self.__ensure_currency(currency)
            # Get stock if already in database, else create
            symbol = element["Symbol"].lower()
            stock_id = self.__ensure_stock(symbol)

            for _, param_values in element["DataSeries"].items():
                for (count, value) in enumerate(param_values["values"]):
                    date = datetime.strptime(historical_data["Dates"][count], INPUT_DATETIME_FORMAT)
                    new_price = StockPrice(stock_id=stock_id, currency_id=currency_id,
                                           date=date, price=value)
                    try:
                        self.db_session.add(new_price)
                        self.db_session.commit()
                    except IntegrityError:
                        self.db_session.rollback()

    def stock_get_prices(self, stock_symbol):
        stock_query, exchange_query = self.db_session.query(Stock, Exchange).join(Exchange).\
                filter(Stock.stock_symbol == stock_symbol).first()
        if stock_query is None:
            return None, None
        stock_obj = stock_query.as_dict(OUTPUT_DATETIME_FORMAT)
        stock_obj['exchange'] = exchange_query.name

        query = self.db_session.query(StockPrice, Currency).join(Currency).\
                filter(StockPrice.stock_id == stock_query.id).\
                order_by(desc(StockPrice.date))

        prices = []
        for stock_price, currency in query:
            price = stock_price.as_dict(OUTPUT_DATETIME_FORMAT)
            price['currency'] = currency.name
            prices.append(price)
        return stock_obj, prices


# Set up parse args and main class to use
def parse_args():
    p = argparse.ArgumentParser(description="Database Scripts")
    p.add_argument("database_file", help="SQLite Database File")

    sub = p.add_subparsers(description="Module", dest="module")

    update = sub.add_parser("update", help="Update stock information")
    update.add_argument("number_of_days", type=int, help="Number of days past to add to db")
    update.add_argument("stock_symbols", nargs="+", help="Stocks symbols to update")

    prices = sub.add_parser("prices", help="List stock prices")
    prices.add_argument("stock_symbol", help="Stock symbol whose prices to show")

    return vars(p.parse_args())


def _update(client, args):
    client.stock_update(args["number_of_days"], args["stock_symbols"])
    print "Finished"

def _price(client, args):
    stock, prices = client.stock_get_prices(args["stock_symbol"])
    print "Stock"
    print json.dumps(stock, indent=4)
    print "Prices"
    print json.dumps(prices, indent=4)

COMMAND_DICT = {
    'price' : _price,
    'update' : _update,
}

def main():
    args = parse_args()
    db = StockDatabase(database_file=args["database_file"])
    method = COMMAND_DICT[args['module']]
    method(db, args)

if __name__ == '__main__':
    main()
