from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.PloneGetPaid.browser.checkout import BasePaymentMethodButton

class LuottokuntaPaymentButton(BasePaymentMethodButton):
    __call__ = ZopeTwoPageTemplateFile("templates/button.pt")
