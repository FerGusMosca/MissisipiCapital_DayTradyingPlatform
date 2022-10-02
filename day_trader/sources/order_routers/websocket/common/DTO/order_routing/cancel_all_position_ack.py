from sources.server.order_router.websocket.common.DTO.websocket_message import *
import json

class CancelAllPositionAck(WebSocketMessage):


    def __init__(self, Msg,UUID,ReqId,Success=True,Error=None):
        super(CancelAllPositionAck, self).__init__(Msg)
        self.UUID = UUID
        self.ReqId = ReqId
        self.Success = Success
        self.Error = Error


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
