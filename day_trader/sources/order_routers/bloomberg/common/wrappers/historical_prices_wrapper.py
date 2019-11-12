from sources.framework.common.wrappers.wrapper import *
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.historical_prices_field import *
from sources.order_routers.bloomberg.common.util.subscription_helper import *
import blpapi


class HistoricalPricesWrapper(Wrapper):

    def __init__(self,pLogger, pTimeUnit,pMessage):

        self.Logger = pLogger
        self.TimeUnit = pTimeUnit
        self.Message=pMessage
        self.Security = None

    #region Private Methods

    def GetSecurity (self):
        self.Security =  SubscriptionHelper.ExtractSecurity(self.Logger,self.Message)
        return self.Security

    def GetMarketDataArray(self):
        if(self.Security is None):
            self.Security = self.GetSecurity()

        return SubscriptionHelper.ProcessHistoricalPrices(self.Logger,self.Security, self.Message)

    #endregion

    # region Public Methods

    def GetAction(self):
        return Actions.HISTORICAL_PRICES

    def GetField(self, field):

        if field == None:
            return None

        if field == HistoricalPricesField.Security:
            return self.GetSecurity()
        elif field == HistoricalPricesField.TimeUnit:
            return self.TimeUnit
        elif field == HistoricalPricesField.MarketDataArray:
            return self.GetMarketDataArray()

        else:
            return None


    # endregion
