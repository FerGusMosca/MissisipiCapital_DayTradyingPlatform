from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class PositionNewReq(WebSocketMessage):


    def __init__(self, Msg,ReqId,Symbol=None,SecurityType=None,Exchange=None,UUID=None):
        super(PositionNewReq, self).__init__(Msg)

        self.Symbol=Symbol
        self.UUID = UUID
        self.ReqId = ReqId
        self.SecurityType=SecurityType
        self.Exchange=Exchange

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)