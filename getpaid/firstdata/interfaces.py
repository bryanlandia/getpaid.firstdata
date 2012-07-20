from zope import schema
from zope.interface import Interface
from getpaid.core.interfaces import IPaymentProcessorOptions#, IRecurringPaymentProcessor
from getpaid.firstdata import FirstDataGGe4MessageFactory as _


class IFirstDataGGe4Options(IPaymentProcessorOptions):
    """
    First Data Global Gateway e4 payment processor options
    """
    server_url = schema.Choice(
        title=_(u"FirstData Global Gateway e4 Server URL"),
        values=("Demo",
                "Production"),
        default="Demo"
        )
    merchant_exact_id = schema.ASCIILine( title=_(u"ExactID (GatewayID)") )
    merchant_password = schema.Password( title=_(u"Password") )
    allow_authorization = schema.Choice(
        title=_(u"Allow Authorizations"),
        default=u"allow_authorization",
        values = (u"allow_authorization",
                  u"no_authorization")
        )

    allow_capture = schema.Choice(
        title=_(u"Allow Captures"),
        default=u"allow_capture",
        values = (u"allow_capture",
                  u"no_capture" )
        )

    allow_refunds = schema.Choice(
        title=_(u"Allow Refunds"),
        default=u"allow_refund",
        values = (u"allow_refund",
                  u"no_refund" )
        )



### Adapters
class IFirstDataGGe4OrderInfo(Interface):
    def __call__():
        """Returns information of order."""

### Utilities
class IDecimalPrice(Interface):
    def __call__():
        """Returns decimal price."""

