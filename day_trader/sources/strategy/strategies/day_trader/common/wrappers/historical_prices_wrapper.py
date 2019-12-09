from sources.framework.common.wrappers.wrapper import *
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.historical_prices_field import *
from sources.order_routers.bloomberg.common.util.subscription_helper import *
import blpapi


class HistoricalPricesWrapper(Wrapper):

    def __init__(self,pSymbol,pFrom,pTo,pMarketDataArray):
        self.Symbol = pSymbol
        self.From=pFrom
        self.To = pTo
        self.MarketDataArray = pMarketDataArray

    # region Public Methods

    def GetAction(self):
        return Actions.HISTORICAL_PRICES

    def GetField(self, field):

        if field == None:
            return None

        if field == HistoricalPricesField.Security:
            return self.Symbol
        elif field == HistoricalPricesField.MarketDataArray:
            return self.MarketDataArray
        elif field == HistoricalPricesField.TimeUnit:
            return TimeUnit.Day
        else:
            return None


    # endregion
