from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
class ErrorMessage(WebSocketMessage):
    def __init__(self, Error):
        self.Error = Error
