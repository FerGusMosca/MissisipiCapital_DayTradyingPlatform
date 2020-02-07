from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.order_field import *
from sources.generic_orderrouter.market_order_router.common.wrappers.order_wrapper import *


class NewOrderWrapper(OrderWrapper):
    def __init__(self, pSymbol, pQty, pClOrdId, pCurrency,pSecType,pExchange, pSide=None, pAccount=None, pBroker=None, pStrategy=None,
                 pOrderType=None,pOrderPrice=None):
        super().__init__(pSymbol, pQty, pClOrdId, pCurrency,pSecType,pExchange, pSide, pAccount, pBroker, pStrategy, pOrderType,
                         pOrderPrice)

    def GetAction(self):
        """

        Returns:

        """
        return Actions.NEW_ORDER

    def GetField(self, field):
        """

        Args:
            field ():

        Returns:

        """
        if field is None:
            return None

        if field == OrderField.OrigClOrdID:
            return None
        else:
            return super().GetField(field)
