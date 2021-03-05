from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
import json

class PositionDTO:
    def __init__(self, dayTradingPos):
        self.Msg="DayTradingPosition"
        self.PosId = dayTradingPos.Id
        self.Symbol = dayTradingPos.Security.Symbol
        self.Active=dayTradingPos.Active
        self.PositionSize = dayTradingPos.SharesQuantity
        self.IsOpen=dayTradingPos.Open()
        self.IsRouting = dayTradingPos.Routing
        self.LongSignal = dayTradingPos.LongSignal
        self.ShortSignal = dayTradingPos.ShortSignal
        self.SignalType = dayTradingPos.SignalType
        self.SignalDesc = dayTradingPos.SignalDesc

        self.RSI=dayTradingPos.MinuteNonSmoothedRSIIndicator.RSI
        self.DailyRSI = dayTradingPos.DailyRSIIndicator.RSI

        self.NetShares = dayTradingPos.GetNetOpenShares()

        if dayTradingPos.GetNetOpenShares()>0:
            self.Direction = "LONG"
        elif dayTradingPos.GetNetOpenShares()<0:
            self.Direction="SHORT"
        else:
            self.Direction="LIQUID"

        self.CurrentMarketPrice = dayTradingPos.MarketData.Trade if dayTradingPos.MarketData is not None else None
        self.CurrentProfit = dayTradingPos.CurrentProfit * 100 if dayTradingPos.CurrentProfit is not None else None
        self.CurrentProfitMonetary = dayTradingPos.CurrentProfitMonetary
        self.CurrentProfitLastTrade  = dayTradingPos.CurrentProfitLastTrade
        self.CurrentProfitMonetaryLastTrade = dayTradingPos.CurrentProfitMonetaryLastTrade
        self.IncreaseDecrease = dayTradingPos.IncreaseDecrease
        self.MaxProfit = dayTradingPos.MaxProfit * 100 if dayTradingPos.MaxProfit is not None else None
        self.MaxLoss = dayTradingPos.MaxLoss * 100 if dayTradingPos.MaxLoss is not None else None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)


