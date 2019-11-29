from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class UpdateModelParamAck(WebSocketMessage):


    def __init__(self, Msg,UUID,ReqId,symbol,key,Success=True,Error=None):
        super(UpdateModelParamAck, self).__init__(Msg)
        self.UUID = UUID
        self.ReqId = ReqId
        self.Symbol = symbol
        self.Key= key
        self.Success = Success
        self.Error = Error


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)

