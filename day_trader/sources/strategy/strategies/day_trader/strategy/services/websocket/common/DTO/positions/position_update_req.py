from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class PositionUpdateReq(WebSocketMessage):


    def __init__(self, Msg,ReqId,PosId,SharesQuantity=None,Active=None,UUID=None, TradingMode=None,
                 Depurate=None,CleanStopLoss=None,CleanTakeProfit=None,CleanEndOfDay=None):
        super(PositionUpdateReq, self).__init__(Msg)
        self.PosId=PosId
        self.SharesQuantity=SharesQuantity
        self.Active = Active
        self.UUID = UUID
        self.TradingMode = TradingMode
        self.Depurate=Depurate
        self.ReqId = ReqId
        self.CleanStopLoss=CleanStopLoss
        self.CleanTakeProfit=CleanTakeProfit
        self.CleanEndOfDay=CleanEndOfDay

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
