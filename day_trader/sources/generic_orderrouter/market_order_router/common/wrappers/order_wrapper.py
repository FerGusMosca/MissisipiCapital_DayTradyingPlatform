from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.order_field import *
from sources.framework.common.enums.SettlType import *
from sources.framework.common.enums.Side import *
from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.OrdType import *
from sources.framework.common.enums.PriceType import *
from sources.framework.common.enums.TimeInForce import *


class OrderWrapper(Wrapper):
    def __init__(self, pSymbol, pQty, pClOrdId, pCurrency,pSecurityType=None,pExchange=None, pSide=None, pAccount=None, pBroker=None, pStrategy=None,
                 pOrderType=None,
                 pOrderPrice=None):
        self.Symbol = pSymbol
        self.SecurityType=pSecurityType
        self.Exchange=pExchange
        self.OrderQty = pQty
        self.ClOrdId = pClOrdId
        self.Currency = pCurrency
        self.Side = pSide
        self.Account = pAccount
        self.Broker = pBroker
        self.Strategy = pStrategy
        self.OrderType = pOrderType
        self.OrderPrice = pOrderPrice

    def GetOrdQty(self):
        """

        Returns:

        """
        # qty is always positive
        if self.OrderQty > 0:
            return self.OrderQty
        else:
            return self.OrderQty * -1

    def GetSide(self):
        """

        Returns:

        """
        if self.Side is not None:
            return self.Side
        else:
            # qty is always positive
            if self.OrderQty > 0:
                return Side.Buy
            else:
                return Side.Sell

    def GetOrdType(self):
        """

        Returns:

        """
        if self.OrderType is not None:
            return self.OrderType
        else:
            return OrdType.Market  # default is market

    def GetField(self, field):
        """

        Args:
            field ():

        Returns:

        """
        if field is None:
            return None

        if field == OrderField.Symbol:
            return self.Symbol
        elif field == OrderField.OrderQty:
            return self.GetOrdQty()
        elif field == OrderField.Side:
            return self.GetSide()
        elif field == OrderField.ClOrdID:
            return self.ClOrdId
        elif field == OrderField.SettlType:
            return SettlType.Regular  # default
        elif field == OrderField.SettlDate:
            return None  # default
        elif field == OrderField.SecurityType:
            return self.SecurityType
        elif field == OrderField.Currency:
            return self.Currency
        elif field == OrderField.Exchange:
            return self.Exchange
        elif field == OrderField.OrdType:
            return self.GetOrdType()
        elif field == OrderField.PriceType:
            return PriceType.FixedAmount  # default
        elif field == OrderField.Price:
            return self.OrderPrice
        elif field == OrderField.StopPx:
            return None  # default
        elif field == OrderField.ExpireDate:
            return None  # default
        elif field == OrderField.ExpireTime:
            return None  # default
        elif field == OrderField.CashOrderQty:
            return None  # default
        elif field == OrderField.TimeInForce:
            return TimeInForce.Day  # default
        elif field == OrderField.MinQty:
            return None  # default
        elif field == OrderField.Account:
            return self.Account
        elif field == OrderField.Broker:
            return self.Broker
        elif field == OrderField.Strategy:
            return self.Strategy
        else:
            return None

