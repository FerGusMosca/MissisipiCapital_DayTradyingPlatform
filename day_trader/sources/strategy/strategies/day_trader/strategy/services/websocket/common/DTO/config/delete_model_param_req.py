from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class DeleteModelParamReq(WebSocketMessage):


    def __init__(self, Msg,ReqId,Key=None,Symbol=None,StringValue=None,IntValue=None,FloatValue=None,UUID=None):
        super(DeleteModelParamReq, self).__init__(Msg)

        self.UUID = UUID
        self.ReqId = ReqId
        self.Key=Key
        self.Symbol=Symbol


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
