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
    def MAXIM_SHORT_PCT_CHANGE_3_MIN():
        return "MAXIM_SHORT_PCT_CHANGE_3_MIN"

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
    def PCT_SLOPE_TO_CLOSE_SHORT():
        return "PCT_SLOPE_TO_CLOSE_SHORT"

    @staticmethod
    def BACKWARD_DAYS_SUMMARIES_IN_MEMORY():
        return "BACKWARD_DAYS_SUMMARIES_IN_MEMORY"

    @staticmethod
    def HISTORICAL_PRICES_PAST_DAYS_STD_DEV():
        return "HISTORICAL_PRICES_PAST_DAYS_STD_DEV"

    @staticmethod
    def HISTORICAL_PRICES_PAST_DAYS_DAILY_RSI():
        return "HISTORICAL_PRICES_PAST_DAYS_DAILY_RSI"

    @staticmethod
    def CANDLE_BARS_NON_SMOTHED_MINUTES_RSI():
        return "CANDLE_BARS_NON_SMOTHED_MINUTES_RSI"

    @staticmethod
    def CANDLE_BARS_SMOOTHED_MINUTES_RSI():
        return "CANDLE_BARS_SMOOTHED_MINUTES_RSI"

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

    @staticmethod
    def END_OF_DAY_LIMIT():
        return "END_OF_DAY_LIMIT"

    @staticmethod
    def NON_SMOOTHED_RSI_LONG_THRESHOLD():
        return "NON_SMOOTHED_RSI_LONG_THRESHOLD"

    @staticmethod
    def NON_SMOOTHED_RSI_SHORT_THRESHOLD():
        return "NON_SMOOTHED_RSI_SHORT_THRESHOLD"

    @staticmethod
    def MACD_SLOW():
        return "MACD_SLOW"

    @staticmethod
    def MACD_FAST():
        return "MACD_FAST"

    @staticmethod
    def MS_MAX_MIN_MINUTES():
        return "MS_MAX_MIN_MINUTES"

    @staticmethod
    def MACD_SIGNAL():
        return "MACD_SIGNAL"

    @staticmethod
    def AUTOMATIC_TRADING_MODE():
        return "AUTOMATIC_TRADING_MODE"

    @staticmethod
    def M_S_NOW_A():
        return "M_S_NOW_A"

    @staticmethod
    def M_S_MIN_B():
        return "M_S_MIN_B"

    @staticmethod
    def RSI_30_SLOPE_SKIP_5_C():
        return "RSI_30_SLOPE_SKIP_5_C"

    @staticmethod
    def M_S_MAX_MIN_D():
        return "M_S_MAX_MIN_D"

    @staticmethod
    def M_S_NOW_MAX_E():
        return "M_S_NOW_MAX_E"

    @staticmethod
    def M_S_NOW_F():
        return "M_S_NOW_F"

    @staticmethod
    def RSI_30_SLOPE_SKIP_10_G():
        return "RSI_30_SLOPE_SKIP_10_G"

    @staticmethod
    def ABS_M_S_MAX_MIN_LAST_5_H():
        return "ABS_M_S_MAX_MIN_LAST_5_H"

    @staticmethod
    def SEC_5_MIN_SLOPE_I():
        return "SEC_5_MIN_SLOPE_I"

    @staticmethod
    def MACD_MAX_GAIN_J():
        return "MACD_MAX_GAIN_J"

    @staticmethod
    def MACD_GAIN_NOW_MAX_K():
        return "MACD_GAIN_NOW_MAX_K"

    @staticmethod
    def RSI_30_SLOPE_SKIP_5_EXIT_L():
        return "RSI_30_SLOPE_SKIP_5_EXIT_L"

    @staticmethod
    def M_S_NOW_EXIT_N():
        return "M_S_NOW_EXIT_N"

    @staticmethod
    def M_S_MAX_MIN_EXIT_N_BIS():
        return "M_S_MAX_MIN_EXIT_N_BIS"

    @staticmethod
    def M_S_NOW_MAX_MIN_EXIT_P():
        return "M_S_NOW_MAX_MIN_EXIT_P"

    @staticmethod
    def M_S_NOW_EXIT_Q():
        return "M_S_NOW_EXIT_Q"

    @staticmethod
    def RSI_30_SLOPE_SKIP_10_EXIT_R():
        return "RSI_30_SLOPE_SKIP_10_EXIT_R"

    @staticmethod
    def M_S_MAX_MIN_EXIT_S():
        return "M_S_MAX_MIN_EXIT_S"

    @staticmethod
    def SEC_5_MIN_SLOPE_EXIT_T():
        return "SEC_5_MIN_SLOPE_EXIT_T"

    @staticmethod
    def GAIN_MIN_STOP_LOSS_EXIT_U():
        return "GAIN_MIN_STOP_LOSS_EXIT_U"

    @staticmethod
    def PROCESS_EXTERNAL_TRADING():
        return "PROCESS_EXTERNAL_TRADING"

    #endregion

    #region Public Methods

    def GetAll(self,  symbol):

        modelParamArr=[]

        for key in self.ModelParametersDict:
            if symbol is None:
                if not _KEY_CHAR in key:
                    modelParamArr.append(self.ModelParametersDict[key])
            else:
                if key.startswith(symbol):
                    modelParamArr.append(self.ModelParametersDict[key])

        return modelParamArr



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

    def Set(self, key, symbol,modelParam):
        if(symbol is not None and symbol!="*"):
            self.ModelParametersDict[symbol + _KEY_CHAR +key] = modelParam
        else:
            self.ModelParametersDict[key] = modelParam

    #endregion