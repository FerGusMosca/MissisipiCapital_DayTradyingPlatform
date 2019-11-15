from sources.strategy.strategies.day_trader.business_entities.security_to_trade import *
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

    def __init__(self, Msg,Side,ReqId,Qty,Account,Symbol=None,PosId=None,UUID=None):
        super(RoutePositionReq, self).__init__(Msg)
        self.Symbol=Symbol
        self.PosId = None
        self.Side=Side
        self.UUID = UUID
        self.ReqId = ReqId
        self.Qty = Qty
        self.Account = Account


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
