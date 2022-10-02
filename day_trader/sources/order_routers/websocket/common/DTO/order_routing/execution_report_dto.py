import datetime
import decimal
import json
_DATETIME_FORMAT="%d/%m/%Y %H:%M:%S"
class ExecutionReportDto:
    def __init__(self, Msg=None, Status=None,ExecType=None,OrdStatus=None,Text=None,LeavesQty=None,
                        CumQty=None,LastQty=None,
                        LastPx=None,AvgPx=None,Commission=None,
                        EffectiveTime=None,LastFilledTime=None,TransactTime=None,
                        OrderId=None,OrigClOrdId=None,ClOrdId=None,DatetimeFormat=None,** kwargs):
        self.Msg=Msg
        self.Status = Status
        self.ExecType=ExecType
        self.OrdStatus=OrdStatus
        self.Text = Text
        self.LeavesQty = int( LeavesQty) if LeavesQty is not None else None
        self.CumQty = int( CumQty) if CumQty is not None else None
        self.AvgPx = float( AvgPx) if AvgPx is not None else None
        self.LastQty=LastQty
        self.LastPx=float(LastPx) if LastPx is not None else None
        self.Commission = float(Commission) if Commission is not None else None

        datetime_format=DatetimeFormat if DatetimeFormat is not None else _DATETIME_FORMAT

        self.EffectiveTime = datetime.datetime.strptime(EffectiveTime, datetime_format) if EffectiveTime is not None else None
        self.LastFilledTime = datetime.datetime.strptime(LastFilledTime, datetime_format) if LastFilledTime is not None else None
        self.TransactTime = datetime.datetime.strptime(TransactTime,datetime_format) if TransactTime is not None else None
        self.OrderId = OrderId
        self.ClOrdId = ClOrdId
        self.OrigClOrdId=OrigClOrdId


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)