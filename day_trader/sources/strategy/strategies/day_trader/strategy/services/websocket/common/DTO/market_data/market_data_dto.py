from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
import json

class MarketDataDTO:
    def __init__(self, md):
        self.Msg="MarketData"
        self.Symbol=md.Security.Symbol
        self.TradingSessionHighPrice = md.TradingSessionHighPrice
        self.TradingSessionLowPrice = md.TradingSessionLowPrice
        self.OpeningPrice = md.OpeningPrice
        self.Imbalance = md.Imbalance
        self.Trade = md.Trade
        self.OpeningPrice = md.OpeningPrice
        self.ClosingPrice = md.ClosingPrice
        self.BestBidPrice = md.BestBidPrice
        self.BestAskPrice = md.BestAskPrice
        self.BestBidSize = md.BestBidSize
        self.BestAskSize = md.BestAskSize
        self.BestBidCashSize = md.BestBidCashSize
        self.BestAskCashSize = md.BestAskCashSize
        self.TradeVolume = md.TradeVolume
        self.MDTradeSize = md.MDTradeSize
        self.BestAskExch = md.BestAskExch
        self.BestBidExch = md.BestBidExch
        self.Change=md.Change
        self.StdDev = md.StdDev


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
