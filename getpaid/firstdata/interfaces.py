from zope import schema
from zope.interface import Interface
from getpaid.core.interfaces import IPaymentProcessor,IPaymentProcessorOptions#, IRecurringPaymentProcessor
from getpaid.firstdata import FirstDataGGe4MessageFactory as _

class IFirstDataGGe4Processor(IPaymentProcessor):
    """
    FirstData Global Gateway e4 Processor
    """

class IFirstDataGGe4Options(IPaymentProcessorOptions):
    """
    First Data Global Gateway e4 payment processor options
    """
    server_url = schema.Choice(
        title=_(u"FirstData Global Gateway e4 Server URL"),
        values=("Demo",
                "Production")
        )
    merchant_exact_id = schema.ASCIILine( title=_(u"ExactID (GatewayID)") )
    merchant_password = schema.ASCIILine( title=_(u"Password") )


### Adapters
class IFirstDataGGe4OrderInfo(Interface):
    def __call__():
        """Returns information of order."""

### Utilities
class IDecimalPrice(Interface):
    def __call__():
        """Returns decimal price."""

