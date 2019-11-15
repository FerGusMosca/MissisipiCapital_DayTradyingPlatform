from sources.strategy.strategies.day_trader.business_entities.security_to_trade import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class CancelPositionReq(WebSocketMessage):


    def __init__(self, Msg,PosId,ReqId,UUID=None):
        super(CancelPositionReq, self).__init__(Msg)
        self.PosId=PosId
        self.UUID = UUID
        self.ReqId = ReqId

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
