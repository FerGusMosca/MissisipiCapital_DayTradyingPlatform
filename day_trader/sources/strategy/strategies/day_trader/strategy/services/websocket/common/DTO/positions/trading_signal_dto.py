from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *

import json

class TradingSignalDTO:
    def __init__(self, symbol,signal,recommendation):
        self.Msg="TradingSignal"
        self.Symbol=symbol
        self.Signal = signal
        self.RecomendationId = recommendation
        self.RecomendationDesc = self.TranslateRecomendation(recommendation)


    def TranslateRecomendation(self,recomendation):
        if recomendation == DayTradingPosition._TERMINALLY_CLOSED():
            return "Terminally Closed"
        elif recomendation == DayTradingPosition._REC_GO_LONG_NOW():
            return "Go Long Now!"
        elif recomendation == DayTradingPosition._REC_GO_SHORT_NOW():
            return "Go Short Now!"
        elif recomendation == DayTradingPosition._REC_STAY_OUT():
            return "Stay Out"
        elif recomendation == DayTradingPosition._REC_EXIT_LONG_NOW():
            return "Exit Long Now!"
        elif recomendation == DayTradingPosition._REC_STAY_LONG():
            return "Stay Long"
        elif recomendation == DayTradingPosition._REC_EXIT_SHORT_NOW():
            return "Exit Short Now!"
        elif recomendation == DayTradingPosition._REC_STAY_SHORT():
            return "Stay Short"
        else:
            return "Unknown recomendation id {}".format(recomendation)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
