from sources.framework.common.enums.Side import *
from sources.framework.common.enums.ExecType import *
from sources.framework.common.enums.OrdStatus import *


class ArQuantsTranslationHelper:

    @staticmethod
    def GetExecType(execType):
        if execType=="PendingNew":
            return  ExecType.PendingNew
        elif execType=="New":
            return  ExecType.New
        elif execType=="Canceled":
            return  ExecType.Canceled
        elif execType=="MarginRejected":
            return  ExecType.Rejected
        elif execType=="Rejected":
            return  ExecType.Rejected
        elif execType == "PartiallyFilled":
            return ExecType.Trade
        elif execType == "Filled":
            return ExecType.Trade
        elif execType == "Expired":
            return ExecType.Expired
        else:
            return ExecType.Unknown

    @staticmethod
    def GetOrdStatus(status):
        if status == "PendingNew":
            return OrdStatus.PendingNew
        elif status == "New":
            return OrdStatus.New
        elif status == "Canceled":
            return OrdStatus.Canceled
        elif status == "MarginRejected":
            return OrdStatus.Rejected
        elif status == "Rejected":
            return OrdStatus.Rejected
        elif status == "PartiallyFilled":
            return OrdStatus.PartiallyFilled
        elif status == "Filled":
            return OrdStatus.Filled
        elif status == "Expired":
            return OrdStatus.Expired
        else:
            return OrdStatus.Undefined

