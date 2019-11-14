from sources.framework.business_entities.securities.security import *
import json
from json import JSONEncoder

class SecurityToTrade():

    def __init__(self, security,shares,active):
        self.Security = security
        self.Shares= shares
        self.Active=active
        self.MarketData=None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)
