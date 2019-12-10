from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
import json

class ModelParamDto:
    def __init__(self, key,symbol,intValue,stringValue,floatValue):
        self.Msg="ModelParam"
        self.Key=key
        self.Symbol =symbol
        self.IntValue = intValue
        self.StringValue = stringValue
        self.FloatValue= floatValue


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)


