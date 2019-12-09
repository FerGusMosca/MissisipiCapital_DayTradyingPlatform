from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
import json

class HistoricalPriceDTO:
    def __init__(self, historicalPrice):
        self.Msg="HistoricalPrice"
        self.MDEntryDate=historicalPrice.MDEntryDate
        self.OpeningPrice=historicalPrice.OpeningPrice
        self.ClosingPrice=historicalPrice.ClosingPrice
        self.TradingSessionHighPrice=historicalPrice.TradingSessionHighPrice
        self.TradingSessionLowPrice=historicalPrice.TradingSessionLowPrice



    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
