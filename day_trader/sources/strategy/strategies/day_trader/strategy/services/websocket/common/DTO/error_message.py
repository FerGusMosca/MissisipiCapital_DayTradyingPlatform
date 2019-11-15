from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json
class ErrorMessage(WebSocketMessage):
    def __init__(self, Error):
        self.Error = Error

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
