from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *


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


