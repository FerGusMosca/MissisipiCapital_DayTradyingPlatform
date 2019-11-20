from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
import json

class PositionDTO:
    def __init__(self, dayTradingPos):
        self.Msg="DayTradingPosition"
        self.Symbol = dayTradingPos.Security.Symbol
        self.PositionSize = dayTradingPos.Shares
        self.IsOpen=False
        self.CurrentMarketPrice = dayTradingPos.MarketData.Trade if dayTradingPos.MarketData is not None else None


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)


