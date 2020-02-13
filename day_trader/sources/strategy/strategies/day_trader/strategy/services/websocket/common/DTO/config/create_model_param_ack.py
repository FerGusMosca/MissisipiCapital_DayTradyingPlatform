from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class CreateModelParamAck(WebSocketMessage):


    def __init__(self, Msg,UUID,ReqId,key,symbol=None,Success=True,Error=None):
        super(CreateModelParamAck, self).__init__(Msg)
        self.UUID = UUID
        self.ReqId = ReqId
        self.Symbol = symbol
        self.Key= key
        self.Success = Success
        self.Error = Error


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
