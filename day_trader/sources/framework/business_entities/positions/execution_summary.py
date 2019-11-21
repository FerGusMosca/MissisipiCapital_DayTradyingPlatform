from sources.framework.business_entities.positions.position import Position
from sources.framework.business_entities.orders.execution_report import *
import datetime

_TRADE_ID_PREFIX="trd_"

class ExecutionSummary:
    def __init__(self, Date, Position):
        self.Date = Date
        self.AvgPx = None
        self.CumQty = 0
        self.LeavesQty = Position.Qty
        self.InitialPrice = Position.OrderPrice
        self.Commission = None
        self.Text = None
        self.Position = Position
        self.LastUpdateTime =datetime.datetime.now()
        self.LastTradeTime = None

    def UpdateStatus(self, execReport):
        self.CumQty = execReport.CumQty
        self.AvgPx = execReport.AvgPx
        self.Commission = execReport.Commission
        self.Text = execReport.Text

        self.Position.LeavesQty = execReport.LeavesQty
        self.Position.CumQty=execReport.CumQty
        self.Position.AvgPx=execReport.AvgPx

        self.Position.SetPositionStatusFromExecution(execReport)
        self.Position.ExecutionReports.append(execReport)
        self.LeavesQty = execReport.LeavesQty if self.Position.IsOpenPosition() else 0

        self.LastUpdateTime = datetime.datetime.now()

        if execReport.ArrivalPrice is not None:
            self.Position.ArrivalPrice=execReport.ArrivalPrice

        self.LastTradeTime=execReport.LastFillTime

        if execReport.Order is not None:
            self.Position.AppendOrder(execReport.Order)


    def GetTradeId(self):
        if(self.Position is None):
            raise Exception("Could not save execution summary without position")

        orderId=None

        if(self.Position.GetLastOrder()is None):
            orderId="-"
        else:
            orderId=self.Position.GetLastOrder().OrderId

        return "{}_{}_{}".format(_TRADE_ID_PREFIX,self.Position.Security.Symbol,orderId)