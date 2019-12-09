from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class GetHistoricalPricesBatch(WebSocketMessage):

    def __init__(self, Msg ,symbol,historicalPrices):
        super(GetHistoricalPricesBatch, self).__init__(Msg)
        self.Symbol = symbol
        self.HistoricalPrices=historicalPrices

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

