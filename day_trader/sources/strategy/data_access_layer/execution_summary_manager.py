import pymssql
from sources.framework.business_entities.positions.execution_summary import *
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

    #region Public Methods

    def PersistExecutionSummary(self,summary, dayTradingPositionId):

        with self.connection.cursor(as_dict=True) as cursor:
            params = (summary.GetTradeId(),summary.Position.Security.Symbol,int(summary.Position.Qty),
                      int(summary.Position.CumQty if summary.Position.CumQty is not None else 0),
                      summary.Position.GetStrSide(),summary.Position.GetStrStatus(),
                      int(summary.Position.LeavesQty),summary.LastTradeTime,summary.AvgPx,
                      summary.Position.GetLastOrder().OrderId if summary.Position.GetLastOrder() is not None else None,
                      int(dayTradingPositionId) if dayTradingPositionId is not None else None,
                      summary.Position.Account,summary.LastUpdateTime)
            cursor.callproc("PersistExecutionSummary", params)
            self.connection.commit()

    #endregion


