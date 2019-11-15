from sources.strategy.strategies.day_trader.business_entities.security_to_trade import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class CancelPositionAck(WebSocketMessage):


    def __init__(self, Msg,UUID,ReqId,PosId,Success=True,Error=None):
        super(CancelPositionAck, self).__init__(Msg)
        self.UUID = UUID
        self.ReqId = ReqId
        self.PosId = PosId
        self.Success = Success
        self.Error = Error


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
