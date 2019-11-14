from sources.strategy.strategies.day_trader.business_entities.security_to_trade import *
import json

class PositionDTO:
    def __init__(self, secToTrade):
        self.Symbol = secToTrade.Security.Symbol
        self.PositionSize = secToTrade.Shares
        self.IsOpen=False
        self.CurrentMarketPrice = secToTrade.Security.MarketData.Trade


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)


