from zope.interface import implements
from zope.component import adapts
from getpaid.core.interfaces import IStore
from getpaid.firstdata.interfaces import IFirstDataGGe4Processor
from getpaid.firstdata.interfaces import IFirstDataGGe4Options

class FirstDataGGe4Processor( object ):

    implements(IFirstDataGGe4Processor)
    adapts(IStore)

    options_interface = IFirstDataGGe4Options

    def __init__( self, context ):
        self.context = context

    def capture(self, order, price):
        pass
        
    def authorize( self, order, payment ):
        pass

    def refund( self, order, amount ):
        """ We aren't handling refunds yet. """
        raise NotImplementedError
