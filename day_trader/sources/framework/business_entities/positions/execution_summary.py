from sources.framework.business_entities.positions.position import Position
from sources.framework.business_entities.orders.execution_report import *
import datetime


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
        """ Update execution summary fields with execution report data.

        Args:
            execReport (:obj:`ExecutionReport`): Execution report data as input.
        """
        self.CumQty = execReport.CumQty
        self.LeavesQty = execReport.LeavesQty
        self.AvgPx = execReport.AvgPx
        self.Commission = execReport.Commission
        self.Text = execReport.Text
        self.Position.LeavesQty = execReport.LeavesQty
        self.Position.SetPositionStatusFromExecution(execReport)
        self.Position.ExecutionReports.append(execReport)

        self.LastUpdateTime = datetime.datetime.now()

        if execReport.ArrivalPrice is not None:
            self.Position.ArrivalPrice=execReport.ArrivalPrice

        if self.Position.IsTradedPosition():
            self.LastTradeTime=execReport.TransactTime

        if execReport.Order is not None:
            self.Position.AppendOrder(execReport.Order)
