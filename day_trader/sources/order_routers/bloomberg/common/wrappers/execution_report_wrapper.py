import blpapi
from blpapi import SessionOptions, Session
from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.execution_report_field import *
from sources.framework.common.enums.ExecType import *
from sources.framework.common.enums.OrdStatus import *
from sources.order_routers.bloomberg.common.util.bloomberg_translation_helper import *
import datetime


class ExecutionReportWrapper(Wrapper):
    def __init__(self, pOrder, pMessage, pParent = None):
        self.Message = pMessage
        self.Order = pOrder
        self.Parent = pParent

    def GetExecType(self):
        return BloombergTranslationHelper.GetExecType(self.Parent, self.Message)

    def GetOrdStatus(self):
        return BloombergTranslationHelper.GetOrdStatus(self.Parent, self.Message)

    def GetExecId(self):
        return BloombergTranslationHelper.GetFillId(self.Parent, self.Message)

    def GetCumQty(self):
        return BloombergTranslationHelper.GetSafeFloat(self.Parent,self.Message,"EMSX_FILLED",0)

    def GetLeavesQty(self):
        if(self.Order is not None and self.Order.OrderQty is not None):
            return self.Order.OrderQty - self.GetCumQty()
        else:
            return 0

    def GetAvgPx(self):
        return BloombergTranslationHelper.GetSafeFloat(self.Parent, self.Message, "EMSX_AVG_PRICE", 0)

    def GetLastFillTime(self):
        return BloombergTranslationHelper.GetTimeFromDate(self.Parent,self.Message,"EMSX_LAST_FILL_DATE","EMSX_LAST_FILL_TIME")

    def GetArrivalPrice(self):
        return BloombergTranslationHelper.GetSafeFloat(self.Parent, self.Message, "EMSX_ARRIVAL_PRICE", 0)

    def GetRejReason(self):
        return ""

    def GetTransactTime(self):
        try:
            if self.Message.hasElement("EMSX_TIME_STAMP"):
                return BloombergTranslationHelper.GetTimeFromEpoch(self.Parent, self.Message, "EMSX_TIME_STAMP")
            else:
                return None
        except Exception as e:
            return None

    def GetLastQty(self):
        return BloombergTranslationHelper.GetSafeFloat(self.Parent, self.Message, "EMSX_LAST_SHARES", 0)

    def GetLastPx(self):
        return BloombergTranslationHelper.GetSafeFloat(self.Parent, self.Message, "EMSX_LAST_PRICE", 0)

    # region Public Methods

    def GetAction(self):
        return Actions.EXECUTION_REPORT

    def GetField(self, field):
        if field == None:
            return None

        if field == ExecutionReportField.ExecType:
            return self.GetExecType()
        elif field == ExecutionReportField.ExecID:
            return self.GetExecId()
        elif field == ExecutionReportField.OrdStatus:
            return self.GetOrdStatus()
        elif field == ExecutionReportField.OrdRejReason:
            return None
        elif field == ExecutionReportField.LeavesQty:
            return self.GetLeavesQty()
        elif field == ExecutionReportField.CumQty:
            return self.GetCumQty()
        elif field == ExecutionReportField.AvgPx:
            return self.GetAvgPx()
        elif field == ExecutionReportField.Commission:
            return  BloombergTranslationHelper.GetSafeFloat(self.Parent, self.Message, "EMSX_BROKER_COMM", 0)
        elif field == ExecutionReportField.Text:
            return BloombergTranslationHelper.GetSafeString(self.Parent, self.Message, "EMSX_REASON_DESC", "")
        elif field == ExecutionReportField.TransactTime:
            return self.GetTransactTime()
        elif field == ExecutionReportField.LastQty:
            return self.GetLastQty()
        elif field == ExecutionReportField.LastPx:
            return self.GetLastPx()
        elif field == ExecutionReportField.LastMkt:
            return BloombergTranslationHelper.GetSafeFloat(self.Parent, self.Message, "EMSX_LAST_MARKET", 0)
        elif field == ExecutionReportField.OrderID:
            return self.Order.OrderId if self.Order is not None else None
        elif field == ExecutionReportField.Currency:
            return self.Order.Currency if self.Order is not None else None
        elif field == ExecutionReportField.ClOrdID:
            return self.Order.ClOrdId if self.Order is not None else None
        elif field == ExecutionReportField.OrigClOrdID:
            return self.Order.OrigClOrdId if self.Order is not None else None
        elif field == ExecutionReportField.Symbol:
            return self.Order.Security.Symbol if (self.Order is not None and self.Order.Security is not None) else None
        elif field == ExecutionReportField.OrderQty:
            return self.Order.OrderQty if self.Order is not None else None
        elif field == ExecutionReportField.CashOrderQty:
            return None
        elif field == ExecutionReportField.OrdType:
            return self.Order.OrdType if self.Order is not None else None
        elif field == ExecutionReportField.Price:
            return self.Order.Price if self.Order is not None else None
        elif field == ExecutionReportField.StopPx:
            return self.Order.StopPx if self.Order is not None else None
        elif field == ExecutionReportField.Currency:
            return self.Order.Currency if self.Order is not None else None
        elif field == ExecutionReportField.ExpireDate:
            return None
        elif field == ExecutionReportField.MinQty:
            return None
        elif field == ExecutionReportField.Side:
            return self.Order.Side if self.Order is not None else None
        elif field == ExecutionReportField.QuantityType:
            return self.Order.QuantityType if self.Order is not None else None
        elif field == ExecutionReportField.PriceType:
            return self.Order.PriceType if self.Order is not None else None
        elif field == ExecutionReportField.Order:
            return self.Order if self.Order is not None else None
        elif field == ExecutionReportField.ArrivalPrice:
            return self.GetArrivalPrice()
        elif field == ExecutionReportField.LastFillTime:
            return self.GetLastFillTime()
        else:
            return None

    # endregion
