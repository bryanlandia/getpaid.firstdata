from zope.interface import implements
from decimal import Decimal, ROUND_HALF_UP
from getpaid.firstdata.interfaces import IDecimalPrice


class DecimalPrice(object):
    implements(IDecimalPrice)
    def __call__(self, price):
        if price is None:
            return None
        if type(price).__name__ == 'float':
            price = str(price)
        price = Decimal(price).quantize(Decimal('.001'), rounding=ROUND_HALF_UP)
        price = Decimal(price).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        return price
