import json

from sources.framework.common.enums.SecurityType import SecurityType
from enum import IntEnum

class MarketDataRequestDTO:

    def __init__(self, Symbol=None, pSecurityType=None, Currency=None,SubscriptionRequestType=None,
                        MDReqId=None):
        self.Msg="MarketDataReq"
        self.Symbol=Symbol
        self.SecurityType=pSecurityType.name
        self.Currency=Currency
        self.SubscriptionRequestType=SubscriptionRequestType.name
        self.MDReqId=MDReqId

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)