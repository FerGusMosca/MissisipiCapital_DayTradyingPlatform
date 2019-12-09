from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class HistoricalPricesReq(WebSocketMessage):


    def __init__(self, Msg,ReqId,Symbol=None,From=None,To=None,UUID=None):
        super(HistoricalPricesReq, self).__init__(Msg)
        self.Symbol=Symbol
        self.From=From
        self.To = To
        self.UUID = UUID
        self.ReqId = ReqId

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
