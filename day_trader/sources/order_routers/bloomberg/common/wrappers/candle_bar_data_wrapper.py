from sources.framework.common.enums.Actions import *
from sources.framework.common.wrappers.wrapper import *
from sources.framework.common.enums.TimeUnit import *
from sources.framework.common.enums.fields.candle_bar_field import *
from sources.order_routers.bloomberg.common.util.bloomberg_translation_helper import *

class CandleBarDataWrapper(Wrapper):

    def __init__(self,pLogger,pCandlebar):

        self.Logger = pLogger
        self.Candlebar=pCandlebar

    # region Public Methods

    def GetAction(self):
        return Actions.CANDLE_BAR_DATA

    def GetField(self, field):

        if field == None:
            return None

        if field == CandleBarField.Time:
            return self.Candlebar.Time
        elif field == CandleBarField.Open:
            return self.Candlebar.Open
        elif field == CandleBarField.Close:
            return self.Candlebar.Close
        elif field == CandleBarField.High:
            return self.Candlebar.High
        elif field == CandleBarField.Low:
            return self.Candlebar.Low
        elif field == CandleBarField.NumberOfTicks:
            return self.Candlebar.NumberOfTicks
        elif field == CandleBarField.Value:
            return self.Candlebar.Value
        elif field == CandleBarField.Volume:
            return self.Candlebar.Volume
        elif field == CandleBarField.DateTime:
            return self.Candlebar.DateTime
        elif field == CandleBarField.Security:
            return self.Candlebar.Security
        else:
            return None


    # endregion
