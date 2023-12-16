import json

from sources.framework.common.enums.OrdType import OrdType
from sources.framework.common.enums.Side import Side
from sources.framework.common.enums.TimeInForce import TimeInForce


class UpdateOrderReq:



    def __init__(self, Msg,OrigClOrdId=None,ClOrdId=None,pSymbol=None,pPrice=None,pOrdType=None,pSide=None,pTimeInforce=None,pOrdQty=None):
        self.Msg= str(Msg)
        self.OrigClOrdId= str(OrigClOrdId)
        self.ClOrdId = str(ClOrdId)
        self.Symbol=pSymbol
        self.Price = float( pPrice) if pPrice is not None else None
        self.OrdType=pOrdType.name
        self.Side=pSide.name
        self.TimeInForce=pTimeInforce.name
        self.Qty=float(pOrdQty)


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)
