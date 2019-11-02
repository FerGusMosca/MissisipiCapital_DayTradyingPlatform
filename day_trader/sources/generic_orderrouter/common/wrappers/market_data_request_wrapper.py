from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.market_data_request_field import *


class MarketDataRequestWrapper(Wrapper):
    def __init__(self, pSymbol, pSubscriptionRequestType, pSecurityType=None, pCurrency=None, pExchange=None):
        self.Symbol = pSymbol
        self.SubscriptionRequestType = pSubscriptionRequestType
        self.SecurityType = pSecurityType
        self.Currency = pCurrency
        self.Exchage = pExchange

    def GetAction(self):
        """

        Returns:

        """
        return Actions.MARKET_DATA_REQUEST

    def GetField(self, field):
        """

        Args:
            field ():

        Returns:

        """
        if field is None:
            return None

        if field == MarketDataRequestField.Symbol:
            return self.Symbol
        elif field == MarketDataRequestField.SecurityType:
            return self.SecurityType
        elif field == MarketDataRequestField.Currency:
            return self.Currency
        elif field == MarketDataRequestField.Exchange:
            return self.Exchage
        elif field == MarketDataRequestField.SubscriptionRequestType:
            return self.SubscriptionRequestType

        else:
            return None

    # endregion
