import json

class UpdateOrderReq:


    def __init__(self, Msg,OrigClOrdId=None,ClOrdId=None,pSymbol=None,pPrice=None,pOrdType=None,pSide=None,pTimeInforce=None,pOrdQty=None):
        self.Msg= str(Msg)
        self.OrigClOrdId= str(OrigClOrdId)
        self.ClOrdId = str(ClOrdId)
        self.Symbol=pSymbol
        self.Price = float( pPrice) if pPrice is not None else None
        self.OrdType=pOrdType
        self.Side=pSide
        self.TimeInForce=pTimeInforce
        self.OrdQty=pOrdQty

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)