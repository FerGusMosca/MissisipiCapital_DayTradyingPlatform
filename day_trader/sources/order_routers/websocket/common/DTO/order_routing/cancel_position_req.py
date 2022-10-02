from sources.server.order_router.websocket.common.DTO.websocket_message import *
import json

class CancelPositionReq(WebSocketMessage):


    def __init__(self, Msg,ReqId,PosId=None,UUID=None):
        super(CancelPositionReq, self).__init__(Msg)
        self.PosId=PosId
        self.UUID = UUID
        self.ReqId = ReqId

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
