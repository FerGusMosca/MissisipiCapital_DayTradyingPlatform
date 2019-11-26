import pymssql
import uuid
import datetime
from sources.framework.business_entities.positions.execution_summary import *
from sources.framework.business_entities.orders.order import *
from sources.framework.common.enums.QuantityType import *
from sources.framework.common.enums.PriceType import *
from sources.framework.common.enums.OrdType import *
from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *

_CS_SEC_TYPE = "Equity"

class ExecutionSummaryManager():

    #region Constructors

    def __init__(self, host, port, database, user, password):
        self.ConnParams = {}

        self.ConnParams["host"] = host
        self.ConnParams["port"] = port
        self.ConnParams["database"] = database
        self.ConnParams["user"] = user
        self.ConnParams["password"] = password
        self.i = 0
        self.connection = pymssql.connect(server=host, user=user, password=password, database=database)
    #endregion

    #region Private Methods

    def BuildExecutionSummary(self, row,dayTradingPos):
        newPos = Position(PosId= row["trade_id"],
                          Security=dayTradingPos.Security,
                          Side=Position.FromStrSide(str(row["side"])),
                          PriceType=PriceType.FixedAmount,
                          Qty=int(row["quantity_requested"]),
                          CumQty=int(row["quantity_filled"]),
                          QuantityType=QuantityType.SHARES,
                          Account=str(row["account_id"]),
                          Broker=None,
                          Strategy=None,
                          OrderType=OrdType.Market)

        newPos.PosStatus = Position.FromStrStatus(str(row["status"]))
        newPos.LeavesQty=int(row["leaves_quantity"])
        newPos.AvgPx= float(row["average_price"]) if row["average_price"] is not None else None


        order = Order()
        order.OrderId=str(row["order_id"]) if row["order_id"] is not None else None
        newPos.Orders.append(order)

        summary = ExecutionSummary(datetime.now(), newPos)
        summary.LastTradeTime=datetime.strptime(str(row["last_filled_time"]), '%Y-%m-%d %H:%M:%S') if row["last_filled_time"] is not None else None
        summary.Text = str(row["text"]) if row["text"] is not None else None
        summary.AvgPx=newPos.AvgPx
        summary.CumQty=newPos.CumQty
        summary.LeavesQty=  newPos.LeavesQty if newPos.IsOpenPosition() else 0
        try:
            summary.LastUpdateTime = datetime.strptime(str(row["timestamp"]), '%Y-%m-%d %H:%M:%S.%f')
            summary.Timestamp = datetime.strptime(str(row["timestamp"]), '%Y-%m-%d %H:%M:%S.%f')
        except Exception as e:
            summary.LastUpdateTime = datetime.strptime(str(row["timestamp"]), '%Y-%m-%d %H:%M:%S')
            summary.Timestamp = datetime.strptime(str(row["timestamp"]), '%Y-%m-%d %H:%M:%S')

        return summary


    #endregion

    #region Public Methods

    def GetExecutionSummaries(self,dayTradingPos, fromDate):
        executionSummaries=[]
        with self.connection.cursor(as_dict=True) as cursor:
            params = (dayTradingPos.Id,fromDate)
            cursor.callproc("GetExecutionSummaries", params)

            for row in cursor:

                summary = self.BuildExecutionSummary(row,dayTradingPos)
                executionSummaries.append(summary)

        return executionSummaries

    def PersistExecutionSummary(self,summary, dayTradingPositionId):

        with self.connection.cursor(as_dict=True) as cursor:
            params = (summary.GetTradeId(),summary.Position.Security.Symbol,int(summary.Position.Qty),
                      int(summary.CumQty if summary.CumQty is not None else 0),
                      summary.Position.GetStrSide(),summary.Position.GetStrStatus(),
                      int(summary.LeavesQty),
                      summary.LastTradeTime if summary.LastTradeTime is not None else None,
                      summary.AvgPx,
                      summary.Position.GetLastOrder().OrderId if summary.Position.GetLastOrder() is not None else None,
                      int(dayTradingPositionId) if dayTradingPositionId is not None else None,
                      summary.Position.Account,summary.Timestamp,
                      summary.Text)
            cursor.callproc("PersistExecutionSummary", params)
            self.connection.commit()

    #endregion


