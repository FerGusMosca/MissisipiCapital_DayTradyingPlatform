from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.market_data_field import *
from sources.framework.common.enums.SubscriptionRequestType import *


_CURRENCY="USD"
_EXCHANGE="US"

class MarketDataWrapper(Wrapper):
    def __init__(self, marketData):
        self.MarketData = marketData



    #region Public Methods

    def GetAction(self):
        return Actions.MARKET_DATA

    def GetField(self, field):
        if field is None:
            return None

        if field == MarketDataField.Symbol:
            return self.MarketData.Symbol
        elif field == MarketDataField.SecurityType:
            return None
        elif field == MarketDataField.Currency:
            return None
        elif field == MarketDataField.MDMkt:
            return None
        elif field == MarketDataField.OpeningPrice:
            return None
        elif field == MarketDataField.ClosingPrice:
            return None
        elif field == MarketDataField.TradingSessionHighPrice:
            return None
        elif field == MarketDataField.TradingSessionLowPrice:
            return None
        elif field == MarketDataField.TradeVolume:
            return None
        elif field == MarketDataField.OpenInterest:
            return None
        elif field == MarketDataField.SettlType:
            return None
        elif field == MarketDataField.CompositeUnderlyingPrice:
            return None
        elif field == MarketDataField.MidPrice:
            return None
        elif field == MarketDataField.SessionHighBid:
            return None
        elif field == MarketDataField.SessionLowOffer:
            return None
        elif field == MarketDataField.EarlyPrices:
            return None
        elif field == MarketDataField.Trade:
            return self.MarketData.Trade
        elif field == MarketDataField.MDTradeSize:
            return self.MarketData.MDTradeSize
        elif field == MarketDataField.BestBidPrice:
            return self.MarketData.BestBidPrice
        elif field == MarketDataField.BestAskPrice:
            return self.MarketData.BestAskPrice
        elif field == MarketDataField.BestBidSize:
            return self.MarketData.BestBidSize
        elif field == MarketDataField.BestBidCashSize:
            return None
        elif field == MarketDataField.BestAskSize:
            return self.MarketData.BestAskSize
        elif field == MarketDataField.BestAskCashSize:
            return None
        elif field == MarketDataField.BestBidExch:
            return None
        elif field == MarketDataField.BestAskExch:
            return None
        elif field == MarketDataField.MDEntryDate:
            return self.MarketData.MDLocalEntryDate
        elif field == MarketDataField.MDEntryTime:
            return None
        elif field == MarketDataField.MDLocalEntryDate:
            return None
        elif field == MarketDataField.MDLocalEntryDate:
            return None
        elif field == MarketDataField.LastTradeDateTime:
            return None
        elif field == MarketDataField.Change:
            return None
        elif field == MarketDataField.StdDev:
            return None
        else:
            return None

    #endregion

