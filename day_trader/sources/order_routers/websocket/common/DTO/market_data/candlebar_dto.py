from datetime import datetime

from sources.framework.business_entities.securities.security import Security

_DATETIME_FORMAT="%d-%m-%Y %H:%M:%S"
class CandlebarDTO:
    def __init__(self, Msg=None, Symbol=None,Key=None,Date=None,High=None,Open=None,Low=None,Close=None,Trade=None,
                        Volume=None,** kwargs):
        self.Msg = Msg
        self.Symbol=Symbol
        self.Key=Key

        self.High=High
        self.Open=Open
        self.Low=Low
        self.Close=Close
        self.Trade=Trade
        self.Volume=Volume

        self.Security=Security(Symbol)
        self.Date = datetime.strptime(Date,_DATETIME_FORMAT) if Date is not None else None
