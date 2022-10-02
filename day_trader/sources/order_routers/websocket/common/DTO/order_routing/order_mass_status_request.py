import json


class OrderMassStatusRequest:

    def __init__(self):
        self.Msg= "OrderMassStatusRequest"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)