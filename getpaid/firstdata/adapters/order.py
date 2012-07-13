from decimal import Decimal
from zope.interface import implements
from zope.component import adapts, getUtility
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from zope.app.component.hooks import getSite
from getpaid.core.order import Order

### For implements.
from getpaid.firstdata.interfaces import IFirstDataGGe4OrderInfo

### For call.
from getpaid.firstdata.interfaces import (
    IDecimalPrice,
    IFirstDataGGe4Options
)

class FirstDataGGe4OrderInfo(object):

    implements(IFirstDataGGe4OrderInfo)
    adapts(Order)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        """Returns information of order."""
        site = getSite()
        context = aq_inner(self.context)
        membership = getToolByName(site, 'portal_membership')
        member_id = membership.getAuthenticatedMember().getId()
        getpaid_order_id = context.order_id
        customer_id = member_id
        dp = getUtility(IDecimalPrice)
        price = dp(context.getTotalPrice())
        firstdata_price = unicode(Decimal(price * 100).quantize(Decimal('1')))
        options = IFirstDataGGe4Options(site)
        merchant_exact_id = options.merchant_exact_id
        order_info = {
                        'merchant_exact_id' : merchant_exact_id,
                        'price' : firstdata_price,
                        'order_number' : getpaid_order_id,
                        'getpaid_order_id': getpaid_order_id,
                        'customer_id' : customer_id,
        }
        return order_info
