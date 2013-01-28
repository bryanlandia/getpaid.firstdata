import re
from datetime import datetime

from zope.annotation.interfaces import IAnnotations
# import zc.creditcard
# import zc.ssl
from z3c.suds import get_suds_client

from getpaid.firstdata.interfaces import IFirstDataGGe4Options
from getpaid.core import interfaces as GPInterfaces


APPROVAL_KEY = "getpaid.firstdata.approval_code"
TRANSACTION_TAG = "getpaid.firstdata.transaction_tag"


class FirstDataGGe4Connection(object):
        
    def __init__(self, server, exact_id, password, timeout=None):
        self.server = server
        self.login = exact_id
        self.password = password
        self.timeout = timeout
        self.standard_fields = dict(
            ExactID = exact_id,
            Password = password,
            )

    def sendTransaction(self, **kws):
        """Builds a transaction object, sends, and commits to First Data GGe4
           Pass in properties for the transaction object as keyword args.
        """
        # Parameters for transactions allowed by First Data GGe4
        # (Transaction){
        #    ExactID = None (String [10])
        #    Password = None (String [30])
        #    Transaction_Type = None (String [2])
        #    DollarAmount = None (Double)
        #    SurchargeAmount = None 
        #    Card_Number = None (String [16])
        #    Transaction_Tag = None (Integer)
        #    Track1 = None (String [75])
        #    Track2 = None (String)
        #    PAN = None 
        #    Authorization_Num = None (String [8])
        #    Expiry_Date = None (String [4])
        #    CardHoldersName = None (String [30])
        #    VerificationStr1 = None (String [41])
        #    This string is populated with the cardholders address information
        #    in a specific format. The address is verified and a result is
        #    returned (AVS property) that indicates how well the address
        #    matched. 
        #    VerificationStr2 = None (String [4])
        #    CVD_Presence_Ind = None (String [1])
        #    ZipCode = None (String [10])
        #    Tax1Amount = None  (Double [99,999.99])
        #    Tax1Number = None (String [20])
        #    Tax2Amount = None (Double [99,999.99])
        #    Tax2Number = None (String [20])
        #    Secure_AuthRequired = None 
        #    Secure_AuthResult = None
        #    Ecommerce_Flag = None
        #    XID = None
        #    CAVV = None
        #    CAVV_Algorithm = None
        #    Reference_No = None
        #    Customer_Ref = None (String [20])
        #    Reference_3 = None (Char [30])
        #    Language = None 
        #    Client_IP = None (String [15])
        #    Client_Email = None (String [30])
        #    User_Name = None 
        #    Currency = None (String [3]) 
        #    https://firstdata.zendesk.com/entries/450214-supported-currencies
        #    PartialRedemption = None
        #  }
        
        wsdl_uri = self.server + '/transaction/wsdl'
        client = get_suds_client(wsdl_uri)
        tx = client.factory.create('ns0:Transaction')
        tx.ExactID = self.login
        tx.Password = self.password
        for key, val in kws.items():
            if tx.__contains__(key):
                tx.__setattr__(key, val)

        # can also set tx.headers
        # can also set tx.proxy
        response = client.service.SendAndCommit(tx)
        return response


class FirstDataGGe4Processor(object):

    options_interface = IFirstDataGGe4Options
    _sites = dict(
        Production = "https://api.globalgatewaye4.firstdata.com",
        Demo = "https://api.demo.globalgatewaye4.firstdata.com"
        )    
        
    def __init__( self, context ):
        self.context = context
        self.settings = self.options_interface( self.context )
        server = self._sites[self.settings.server_url]
        exact_id = self.settings.merchant_exact_id
        password = self.settings.merchant_password
        self.connection = FirstDataGGe4Connection(
            server, exact_id, password)
            
    def _is_successful_response(self, response):
        if response.Transaction_Approved and \
            response.Error_Number == '0' and \
            response.EXact_Resp_Code == '00':
            return True
        return False  
        
    def _format_address_verification_str(self, bill_address):
        """Pass in a billing address object and return a string
           formatted for First Data GGe4's VerificationStr1
        """
        # like:
        # Street Address|Zip/Postal|City|State/Prov|Country.
        # 
        # If any of the address fields are not available or not applicable,
        # they may be omitted. If available, the last 5 or 9 digits, without
        # embedded spaces, should be the zip code. Numbers are not spelled out.
        # ('First Street' becomes '1ST Street', 'Second' becomes '2ND', etc).
        # For instance:
        # 1391 ELM STREET 40404
        # is equivalent to: 1391 ELM STREET|40404
        
        def _format_street_numbers(bill_street):
            numerical_reps = {
                'first' : '1ST',
                'second' : '2ND',
                'third' : '3RD',
                'fourth' : '4TH',
                'forth' : '4TH',
                'fifth' : '5TH',
                'sixth' : '6TH',
                'seventh' : '7TH',
                'eighth' : '8TH',
                'ninth' : '9TH',
                'tenth' : '10TH',
                # XXX TODO: make this more comprehensive                
            }
            for key, val in numerical_reps.items():
                p = re.compile(key, re.IGNORECASE)
                bill_street = p.sub(val, bill_street)
            return bill_street

        return "%s|%s|%s|%s" % (
            _format_street_numbers(bill_address.bill_first_line),
            bill_address.bill_postal_code,
            bill_address.bill_city,
            bill_address.bill_state,
            # 'USA',
            )

    def _format_cc_expiry(self, payment):
        """Pass in payment object and return string formatted as:
            YYMM.
        """
        dt = datetime.strptime(payment.cc_expiration, '%Y-%m-%d %H:%M')
        yy = dt.strftime('%y')
        mm = dt.strftime('%m')
        return "%s%s" % (mm, yy)

    def authorize( self, order, payment ):
        """ Authorize an amount using the card and buyer information.
        """
        if self.settings.allow_authorization == u'allow_authorization':
            bill_addr = order.billing_address
            price = order.getTotalPrice()
            txKw = dict(
                Ecommerce_flag = '7',
                Transaction_Type = '01',
                DollarAmount = price,
                CardHoldersName = payment.name_on_card,
                Card_Number = payment.credit_card,
                CVD_Presence_Ind = '1',
                Expiry_Date = self._format_cc_expiry(payment),
                ZipCode = order.billing_address.bill_postal_code,
                Currency = 'USD', # TODO: allow others
                VerificationStr1 = self._format_address_verification_str(
                    bill_addr),
                VerificationStr2 = payment.cc_cvc,
                Reference_No = order._order_id,
                Customer_Ref = order.contact_information.name.upper()
                )

            response = self.connection.sendTransaction(**txKw)
            
            if self._is_successful_response(response):
                annotation = IAnnotations( order )
                annotation[GPInterfaces.keys.processor_txn_id ] = \
                    response.Transaction_Tag
                order.processor_order_id = response.Retrieval_Ref_No
                order.user_payment_info_last4 = payment.credit_card[-4:]
                order.name_on_card = order.contact_information.name
                order.bill_phone_number = \
                    order.contact_information.phone_number
                annotation[APPROVAL_KEY] = response.Authorization_Num
                annotation[TRANSACTION_TAG] = response.Transaction_Tag
                return GPInterfaces.keys.results_success
            # failed
            else:
                resp_err = response.EXact_Message
            return ("Authorization Failed (%s).  Please check your entries "
                    "and try again." % resp_err)
        return ("Authorization Failed.  Please check your entries and try "
                "again.")

    def capture( self, order, amount ):
        """Make a 'tagged pre-authorization completion' request using the approval
           code stored on the order.
        """
        if self.settings.allow_capture == u'allow_capture':
            annotations = IAnnotations( order )
            txKw = dict(
                Ecommerce_flag = '7',
                Transaction_Type = '32',
                DollarAmount = amount,
                Transaction_Tag = annotations[TRANSACTION_TAG],
                Authorization_Num = annotations[APPROVAL_KEY]
            )
            response = self.connection.sendTransaction(**txKw)
            if self._is_successful_response(response):
                if annotations.get( GPInterfaces.keys.capture_amount ) is None:
                    annotations[ GPInterfaces.keys.capture_amount ] = amount
                else:
                    annotations[ GPInterfaces.keys.capture_amount ] += amount  
                order.user_payment_info_trans_id = response.Transaction_Tag
                return GPInterfaces.keys.results_success
        return "Capture Failed"

    def refund( self, order, amount ):
        raise NotImplementedError
        # if self.settings.allow_refunds == u'allow_refund':
        #     return GPInterfaces.keys.results_success
        # return "Refund Failed"
