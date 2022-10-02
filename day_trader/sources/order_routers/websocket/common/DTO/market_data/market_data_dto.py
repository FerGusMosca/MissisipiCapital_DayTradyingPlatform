import decimal
import json
import datetime

class MarketDataDTO:
    def __init__(self, Msg=None,Symbol=None, MDLocalEntryDate=None, DateTimeFormat = None, Trade=None,MDTradeSize=None,
                     BestBidPrice=None,BestBidSize=None,BestAskPrice=None,BestAskSize=None,** kwargs ):
        self.Msg = Msg

        try:
            if(MDLocalEntryDate is not None):
                self.MDLocalEntryDate = datetime.datetime.strptime(MDLocalEntryDate, DateTimeFormat) if DateTimeFormat is not None else datetime.datetime.strptime(MDLocalEntryDate, "%d/%m/%Y %H:%M")
            else:
                self.MDLocalEntryDate=datetime.datetime.now()
        except Exception as e:
            self.MDLocalEntryDate = datetime.datetime.now()

        self.Symbol = Symbol
        self.Trade = float (Trade) if Trade is not None else None
        self.MDTradeSize = float(MDTradeSize) if MDTradeSize is not None else None
        self.BestBidPrice = float(BestBidPrice) if BestBidPrice is not None else None
        self.BestAskPrice = float(BestAskPrice) if BestAskPrice is not None else None
        self.BestBidSize = float(BestBidSize) if BestBidSize is not None else None
        self.BestAskSize = float(BestAskSize) if BestAskSize is not None else None


def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
