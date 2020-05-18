from sources.framework.business_entities.positions.position import Position
from sources.framework.business_entities.orders.execution_report import *
import datetime
from sources.framework.common.enums.Side import *

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
        self.Timestamp = datetime.datetime.now()
        self.LastTradeTime = None
        self.CreateTime= datetime.datetime.now()

    def UpdateStatus(self, execReport,marketDataToUse=None):

        self.CumQty = execReport.CumQty
        self.AvgPx = execReport.AvgPx if marketDataToUse is None else marketDataToUse.Trade
        self.Commission = execReport.Commission
        self.Text = execReport.Text if execReport.Text is not None and execReport.Text!="" else self.Text

        self.Position.LeavesQty = execReport.LeavesQty
        self.Position.CumQty=execReport.CumQty
        self.Position.AvgPx=execReport.AvgPx

        self.Position.SetPositionStatusFromExecution(execReport)
        self.Position.ExecutionReports.append(execReport)
        self.LeavesQty = execReport.LeavesQty if self.Position.IsOpenPosition() else 0

        self.LastUpdateTime =  datetime.datetime.now()
        if(execReport.LastFillTime is not None):
            self.Timestamp = execReport.LastFillTime

        if execReport.ArrivalPrice is not None:
            self.Position.ArrivalPrice=execReport.ArrivalPrice

        self.LastTradeTime=execReport.LastFillTime

        if execReport.Order is not None:
            self.Position.AppendOrder(execReport.Order)

    def GetTradedSummary(self):
        if self.CumQty>0 and self.AvgPx is not None:
            return self.CumQty*self.AvgPx
        else:
            return 0

    def GetNetShares(self):
        return self.CumQty if self.CumQty is not None else 0

    def SharesAcquired(self):
        return self.Position.Side==Side.Buy or self.Position.Side==Side.BuyToClose

    def GetTradeId(self):
        if(self.Position is None):
            raise Exception("Could not save execution summary without position")

        orderId=None

        if (self.Position.IsRejectedPosition()):
            orderId= "R" + str( self.CreateTime.timestamp()) if self.CreateTime is not None else "R?"
        elif(self.Position.GetLastOrder()is None):
            orderId="nO" + str( self.CreateTime.timestamp()) if self.CreateTime is not None else "nO?"
        else:
            orderId=self.Position.GetLastOrder().OrderId

        return "{}_{}_{}".format(_TRADE_ID_PREFIX,self.Position.Security.Symbol,orderId)