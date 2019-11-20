from sources.framework.business_entities.securities.security import *
import json
from json import JSONEncoder

class DayTradingPosition():

    def __init__(self,id ,security,shares,active):
        self.Id=id
        self.Security = security
        self.Shares= shares
        self.Active=active
        self.MarketData=None
        self.ExecutionSummaries={}


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)
