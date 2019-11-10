from sources.framework.common.enums.PositionsStatus import PositionStatus
from sources.framework.common.enums.ExecType import *
from sources.framework.common.enums.PriceType import PriceType
from sources.framework.common.enums.QuantityType import QuantityType
from sources.framework.common.enums.OrdType import *

class Position:
    def __init__(self, PosId=None, Security=None,Side=None,PriceType=None,Qty=None,QuantityType=None,Account=None,
                Broker=None,Strategy=None,OrderType=None, OrderPrice = None, CumQty=None, LeavesQty = None,
                 AvgPx=None, LastQty=None,LastPx=None,LastMkt=None):

        #region Attributes
        self.PosId=PosId
        self.Security=Security
        self.PosStatus=PositionStatus.New
        self.Side=Side
        self.Qty=Qty
        self.QuantityType=QuantityType
        self.Exchange=None
        self.PriceType=PriceType
        self.CumQty = CumQty
        self.LeavesQty = LeavesQty
        self.AvgPx = AvgPx
        self.LastQty = LastQty
        self.LastPx = LastPx
        self.LastMkt = LastMkt

        self.CashQty=None
        self.Percent =None

        self.ExecutionReports=[]
        self.Orders=[]

        self.PositionRejectReason = None
        self.PositionRejectText = None
        self.Account = Account

        self.Broker=Broker
        self.Strategy=Strategy
        self.OrderType=OrderType
        self.OrderPrice = OrderPrice

        self.ArrivalPrice= None




        #endregion


        #region Public Methods

    def SetPositionStatusFromExecution(self,execReport):
        """

        Args:
            execReport ():
        """

        execType=execReport.ExecType

        if execType==ExecType.New:
            self.PosStatus=PositionStatus.New
        elif execType==ExecType.DoneForDay:
            self.PosStatus=PositionStatus.DoneForDay
        elif execType==ExecType.Canceled:
            self.PosStatus=PositionStatus.Canceled
        elif execType==ExecType.Replaced:
            self.PosStatus=PositionStatus.Replaced
        elif execType==ExecType.PendingCancel:
            self.PosStatus=PositionStatus.PendingCancel
        elif execType==ExecType.Stopped:
            self.PosStatus=PositionStatus.Stopped
        elif execType==ExecType.Rejected:
            self.PosStatus=PositionStatus.Rejected
        elif execType==ExecType.Suspended:
            self.PosStatus=PositionStatus.Suspended
        elif execType==ExecType.PendingNew:
            self.PosStatus=PositionStatus.PendingNew
        elif execType==ExecType.Calculated:
            self.PosStatus=PositionStatus.Calculated
        elif execType==ExecType.Expired:
            self.PosStatus=PositionStatus.Expired
        elif execType==ExecType.PendingReplace:
            self.PosStatus=PositionStatus.PendingReplace
        elif execType==ExecType.Trade:
            self.PosStatus=PositionStatus.Filled if execReport.LeavesQty==0 else PositionStatus.PartiallyFilled
        else:
            raise Exception("Unknown exec type {}".format(execType))



        #endregion

    def IsOpenPosition(self):
        return self.PosStatus == PositionStatus.New or self.PosStatus == PositionStatus.PendingNew \
               or self.PosStatus == PositionStatus.PartiallyFilled or self.PosStatus == PositionStatus.Replaced \
               or self.PosStatus == PositionStatus.PendingCancel or self.PosStatus == PositionStatus.Calculated \
               or self.PosStatus == PositionStatus.PendingReplace or self.PosStatus == PositionStatus.AcceptedForBidding \
               or self.PosStatus == PositionStatus.PendingCancel

    def IsFinishedPosition(self):
        """

        Returns:

        """
        if (self.PosStatus == PositionStatus.Filled
            or self.PosStatus == PositionStatus.DoneForDay
            or self.PosStatus == PositionStatus.Stopped
            or self.PosStatus == PositionStatus.Rejected
            or self.PosStatus == PositionStatus.Suspended
            or self.PosStatus == PositionStatus.Expired
            or self.PosStatus == PositionStatus.Canceled):
            return True
        else:
            return  False

    def IsTradedPosition(self):
        """

        Returns:

        """
        if (self.PosStatus == PositionStatus.Filled
            or self.PosStatus == PositionStatus.PartiallyFilled):
            return True
        else:
            return  False

    def ValidateNewPosition(self):
        """

        """
        if(self.OrderType is not None):

            if  self.OrderType==OrdType.Market and self.OrderPrice is not None:
                raise Exception("You cannot specify a limit price for a market position. Symbol {}".format(self.Security.Symbol))

    def GetLastExecutionReport(self):

        if len(self.ExecutionReports)>0:
            execList = sorted(self.ExecutionReports, key=lambda execRep: execRep.TransactTime, reverse=True)
            return execList[0]
        else:
            return None

    def GetLastOrder(self):

        if len(self.Orders)>0:
            ordList = sorted(self.Orders, key=lambda order: order.ClOrdId, reverse=True)
            return ordList[0]
        else:
            return None

    def GetFirstTradeExecutionReport(self):

        if len(self.ExecutionReports)>0:
            execList = sorted(self.ExecutionReports, key=lambda execRep: execRep.TransactTime is not None, reverse=False)
            if len(execList)>0:
                return execList[0]
            else:
                return None
        else:
            return None

    def AppendOrder(self,order):
        ordersInMem = list(filter(lambda x: x.OrderId == order.OrderId, self.Orders))

        if len(ordersInMem)>0:
            ordersInMem[0]=order
        else:
            self.Orders.append(order)

    @staticmethod
    def CountOpenPositions(self, positions):
        i=0

        for pos in positions:
            if not pos.IsFinishedPosition():
                i+=1

        return i


    def GetMarketArrivalTime(self):

        try:
            if self.GetLastOrder() is not None:
                if self.GetLastOrder().MarketArrivalTime is not None:
                    return self.GetLastOrder().MarketArrivalTime
                else:
                    return "1900-01-01"
            else:
                return "1900-01-01"
        except Exception as e:
            return "1900-01-01"