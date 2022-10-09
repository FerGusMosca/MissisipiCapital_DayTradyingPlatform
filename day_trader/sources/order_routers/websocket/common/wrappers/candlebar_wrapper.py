from sources.framework.common.enums.Actions import Actions
from sources.framework.common.enums.fields.candle_bar_field import CandleBarField
from sources.framework.common.wrappers.wrapper import Wrapper


class CandlebarWrapper(Wrapper):

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
            return self.Candlebar.Key
        elif field == CandleBarField.Open:
            return self.Candlebar.Open
        elif field == CandleBarField.Close:
            return self.Candlebar.Close
        elif field == CandleBarField.High:
            return self.Candlebar.High
        elif field == CandleBarField.Low:
            return self.Candlebar.Low
        elif field == CandleBarField.NumberOfTicks:
            return None
        elif field == CandleBarField.Value:
            return self.Candlebar.Trade
        elif field == CandleBarField.Volume:
            return self.Candlebar.Volume
        elif field == CandleBarField.DateTime:
            return self.Candlebar.Date
        elif field == CandleBarField.Security:
            return self.Candlebar.Security
        else:
            return None


    # endregion