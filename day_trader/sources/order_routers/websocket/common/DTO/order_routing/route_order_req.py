import json

from sources.framework.common.enums.Side import Side

_BUY="BUY"
_SELL="SELL"

class RouteOrderReq:


    def __init__(self, Msg,Side,ReqId,Qty, Type=None,Account=None,Symbol=None,ClOrdId=None,Price=None):
        self.Msg= str(Msg)
        self.Symbol= str(Symbol)
        self.ClOrdId = str(ClOrdId)

        self.Type="LIMIT" if Price is not None else "MARKET"
        self.Side=self.GetSide(Side)
        self.Price = float( Price) if Price is not None else None

        self.ReqId = str(ReqId)
        self.Qty = int( Qty)
        self.Account = str( Account)

    def GetSide(self,side):
        if(side==Side.Sell):
            return _SELL
        elif side==Side.SellShort:
            return _SELL
        elif side==Side.Buy:
            return _BUY
        elif side==Side.BuyToClose:
            return _BUY
        else:
            raise Exception("Could not find a translation for side {}".format(side))


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
