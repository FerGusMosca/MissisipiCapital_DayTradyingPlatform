from sources.framework.common.enums.Actions import *
from sources.framework.common.wrappers.wrapper import *
from sources.framework.common.enums.TimeUnit import *
from sources.framework.common.enums.fields.order_cancel_reject_field import *
from sources.order_routers.bloomberg.common.util.bloomberg_translation_helper import *

class OrderCancelRejectWrapper(Wrapper):

    def __init__(self,pText,pCxlRejResponseTo,pCxlRejReason,pOrder):

        self.Order = pOrder
        self.Text=pText
        self.CxlRejResponseTo=pCxlRejResponseTo
        self.CxlRejReason=pCxlRejReason

    # region Public Methods

    def GetAction(self):
        return Actions.ORDER_CANCEL_REJECT

    def GetField(self, field):

        if field == None:
            return None

        if field == OrderCancelRejectField.OrderID:
            return self.Order.OrderId if self.Order is not None else None
        elif field == OrderCancelRejectField.ClOrdID:
            return self.Order.ClOrdId if self.Order is not None else None
        elif field == OrderCancelRejectField.OrigClOrdID:
            return self.Order.OrigClOrdId if self.Order is not None else None
        elif field == OrderCancelRejectField.Text:
            return self.Text
        elif field == OrderCancelRejectField.OrdStatus:
            return self.Order.OrdStatus if self.Order is not None else None
        elif field == OrderCancelRejectField.CxlRejResponseTo:
            return self.CxlRejResponseTo
        elif field == OrderCancelRejectField.CxlRejReason:
            return self.CxlRejReason
        else:
            return None


    # endregion
