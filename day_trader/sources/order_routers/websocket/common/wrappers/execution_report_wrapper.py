from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.execution_report_field import *
from sources.framework.common.enums.SubscriptionRequestType import *
from sources.order_routers.websocket.common.util.ar_quants_translation_helper import *
from sources.framework.common.enums.OrdType import *
import datetime


_CURRENCY="USD"
_EXCHANGE="US"

class ExecutionReportWrapper(Wrapper):
    def __init__(self, pExecutionReport,pOrder):
        self.ExecutionReport=pExecutionReport
        self.Order = pOrder


    #region Private Methods

    def GetExecType(self):
        return ArQuantsTranslationHelper.GetExecType(self.ExecutionReport.Status)

    def GetOrdStatus(self):
        return ArQuantsTranslationHelper.GetOrdStatus(self.ExecutionReport.Status)


    #endregion

    # region Public Methods

    def GetAction(self):
        return Actions.EXECUTION_REPORT

    def GetField(self, field):
        if field is None:
            return None

        if field == ExecutionReportField.ExecType:
            return self.GetExecType()
        elif field == ExecutionReportField.ExecID:
            return None  # default
        elif field == ExecutionReportField.OrdStatus:
            return self.GetOrdStatus()
        elif field == ExecutionReportField.OrdRejReason:
            return None
        elif field == ExecutionReportField.LeavesQty:
            return self.ExecutionReport.LeavesQty
        elif field == ExecutionReportField.CumQty:
            return self.ExecutionReport.CumQty
        elif field == ExecutionReportField.AvgPx:
            return self.ExecutionReport.AvgPx
        elif field == ExecutionReportField.Commission:
            return None  # default
        elif field == ExecutionReportField.Text:
            return self.ExecutionReport.Text
        elif field == ExecutionReportField.TransactTime:
            return datetime.datetime.now()  # default
        elif field == ExecutionReportField.LastQty:
            return self.ExecutionReport.LastQty
        elif field == ExecutionReportField.LastPx:
            return self.ExecutionReport.AvgPx
        elif field == ExecutionReportField.LastMkt:
            return None
        elif field == ExecutionReportField.MarketArrivalTime:
            return self.ExecutionReport.EffectiveTime

        if(self.Order is not None):
            if field == ExecutionReportField.OrderID:
                return self.Order.OrderId
            elif field == ExecutionReportField.ClOrdID:
                return self.Order.ClOrdId
            elif field == ExecutionReportField.OrigClOrdID:
                return self.Order.OrigClOrdId
            elif field == ExecutionReportField.Symbol:
                return self.Order.Security.Symbol
            elif field == ExecutionReportField.OrderQty:
                return self.Order.OrderQty
            elif field == ExecutionReportField.CashOrderQty:
                return None
            elif field == ExecutionReportField.OrdType:
                return self.Order.OrdType
            elif field == ExecutionReportField.Price:
                return self.Order.Price
            elif field == ExecutionReportField.StopPx:
                return self.Order.StopPx
            elif field == ExecutionReportField.Currency:
                return self.Order.Currency
            elif field == ExecutionReportField.ExpireDate:
                return None
            elif field == ExecutionReportField.MinQty:
                return None
            elif field == ExecutionReportField.Side:
                return self.Order.Side
            elif field == ExecutionReportField.QuantityType:
                return self.Order.QuantityType
            elif field == ExecutionReportField.PriceType:
                return self.Order.PriceType
            elif field == ExecutionReportField.Order:
                return self.Order


            else:
                return None
        else:
            return None

    # endregion


