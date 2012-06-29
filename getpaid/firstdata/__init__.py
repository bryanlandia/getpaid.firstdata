from zope.i18nmessageid import MessageFactory
FirstDataGGe4MessageFactory = MessageFactory('getpaid.firstdata')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    
import interfaces
from getpaid.core.options import PersistentOptions

FirstDataGGe4Options = PersistentOptions.wire(
                           "AuthorizeNetOptions",
                           "getpaid.firstdata",
                           interfaces.FirstDataGGe4Options)
