import datetime

from jsonschema import validate
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from market_tool import stocks
from market_tool.schema import DATABASE_SCHEMA

DATETIME_INPUT_FORMAT = '%Y-%m-%d'
DATETIME_OUTPUT_FORMAT = '%Y-%m-%d'

# Set up tables for database
BASE = declarative_base()

def as_dict(row, datetime_output_format):
    data = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        if isinstance(value, datetime.date):
            value = value.strftime(datetime_output_format)
        data[column.name] = value
    return data

def inject_function(func):
    def decorated_class(cls):
        setattr(cls, func.__name__, func)
        return cls
    return decorated_class


@inject_function(as_dict)
class Stock(BASE):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True)
    stock_symbol = Column(String(32), unique=True)


@inject_function(as_dict)
class StockPrice(BASE):
    __tablename__ = 'stockprice'
    __table_args__ = (UniqueConstraint('stock_id', 'date',
                                       name='_stock_date_price'),)
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stock.id'))
    date = Column(Date)
    price_low = Column(Float)
    price_high = Column(Float)
    price_open = Column(Float)
    price_close = Column(Float)
    volume = Column(Integer)


class StockDatabase(object):
    def __init__(self, database_dict):
        '''
        Stock Database interface
        database_dict       :       Dict data for database connection, must match schema
        '''
        validate(database_dict, DATABASE_SCHEMA)

        if database_dict.has_key('sqlite'):
            if database_dict['sqlite']['database_file'] is None:
                engine = create_engine('sqlite:///', encoding='utf-8')
            else:
                engine = create_engine('sqlite:///%s' % database_dict['sqlite']['database_file'], encoding='utf-8')
        elif database_dict.has_key('mysql'):
            engine = create_engine('mysql+pymysql://%s:%s@%s/%s' % (database_dict['mysql']['username'],
                                                                    database_dict['mysql']['password'],
                                                                    database_dict['mysql']['host'],
                                                                    database_dict['mysql']['database_name'],))

        BASE.metadata.create_all(engine)
        BASE.metadata.bind = engine
        self.db_session = sessionmaker(bind=engine)()

    def __ensure_stock(self, stock_symbol):
        stock = self.db_session.query(Stock).\
                filter(Stock.stock_symbol == stock_symbol.lower()).first()
        if stock is None:
            stock = Stock(stock_symbol=stock_symbol.lower())
            self.db_session.add(stock)
            self.db_session.commit()
        return stock.id

    def stock_update(self, stock_symbols, start_date, end_date, number_decimals=2):
        '''
        Update stock information in database for given stock symbols within date range
        stock_symbols       :       Single stock symbol or list of stock symbols
        start_date          :       Start date of stock information
        end_date            :       End date of stock information
        number_decimals     :       Number of decimals to use with stock prices
        '''
        if not isinstance(stock_symbols, list):
            stock_symbols = [stock_symbols]

        for stock in stock_symbols:
            stock_id = self.__ensure_stock(stock)
            hist_data = stocks.historical_data(stock, start_date, end_date,
                                               number_decimals=number_decimals)
            for data_set in hist_data:
                stock_args = {
                    'stock_id' : stock_id,
                    'date' : data_set['datetime'],
                    'price_open' : data_set['open'],
                    'price_close' : data_set['close'],
                    'price_low' : data_set['low'],
                    'price_high' : data_set['high'],
                    'volume' : data_set['volume'],
                }
                stock_price = StockPrice(**stock_args)
                try:
                    self.db_session.add(stock_price)
                    self.db_session.commit()
                except IntegrityError:
                    self.db_session.rollback()

    def stock_show(self, stock_symbols, start_date=None, end_date=None):
        '''
        Show stock information for given date range
        stock_symbols       :       Single stock symbol or list of stock symbols
        start_date          :       Start date of stock information
        end_date            :       End date of stock information
        '''
        if not isinstance(stock_symbols, list):
            stock_symbols = [stock_symbols]
        query = self.db_session.query(StockPrice, Stock).join(Stock).\
                filter(Stock.stock_symbol.in_(stock_symbols))
        if start_date is not None:
            query = query.filter(StockPrice.date >= start_date)
        if end_date is not None:
            query = query.filter(StockPrice.date <= end_date)
        query = query.order_by(desc(StockPrice.date))
        stock_list = []
        for stock_price, stock in query:
            stock_data = stock_price.as_dict(DATETIME_OUTPUT_FORMAT)
            stock_data.pop('id')
            stock_data.pop('stock_id')
            stock_data['stock_symbol'] = stock.as_dict(DATETIME_OUTPUT_FORMAT).pop('stock_symbol')
            stock_list.append(stock_data)
        return stock_list
