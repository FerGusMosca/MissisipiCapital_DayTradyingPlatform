import pyodbc
import uuid
import datetime
from sources.framework.business_entities.positions.execution_summary import *
from sources.framework.business_entities.orders.order import *
from sources.framework.common.enums.QuantityType import *
from sources.framework.common.enums.PriceType import *
from sources.framework.common.enums.OrdType import *
from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *

_CS_SEC_TYPE = "Equity"
_trade_id=0
_symbol=1
_quantity_requested=2
_quantity_filled=3
_side=4
_status=5
_leaves_quantity=6
_last_filled_time=7
_average_price=8
_order_id=9
_position_id=10
_account_id=11
_timestamp=12
_text=13
_stop_loss=14
_take_profit=15
_close_end_of_day=16

class ExecutionSummaryManager():

    #region Constructors

    def __init__(self, connString):
        self.i = 0
        self.connection = pyodbc.connect(connString)
    #endregion

    #region Private Methods

    def BuildExecutionSummary(self, row,dayTradingPos):
        newPos = Position(PosId= row[_trade_id],
                          Security=dayTradingPos.Security,
                          Side=Position.FromStrSide(str(row[_side])),
                          PriceType=PriceType.FixedAmount,
                          Qty=int(row[_quantity_requested]),
                          CumQty=int(row[_quantity_filled]),
                          QuantityType=QuantityType.SHARES,
                          Account=str(row[_account_id]),
                          Broker=None,
                          Strategy=None,
                          OrderType=OrdType.Market)

        newPos.PosStatus = Position.FromStrStatus(str(row[_status]))
        newPos.LeavesQty=int(row[_leaves_quantity])
        newPos.AvgPx= float(row[_average_price]) if row[_average_price] is not None else None
        newPos.StopLoss= float(row[_stop_loss]) if row[_stop_loss] is not None else None
        newPos.TakeProfit = float(row[_take_profit]) if row[_take_profit] is not None else None
        newPos.CloseEndOfDay = bool(row[_close_end_of_day]) if row[_close_end_of_day] is not None else None

        order = Order()
        order.OrderId=str(row[_order_id]) if row[_order_id] is not None else None
        newPos.Orders.append(order)

        summary = ExecutionSummary(datetime.now(), newPos)
        summary.LastTradeTime=datetime.strptime(str(row[_last_filled_time]), '%Y-%m-%d %H:%M:%S') if row[_last_filled_time] is not None else None
        summary.Text = str(row[_text]) if row[_text] is not None else None
        summary.AvgPx=newPos.AvgPx
        summary.CumQty=newPos.CumQty
        summary.LeavesQty=  newPos.LeavesQty if newPos.IsOpenPosition() else 0
        try:
            summary.LastUpdateTime = datetime.strptime(str(row[_timestamp]), '%Y-%m-%d %H:%M:%S.%f')
            summary.Timestamp = datetime.strptime(str(row[_timestamp]), '%Y-%m-%d %H:%M:%S.%f')
        except Exception as e:
            summary.LastUpdateTime = datetime.strptime(str(row[_timestamp]), '%Y-%m-%d %H:%M:%S')
            summary.Timestamp = datetime.strptime(str(row[_timestamp]), '%Y-%m-%d %H:%M:%S')

        return summary


    #endregion

    #region Public Methods

    def GetExecutionSummaries(self,dayTradingPos, fromDate):
        executionSummaries=[]
        with self.connection.cursor() as cursor:
            params = (dayTradingPos.Id,fromDate)
            cursor.execute("{CALL GetExecutionSummaries (?,?)}", params)

            for row in cursor:

                summary = self.BuildExecutionSummary(row,dayTradingPos)
                executionSummaries.append(summary)

        return executionSummaries

    def PersistExecutionSummary(self,summary, dayTradingPositionId):

        with self.connection.cursor() as cursor:
            params = (summary.GetTradeId(),summary.Position.Security.Symbol,int(summary.Position.Qty),
                      int(summary.CumQty if summary.CumQty is not None else 0),
                      summary.Position.GetStrSide(),summary.Position.GetStrStatus(),
                      int(summary.LeavesQty),
                      summary.LastTradeTime if summary.LastTradeTime is not None else None,
                      summary.AvgPx,
                      summary.Position.GetLastOrder().OrderId if summary.Position.GetLastOrder() is not None else None,
                      int(dayTradingPositionId) if dayTradingPositionId is not None else None,
                      summary.Position.Account,summary.Timestamp,
                      summary.Text,summary.Position.StopLoss,summary.Position.TakeProfit,summary.Position.CloseEndOfDay)
            cursor.execute("{CALL PersistExecutionSummary (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)}", params)
            self.connection.commit()

    #endregion


