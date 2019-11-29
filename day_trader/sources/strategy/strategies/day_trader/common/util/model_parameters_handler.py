from sources.strategy.strategies.day_trader.business_entities.model_parameter import *

_KEY_CHAR="$$"

class ModelParametersHandler:
    def __init__(self,pModelParameters):

        self.ModelParametersDict ={}
        for modelParam in pModelParameters:
            if modelParam.Symbol is not None:
                self.ModelParametersDict[modelParam.Symbol+_KEY_CHAR+modelParam.Key]=modelParam
            else:
                self.ModelParametersDict[modelParam.Key] = modelParam


    #region Static Attributes

    @staticmethod
    def TRADING_MODE():
        return "TRADING_MODE"

    @staticmethod
    def DAILY_BIAS():
        return "DAILY_BIAS"

    @staticmethod
    def BAR_FREQUENCY():
        return "BAR_FREQUENCY"

    @staticmethod
    def DAILY_SLOPE():
        return "DAILY_SLOPE"

    @staticmethod
    def MAXIM_PCT_CHANGE_3_MIN():
        return "MAXIM_PCT_CHANGE_3_MIN"

    @staticmethod
    def POS_LONG_MAX_DELTA():
        return "POS_LONG_MAX_DELTA"

    @staticmethod
    def POS_SHORT_MAX_DELTA():
        return "POS_SHORT_MAX_DELTA"

    @staticmethod
    def MAX_GAIN_FOR_DAY():
        return "MAX_GAIN_FOR_DAY"

    @staticmethod
    def PCT_MAX_GAIN_CLOSING():
        return "PCT_MAX_GAIN_CLOSING"

    @staticmethod
    def MAX_LOSS_FOR_DAY():
        return "MAX_LOSS_FOR_DAY"

    @staticmethod
    def PCT_MAX_LOSS_CLOSING():
        return "PCT_MAX_LOSS_CLOSING"

    @staticmethod
    def TAKE_GAIN_LIMIT():
        return "TAKE_GAIN_LIMIT"

    @staticmethod
    def STOP_LOSS_LIMIT():
        return "STOP_LOSS_LIMIT"

    @staticmethod
    def PCT_SLOPE_TO_CLOSE_LONG():
        return "PCT_SLOPE_TO_CLOSE_LONG"

    @staticmethod
    def PCT_SLOPE_TO_CLOSE_SHORT():
        return "PCT_SLOPE_TO_CLOSE_SHORT"

    @staticmethod
    def BACKWARD_DAYS_SUMMARIES_IN_MEMORY():
        return "BACKWARD_DAYS_SUMMARIES_IN_MEMORY"

    @staticmethod
    def HISTORICAL_PRICES_PAST_DAYS():
        return "HISTORICAL_PRICES_PAST_DAYS"

    @staticmethod
    def HISTORICAL_PRICES_CAL_DAYS_TO_REQ():
        return "HISTORICAL_PRICES_CAL_DAYS_TO_REQ"

    @staticmethod
    def LOW_VOL_ENTRY_THRESHOLD():
        return "LOW_VOL_ENTRY_THRESHOLD"

    @staticmethod
    def HIGH_VOL_ENTRY_THRESHOLD():
        return "HIGH_VOL_ENTRY_THRESHOLD"

    @staticmethod
    def LOW_VOL_FROM_TIME():
        return "LOW_VOL_FROM_TIME"

    @staticmethod
    def LOW_VOL_TO_TIME():
        return "LOW_VOL_TO_TIME"

    @staticmethod
    def HIGH_VOL_FROM_TIME_1():
        return "HIGH_VOL_FROM_TIME_1"

    @staticmethod
    def HIGH_VOL_TO_TIME_1():
        return "HIGH_VOL_TO_TIME_1"

    @staticmethod
    def HIGH_VOL_FROM_TIME_2():
        return "HIGH_VOL_FROM_TIME_2"

    @staticmethod
    def HIGH_VOL_TO_TIME_2():
        return "HIGH_VOL_TO_TIME_2"

    #endregion

    #region Public Methods

    def Get(self, key, symbol=None):

        finalKey=key
        if symbol is not None:
            finalKey=symbol+_KEY_CHAR+key

        if finalKey in self.ModelParametersDict:
            return self.ModelParametersDict[finalKey]
        elif key in self.ModelParametersDict:
            return self.ModelParametersDict[key]
        else:
            raise Exception("Critical error! Could not find model parameter {} {} in memory"
                            .format(key," for symbol {} ".format(symbol) if symbol is not None else ""))

    def GetLight(self, key,symbol):
        finalKey = key
        if symbol is not None:
            finalKey = symbol + _KEY_CHAR + key

        if finalKey in self.ModelParametersDict:
            return self.ModelParametersDict[finalKey]
        else:
            return None

    #endregion