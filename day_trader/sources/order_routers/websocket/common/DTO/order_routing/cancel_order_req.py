import json


class CancelOrderReq:

    def __init__(self,OrigClOrderId=None,ClOrderId=None,OrderId=None):
        self.Msg= "CancelOrderReq"
        self.OrigClOrderId=OrigClOrderId
        self.ClOrderId=ClOrderId
        self.OrderId=OrderId

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)