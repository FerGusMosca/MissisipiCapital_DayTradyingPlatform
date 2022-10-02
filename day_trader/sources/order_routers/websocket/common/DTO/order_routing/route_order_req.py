import json

class RouteOrderReq:


    def __init__(self, Msg,Side,ReqId,Qty, Type=None,Account=None,Symbol=None,ClOrdId=None,Price=None):
        self.Msg= str(Msg)
        self.Symbol= str(Symbol)
        self.ClOrdId = str(ClOrdId)

        self.Type="LIMIT" if Price is not None else "MARKET"
        self.Side="BUY" if Side==Side.Buy else "SELL"
        self.Price = float( Price) if Price is not None else None

        self.ReqId = str(ReqId)
        self.Qty = int( Qty)
        self.Account = str( Account)



    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
