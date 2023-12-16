from sources.framework.common.enums.Actions import *
from sources.framework.common.wrappers.wrapper import *
from sources.framework.common.enums.fields.order_field import *
from sources.generic_orderrouter.market_order_router.common.wrappers.order_wrapper import OrderWrapper


class UpdateOrderWrapper(OrderWrapper):

    #region Constructors

    def __init__(self, pSymbol,pOrigClOrdId, pClOrdId,pOrderId,pSide=None,
                    pOrderType=None,pOrderPrice=None, pQty=None):
        super().__init__(pSymbol, pQty, pClOrdId, None, None, None, pSide, None, None, None,pOrderType,pOrderPrice)
        self.OrigClOrdId=pOrigClOrdId
        self.OrderId=pOrderId
    #endregion

    # region Public Methods

    def GetAction(self):
        return Actions.UPDATE_ORDER

    def GetField(self, field):

        if field == OrderField.OrigClOrdID:
            return self.OrigClOrdId
        else:
            return super().GetField(field)

    # endregion
