import json

from sources.order_routers.websocket.common.DTO.websocket_message import *


class WebSocketSubscribeMessage(WebSocketMessage):


    @staticmethod
    def _SUBSCRIPTION_TYPE_UNSUBSCRIBE():
        return "U"

    @staticmethod
    def _SUBSCRIPTION_TYPE_SUBSCRIBE():
        return "S"

    def __init__(self, Msg ,SubscriptionType ,Service,ServiceKey,UUID=None, ReqId = None):
        super(WebSocketSubscribeMessage, self).__init__(Msg)
        self.UUID = UUID
        self.SubscriptionType = SubscriptionType
        self.Service = Service
        self.ServiceKey = ServiceKey
        self.ReqId = ReqId

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


