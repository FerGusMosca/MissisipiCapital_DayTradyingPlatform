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
    def HISTORICAL_PRICES_SDD_OPEN_STD_DEV():
        return "HISTORICAL_PRICES_SDD_OPEN_STD_DEV"

    @staticmethod
    def PRELOAD_PREFIX():
        return "PRELOAD_PREFIX"

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
    def RSI_14_SLOPE_SKIP_3_V():
        return "RSI_14_SLOPE_SKIP_3_V"

    @staticmethod
    def M_S_3_SLOPE_X():
        return "M_S_3_SLOPE_X"

    @staticmethod
    def GAIN_MIN_STOP_LOSS_EXIT_W():
        return "GAIN_MIN_STOP_LOSS_EXIT_W"

    @staticmethod
    def GAIN_STOP_LOSS_EXIT_Y():
        return "GAIN_STOP_LOSS_EXIT_Y"

    @staticmethod
    def GAIN_MIN_STOP_LOSS_EXIT_Z():
        return "GAIN_MIN_STOP_LOSS_EXIT_Z"

    @staticmethod
    def DAILY_BIAS_MACD_RSI():
        return "DAILY_BIAS_MACD_RSI"

    @staticmethod
    def PROCESS_EXTERNAL_TRADING():
        return "PROCESS_EXTERNAL_TRADING"

    @staticmethod
    def M_S_MIN_B_B():
        return "M_S_MIN_B_B"

    @staticmethod
    def M_S_MAX_MIN_D_D():
        return "M_S_MAX_MIN_D_D"

    @staticmethod
    def M_S_NOW_F_F():
        return "M_S_NOW_F_F"

    @staticmethod
    def ABS_M_S_MAX_MIN_LAST_5_H_H():
        return "ABS_M_S_MAX_MIN_LAST_5_H_H"

    @staticmethod
    def MACD_MAX_GAIN_J_J():
        return "MACD_MAX_GAIN_J_J"

    @staticmethod
    def M_S_NOW_EXIT_N_N():
        return "M_S_NOW_EXIT_N_N"

    @staticmethod
    def M_S_MAX_MIN_EXIT_N_N_BIS():
        return "M_S_MAX_MIN_EXIT_N_N_BIS"

    @staticmethod
    def M_S_NOW_EXIT_Q_Q():
        return "M_S_NOW_EXIT_Q_Q"

    @staticmethod
    def M_S_MAX_MIN_EXIT_S_S():
        return "M_S_MAX_MIN_EXIT_S_S"

    @staticmethod
    def M_S_3_SLOPE_X_X():
        return "M_S_3_SLOPE_X_X"

    @staticmethod
    def GAIN_MIN_STOP_LOSS_EXIT_U_U():
        return "GAIN_MIN_STOP_LOSS_EXIT_U_U"

    @staticmethod
    def GAIN_MIN_STOP_LOSS_EXIT_W_W():
        return "GAIN_MIN_STOP_LOSS_EXIT_W_W"

    @staticmethod
    def GAIN_MIN_STOP_LOSS_EXIT_Z_Z():
        return "GAIN_MIN_STOP_LOSS_EXIT_Z_Z"

    @staticmethod
    def RSI_30_5SL_LX():
        return "RSI_30_5SL_LX"

    @staticmethod
    def DELTAUP_YYY():
        return "DELTAUP_YYY"

    @staticmethod
    def DELTADN_XXX():
        return "DELTADN_XXX"

    @staticmethod
    def GAIN_MAX_TRADE_JJJ():
        return "GAIN_MAX_TRADE_JJJ"

    @staticmethod
    def GAIN_MAX_TRADE_SDMULT():
        return "GAIN_MAX_TRADE_SDMULT"

    @staticmethod
    def GAIN_MAX_TRADE_FIXEDGAIN():
        return "GAIN_MAX_TRADE_FIXEDGAIN"

    @staticmethod
    def GAIN_MIN_TRADE_UUU():
        return "GAIN_MIN_TRADE_UUU"

    @staticmethod
    def GAIN_MIN_TRADE_FIXEDLOSS():
        return "GAIN_MIN_TRADE_FIXEDLOSS"

    @staticmethod
    def GAIN_MIN_TRADE_FIXEDLOSS_2():
        return "GAIN_MIN_TRADE_FIXEDLOSS_2"

    @staticmethod
    def PROCESS_EXTERNAL_TRADING():
        return "PROCESS_EXTERNAL_TRADING"

    @staticmethod
    def MACD_RSI_SMOOTHED_MODE():
        return "MACD_RSI_SMOOTHED_MODE"

    @staticmethod
    def MACD_RSI_ABS_MAX_MS_PERIOD():
        return "MACD_RSI_ABS_MAX_MS_PERIOD"

    @staticmethod
    def MACD_RSI_OPEN_LONG_RULE_1():
        return "MACD_RSI_OPEN_LONG_RULE_1"

    @staticmethod
    def MACD_RSI_OPEN_LONG_RULE_2():
        return "MACD_RSI_OPEN_LONG_RULE_2"

    @staticmethod
    def MACD_RSI_OPEN_LONG_RULE_3():
        return "MACD_RSI_OPEN_LONG_RULE_3"

    @staticmethod
    def MACD_RSI_OPEN_LONG_RULE_4():
        return "MACD_RSI_OPEN_LONG_RULE_4"

    @staticmethod
    def MACD_RSI_OPEN_LONG_RULE_BROOMS():
        return "MACD_RSI_OPEN_LONG_RULE_BROOMS"

    @staticmethod
    def MACD_RSI_OPEN_SHORT_RULE_1():
        return "MACD_RSI_OPEN_SHORT_RULE_1"

    @staticmethod
    def MACD_RSI_OPEN_SHORT_RULE_2():
        return "MACD_RSI_OPEN_SHORT_RULE_2"

    @staticmethod
    def MACD_RSI_OPEN_SHORT_RULE_3():
        return "MACD_RSI_OPEN_SHORT_RULE_3"

    @staticmethod
    def MACD_RSI_OPEN_SHORT_RULE_4():
        return "MACD_RSI_OPEN_SHORT_RULE_4"

    @staticmethod
    def MACD_RSI_OPEN_SHORT_RULE_BROOMS():
        return "MACD_RSI_OPEN_SHORT_RULE_BROOMS"

    @staticmethod
    def MACD_RSI_CLOSE_LONG_RULE_1():
        return "MACD_RSI_CLOSE_LONG_RULE_1"

    @staticmethod
    def MACD_RSI_CLOSE_LONG_RULE_2():
        return "MACD_RSI_CLOSE_LONG_RULE_2"

    @staticmethod
    def MACD_RSI_CLOSE_LONG_RULE_3():
        return "MACD_RSI_CLOSE_LONG_RULE_3"

    @staticmethod
    def MACD_RSI_CLOSE_LONG_RULE_4():
        return "MACD_RSI_CLOSE_LONG_RULE_4"

    @staticmethod
    def MACD_RSI_CLOSE_LONG_RULE_5():
        return "MACD_RSI_CLOSE_LONG_RULE_5"

    @staticmethod
    def MACD_RSI_CLOSE_LONG_RULE_6():
        return "MACD_RSI_CLOSE_LONG_RULE_6"

    @staticmethod
    def MACD_RSI_CLOSE_LONG_RULE_7():
        return "MACD_RSI_CLOSE_LONG_RULE_7"

    @staticmethod
    def MACD_RSI_CLOSE_LONG_RULE_8():
        return "MACD_RSI_CLOSE_LONG_RULE_8"

    @staticmethod
    def MACD_RSI_CLOSE_LONG_RULE_9():
        return "MACD_RSI_CLOSE_LONG_RULE_9"

    @staticmethod
    def MACD_RSI_CLOSE_SHORT_RULE_1():
        return "MACD_RSI_CLOSE_SHORT_RULE_1"

    @staticmethod
    def MACD_RSI_CLOSE_SHORT_RULE_2():
        return "MACD_RSI_CLOSE_SHORT_RULE_2"

    @staticmethod
    def MACD_RSI_CLOSE_SHORT_RULE_3():
        return "MACD_RSI_CLOSE_SHORT_RULE_3"

    @staticmethod
    def MACD_RSI_CLOSE_SHORT_RULE_4():
        return "MACD_RSI_CLOSE_SHORT_RULE_4"

    @staticmethod
    def MACD_RSI_CLOSE_SHORT_RULE_5():
        return "MACD_RSI_CLOSE_SHORT_RULE_5"

    @staticmethod
    def MACD_RSI_CLOSE_SHORT_RULE_6():
        return "MACD_RSI_CLOSE_SHORT_RULE_6"

    @staticmethod
    def MACD_RSI_CLOSE_SHORT_RULE_7():
        return "MACD_RSI_CLOSE_SHORT_RULE_7"

    @staticmethod
    def MACD_RSI_CLOSE_SHORT_RULE_8():
        return "MACD_RSI_CLOSE_SHORT_RULE_8"

    @staticmethod
    def MACD_RSI_CLOSE_SHORT_RULE_9():
        return "MACD_RSI_CLOSE_SHORT_RULE_9"

    @staticmethod
    def PACING_ON_BACKTEST_MILISEC():
        return "PACING_ON_BACKTEST_MILISEC"

    @staticmethod
    def MACD_RSI_START_TRADING():
        return "MACD_RSI_START_TRADING"

    @staticmethod
    def BROOMS_TPMA_A():
        return "BROOMS_TPMA_A"

    @staticmethod
    def BROOMS_TPSD_B():
        return "BROOMS_TPSD_B"

    @staticmethod
    def BROOMS_TPSD_B():
        return "BROOMS_TPSD_B"

    @staticmethod
    def BROOMS_BOLLUP_C():
        return "BROOMS_BOLLUP_C"

    @staticmethod
    def BROOMS_BOLLDN_D():
        return "BROOMS_BOLLDN_D"

    @staticmethod
    def BROOMS_BOLLUP_CvHALF():
        return "BROOMS_BOLLUP_CvHALF"

    @staticmethod
    def BROOMS_BOLLDN_DvHALF():
        return "BROOMS_BOLLDN_DvHALF"

    @staticmethod
    def SD_LIMIT_FACTOR():
        return "SD_LIMIT_FACTOR"

    @staticmethod
    def BROOMS_BOLLINGER_K():
        return "BROOMS_BOLLINGER_K"

    @staticmethod
    def BROOMS_BOLLINGER_L():
        return "BROOMS_BOLLINGER_L"

    @staticmethod
    def BROOMS_MS_STRENGTH_M():
        return "BROOMS_MS_STRENGTH_M"

    @staticmethod
    def BROOMS_MS_STRENGTH_N():
        return "BROOMS_MS_STRENGTH_N"

    @staticmethod
    def BROOMS_MS_STRENGTH_P():
        return "BROOMS_MS_STRENGTH_P"

    @staticmethod
    def BROOMS_MS_STRENGTH_Q():
        return "BROOMS_MS_STRENGTH_Q"

    @staticmethod
    def BROOMS_J():
        return "BROOMS_J"

    @staticmethod
    def BROOMS_R():
        return "BROOMS_R"

    @staticmethod
    def BROOMS_S():
        return "BROOMS_S"

    @staticmethod
    def BROOMS_S():
        return "BROOMS_S"

    @staticmethod
    def BROOMS_T():
        return "BROOMS_T"

    @staticmethod
    def BROOMS_U():
        return "BROOMS_U"

    @staticmethod
    def BROOMS_V():
        return "BROOMS_V"

    @staticmethod
    def BROOMS_W():
        return "BROOMS_W"

    @staticmethod
    def BROOMS_X():
        return "BROOMS_X"

    @staticmethod
    def BROOMS_Y():
        return "BROOMS_Y"

    @staticmethod
    def BROOMS_Z():
        return "BROOMS_Z"

    @staticmethod
    def BROOMS_CC():
        return "BROOMS_CC"

    @staticmethod
    def BROOMS_DD():
        return "BROOMS_DD"

    @staticmethod
    def BROOMS_EE():
        return "BROOMS_EE"

    @staticmethod
    def BROOMS_NN():
        return "BROOMS_NN"

    @staticmethod
    def BROOMS_PP():
        return "BROOMS_PP"

    @staticmethod
    def BROOMS_QQ():
        return "BROOMS_QQ"

    @staticmethod
    def BROOMS_RR():
        return "BROOMS_RR"

    @staticmethod
    def BROOMS_SS():
        return "BROOMS_SS"

    @staticmethod
    def BROOMS_TT():
        return "BROOMS_TT"

    @staticmethod
    def BROOMS_UU():
        return "BROOMS_UU"

    @staticmethod
    def BROOMS_VV():
        return "BROOMS_VV"

    @staticmethod
    def BROOMS_WW():
        return "BROOMS_WW"

    @staticmethod
    def BROOMS_XX():
        return "BROOMS_XX"

    @staticmethod
    def BROOMS_BIAS():
        return "BROOMS_BIAS"

    @staticmethod
    def FLEXIBLE_STOP_LOSS_L1():
        return "FLEXIBLE_STOP_LOSS_L1"

    @staticmethod
    def IMPL_FLEXIBLE_STOP_LOSSES():
        return "IMPL_FLEXIBLE_STOP_LOSSES"

    @staticmethod
    def TG_INDICATOR_KK():
        return "TG_INDICATOR_KK"

    @staticmethod
    def TG_INDICATOR_KX():
        return "TG_INDICATOR_KX"

    @staticmethod
    def TG_INDICATOR_KY():
        return "TG_INDICATOR_KY"

    @staticmethod
    def VOLUME_INDICATOR_T1():
        return "VOLUME_INDICATOR_T1"

    @staticmethod
    def VOLUME_INDICATOR_T2():
        return "VOLUME_INDICATOR_T2"

    @staticmethod
    def VOLUME_INDICATOR_T3():
        return "VOLUME_INDICATOR_T3"

    @staticmethod
    def VOLUME_INDICATOR_T3():
        return "VOLUME_INDICATOR_T3"

    @staticmethod
    def VOLUME_INDICATOR_RULE_4():
        return "VOLUME_INDICATOR_RULE_4"

    @staticmethod
    def VOLUME_INDICATOR_RULE_BROOMS():
        return "VOLUME_INDICATOR_RULE_BROOMS"

    @staticmethod
    def PERSIST_TRADING_SIGNAL():
        return "PERSIST_TRADING_SIGNAL"

    @staticmethod
    def CANDLE_PRICE_METHOD():
        return "CANDLE_PRICE_METHOD"

    @staticmethod
    def SL_FLIP():
        return "SL_FLIP"

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

    def RemoveLight(self, key,symbol):
        finalKey = key
        if symbol is not None:
            finalKey = symbol + _KEY_CHAR + key

        if finalKey in self.ModelParametersDict:
            del self.ModelParametersDict[finalKey]

        else:
            return None

    def Set(self, key, symbol,modelParam):
        if(symbol is not None and symbol!="*"):
            self.ModelParametersDict[symbol + _KEY_CHAR +key] = modelParam
        else:
            self.ModelParametersDict[key] = modelParam

    #endregion