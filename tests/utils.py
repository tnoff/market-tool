import datetime

import random
import string

def random_string(prefix='', suffix='', length=10):
    letters = string.digits + string.lowercase
    s = ''.join(random.choice(letters) for _ in range(length))
    return '%s%s%s' % (prefix, s, suffix)

def random_date(start, end):
    start_epoch = int(start.strftime('%s'))
    end_epoch = int(end.strftime('%s'))
    random_epoch = random.randint(start_epoch, end_epoch)
    return datetime.datetime.fromtimestamp(random_epoch)


class PandaStockMock(object):
    def __init__(self, high, low, openy, close, volume):
        self.High = high
        self.Low = low
        self.Open = openy
        self.Close = close
        self.Volume = volume

class PandasDatetimeMock(object):
    def __init__(self, datetime_str, date_format='%Y-%m-%d'):
        self.date = datetime_str
        self.date_format = date_format

    def to_pydatetime(self):
        return datetime.datetime.strptime(self.date, self.date_format)
