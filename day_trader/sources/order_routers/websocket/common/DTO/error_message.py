from sources.server.order_router.websocket.common.DTO.websocket_message import *
import json
class ErrorMessage(WebSocketMessage):
    def __init__(self, Error):
        self.Msg= "ErrorMessage"
        self.Error = Error

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
