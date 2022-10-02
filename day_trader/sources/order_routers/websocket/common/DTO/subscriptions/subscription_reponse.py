from sources.order_router2.websocket.common.DTO.websocket_message import *
import json


class SubscriptionResponse(WebSocketMessage):

    def __init__(self, Msg ,SubscriptionType ,Service,ServiceKey,Success,Message,UUID=None,ReqId =None):
        super(SubscriptionResponse, self).__init__(Msg)
        self.UUID = UUID
        self.SubscriptionType = SubscriptionType
        self.Service = Service
        self.ServiceKey = ServiceKey
        self.Success=Success
        self.Message=Message
        self.ReqId = ReqId

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

