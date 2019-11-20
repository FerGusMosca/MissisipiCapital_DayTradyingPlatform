from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.websocket_message import *
import json

class GetPositionExecutionSummariesBatch(WebSocketMessage):

    def __init__(self, Msg ,executionSummaries):
        super(GetPositionExecutionSummariesBatch, self).__init__(Msg)
        self.ExecutionSummares=executionSummaries

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

