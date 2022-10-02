import json

class UpdateOrderReq:


    def __init__(self, Msg,OrigClOrdId=None,ClOrdId=None,Price=None):
        self.Msg= str(Msg)
        self.OrigClOrdId= str(OrigClOrdId)
        self.ClOrdId = str(ClOrdId)
        self.Price = float( Price) if Price is not None else None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)