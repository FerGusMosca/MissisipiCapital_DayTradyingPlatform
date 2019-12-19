from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class RoutePositionReq(WebSocketMessage):

    #region Static Attributes

    @staticmethod
    def _BUY():
        return "BUY"

    @staticmethod
    def _SELL ():
        return "SELL"

    #endregion

    def __init__(self, Msg,Side,ReqId,Qty, Type=None,Account=None,Symbol=None,PosId=None,Price=None,UUID=None):
        super(RoutePositionReq, self).__init__(Msg)
        self.Symbol=Symbol
        self.PosId = PosId
        self.Type=Type
        self.Side=Side
        self.Price = Price
        self.UUID = UUID
        self.ReqId = ReqId
        self.Qty = Qty
        self.Account = Account


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
