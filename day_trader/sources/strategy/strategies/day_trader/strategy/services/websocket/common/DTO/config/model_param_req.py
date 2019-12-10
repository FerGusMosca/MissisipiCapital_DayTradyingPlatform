from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class ModelParamReq(WebSocketMessage):


    def __init__(self, Msg,ReqId,Key,Symbol=None,UUID=None):
        super(ModelParamReq, self).__init__(Msg)
        self.UUID = UUID
        self.ReqId = ReqId
        self.Symbol = Symbol
        self.Key= Key

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)

