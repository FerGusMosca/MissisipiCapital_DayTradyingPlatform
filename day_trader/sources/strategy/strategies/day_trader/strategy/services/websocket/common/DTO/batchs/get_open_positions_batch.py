from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class GetOpenPositionsBatch(WebSocketMessage):

    def __init__(self, Msg ,positions):
        super(GetOpenPositionsBatch, self).__init__(Msg)
        self.Positions=positions

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

