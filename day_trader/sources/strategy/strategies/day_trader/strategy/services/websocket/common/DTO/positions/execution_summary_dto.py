from sources.framework.business_entities.positions.execution_summary import *

import json

class ExecutionSummaryDTO:
    def __init__(self, summary,posId):
        self.Msg="ExecutionSummary"
        self.DayTradingPositionId = posId
        self.TradeId = summary.GetTradeId()
        self.Symbol = summary.Position.Security.Symbol
        self.QuantityRequested= summary.Position.Qty
        self.QuantityFilled = summary.CumQty
        self.Side = summary.Position.GetStrSide()
        #self.Status = summary.Position.PosStatus
        self.Status = summary.Position.GetStrStatus()
        self.LeavesQty = summary.LeavesQty
        self.LastFilledTime = str(summary.LastTradeTime) if summary.LastTradeTime is not None else None
        self.AvgPx = summary.AvgPx
        self.OrderId = summary.Position.GetLastOrder().OrderId if summary.Position.GetLastOrder() is not None else ""
        self.AccountId= summary.Position.Account
        self.Timestamp = str( summary.Timestamp) if summary.Timestamp is not None else None
        self.Text = summary.Text



    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)




