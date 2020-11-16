from sources.strategy.strategies.day_trader.common.util.model_parameters_handler import *
from sources.framework.common.enums.Side import *
from sources.framework.common.logger.message_type import *
from sources.strategy.strategies.day_trader.common.converters.side_converter import *
import datetime
import threading

class TradingSignalHelper:

    @staticmethod
    def _ACTION_OPEN():
        return "OPEN"

    @staticmethod
    def _ACTION_CLOSE():
        return "CLOSE"

    def __init__(self,pModelParametersHandler,pTradingSignalManager):

       self.ModelParametersHandler=pModelParametersHandler
       self.TradingSignalManager = pTradingSignalManager
       self.PersistingLock = threading.Lock()


    #region Private Methods

    def PersistBollingerParamters(self,tradingSignalId,symbol):

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.DELTAUP_YYY(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.DELTADN_XXX(), symbol))

    def PersistBroomsParamters(self,tradingSignalId,symbol):

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_TPMA_A(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_TPSD_B(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_BOLLUP_C(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_BOLLDN_D(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_BOLLUP_CvHALF(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_BOLLDN_DvHALF(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_BOLLINGER_K(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_BOLLINGER_L(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_MS_STRENGTH_M(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_MS_STRENGTH_N(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_MS_STRENGTH_P(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_MS_STRENGTH_Q(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_R(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_S(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_T(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_U(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_V(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_W(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_X(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_Y(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_Z(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_CC(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_DD(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_EE(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_NN(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_PP(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_QQ(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_RR(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_SS(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_TT(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_UU(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_VV(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_WW(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_XX(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.BROOMS_BIAS(), symbol))

    def PersistTGCalculationParameters(self,tradingSignalId,symbol):

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.TG_INDICATOR_KK(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.TG_INDICATOR_KX(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.TG_INDICATOR_KY(), symbol))

    def PersistTerminalParameters(self,tradingSignalId,symbol):

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.STOP_LOSS_LIMIT(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.TAKE_GAIN_LIMIT(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.END_OF_DAY_LIMIT(), symbol))

    def PersistPriceVolatilityParameters(self,tradingSignalId,symbol):

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.HISTORICAL_PRICES_SDD_OPEN_STD_DEV(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.FLEXIBLE_STOP_LOSS_L1(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.IMPL_FLEXIBLE_STOP_LOSSES(), symbol))

    def PersistVolumeParamters(self,tradingSignalId,symbol):
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.VOLUME_INDICATOR_T1(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.VOLUME_INDICATOR_T2(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.VOLUME_INDICATOR_T3(), symbol))

    def PersistBollingerIndicators(self,dayTradingPos,tradingSignalId):
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.TP",
                                                                    dayTradingPos.BollingerIndicator.TP)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.TPMA",
                                                                    dayTradingPos.BollingerIndicator.TPMA)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.TPSD",
                                                                    dayTradingPos.BollingerIndicator.TPSD)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.TPSDStartOfTrade",
                                                                    dayTradingPos.BollingerIndicator.TPSDStartOfTrade)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.BollUp",
                                                                    dayTradingPos.BollingerIndicator.BollUp)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.BollDn",
                                                                    dayTradingPos.BollingerIndicator.BollDn)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.HalfBollUp",
                                                                    dayTradingPos.BollingerIndicator.HalfBollUp)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.HalfBollDn",
                                                                    dayTradingPos.BollingerIndicator.HalfBollDn)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.DeltaUP",
                                                                    dayTradingPos.BollingerIndicator.DeltaUP())
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.DeltaDN",
                                                                    dayTradingPos.BollingerIndicator.DeltaDN())
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.BSI",
                                                                    dayTradingPos.BollingerIndicator.BSI)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Boollinger.TPSDStartOfTrade",
                                                                    dayTradingPos.BollingerIndicator.TPSDStartOfTrade)

    def PersistMSStrengthIndicators(self,dayTradingPos,tradingSignalId):
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MSStrength.TPSD",
                                                                    dayTradingPos.MSStrengthIndicator.TPSD)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MSStrength.MSI",
                                                                    dayTradingPos.MSStrengthIndicator.MSI)

    def PersistBroomsIndicators(self,dayTradingPos,tradingSignalId):
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Brooms.TPSL",
                                                                    dayTradingPos.BroomsIndicator.TPSL)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Brooms.BSIMax",
                                                                    dayTradingPos.BroomsIndicator.BSIMax)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Brooms.BSIMin",
                                                                    dayTradingPos.BroomsIndicator.BSIMin)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Brooms.MSIMax",
                                                                    dayTradingPos.BroomsIndicator.MSIMax)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Brooms.MSIMin",
                                                                    dayTradingPos.BroomsIndicator.MSIMin)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Brooms.MSSlope",
                                                                    dayTradingPos.BroomsIndicator.MSSlope)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Brooms.BROOMS",
                                                                    dayTradingPos.BroomsIndicator.BROOMS)

    def PersistOpeningRules(self,dayTradingPos,tradingSignalId,symbol):

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_OPEN_LONG_RULE_1(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_OPEN_LONG_RULE_2(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_OPEN_LONG_RULE_3(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_OPEN_LONG_RULE_4(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_OPEN_SHORT_RULE_1(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_OPEN_SHORT_RULE_2(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_OPEN_SHORT_RULE_3(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_OPEN_SHORT_RULE_4(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.VOLUME_INDICATOR_RULE_4(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.VOLUME_INDICATOR_RULE_BROOMS(), symbol))

    def PersistClosingRules(self,tradingSignalId,symbol):

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_1(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_2(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_3(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_4(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_5(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_6(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_7(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_8(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_9(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_1(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_2(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_3(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_4(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_5(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_6(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_7(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_8(), symbol))
        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_9(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.VOLUME_INDICATOR_RULE_4(), symbol))

        self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
            ModelParametersHandler.VOLUME_INDICATOR_RULE_BROOMS(), symbol))

    def PersistProfitIndicators(self,dayTradingPos,tradingSignalId):

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "CurrentProfit",dayTradingPos.CurrentProfit)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "CurrentProfitLastTrade", dayTradingPos.CurrentProfitLastTrade)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "CurrentProfitMonetary",dayTradingPos.CurrentProfitMonetary)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "CurrentProfitMonetaryLastTrade",dayTradingPos.CurrentProfitMonetaryLastTrade)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxProfit",dayTradingPos.MaxProfit)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxProfitCurrentTrade",dayTradingPos.MaxProfitCurrentTrade)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxMonetaryProfitCurrentTrade",dayTradingPos.MaxMonetaryProfitCurrentTrade)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxMonetaryLossCurrentTrade",dayTradingPos.MaxMonetaryLossCurrentTrade)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxLoss",dayTradingPos.MaxLoss)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxLossCurrentTrade",dayTradingPos.MaxLossCurrentTrade)

    def PersistMACDIndicators(self,dayTradingPos,tradingSignalId):

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.MSPrev",
                                                                    dayTradingPos.MACDIndicator.MSPrev)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.MSNow",
                                                                    dayTradingPos.MACDIndicator.MS)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.MaxMS",
                                                                    dayTradingPos.MACDIndicator.MaxMS)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.MinMS",
                                                                    dayTradingPos.MACDIndicator.MinMS)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.AbsMaxMS",
                                                                    dayTradingPos.MACDIndicator.AbsMaxMS)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.MS3SL",
                                                                    dayTradingPos.MACDIndicator.GetMSSlope(3))

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.PriceHMinusL",
                                                                    dayTradingPos.MACDIndicator.PriceHMinusL)

        absMaxMSPeriodParam = self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_ABS_MAX_MS_PERIOD(),
                                                              dayTradingPos.Security.Symbol)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.MaxAbsMSCrossover",
                                                                    dayTradingPos.MACDIndicator.GetMaxAbsMSCrossover(
                                                                        absMaxMSPeriodParam.IntValue))

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.MaxAbsMSPeriod",
                                                                    absMaxMSPeriodParam.IntValue)

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.MACD",
                                                                    dayTradingPos.MACDIndicator.MACD)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MACD.Signal",
                                                                    dayTradingPos.MACDIndicator.Signal)

    def PersistPricesIndicators(self,dayTradingPos,tradingSignalId):
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Symbol 5SL",dayTradingPos.PricesReggrSlope)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Symbol 5SL Period",dayTradingPos.PricesReggrSlopePeriod)

    def PersistRSIIndicators(self,dayTradingPos,tradingSignalId):
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "RSISmoothed5SL",
                                                                    dayTradingPos.MinuteSmoothedRSIIndicator.GetRSIReggr(
                                                                        5))
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "RSISmoothed10SL",
                                                                    dayTradingPos.MinuteSmoothedRSIIndicator.GetRSIReggr(
                                                                        10))
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "RSINonSmoothed3SL",
                                                                    dayTradingPos.MinuteNonSmoothedRSIIndicator.GetRSIReggr(
                                                                        3))
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "SmoothedRSI",
                                                                    dayTradingPos.MinuteSmoothedRSIIndicator.RSI)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "NonSmoothedRSI",
                                                                    dayTradingPos.MinuteNonSmoothedRSIIndicator.RSI)

    def PersistPriceVolatilityIndicators(self,dayTradingPos,tradingSignalId):

        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId,
                                                                    "PriceVolatilityIndicator.LastSDDDaysOpenStdDev",
                                                                    dayTradingPos.PriceVolatilityIndicators.LastSDDDaysOpenStdDev)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId,
                                                                    "PriceVolatilityIndicator.FlexibleStopLoss",
                                                                    dayTradingPos.PriceVolatilityIndicators.FlexibleStopLoss)

    def PersistTGCalculationIndicators(self,dayTradingPos,tradingSignalId):
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "TGIndicator.K",
                                                                    dayTradingPos.TGIndicator.K)
    def PersistVolumeIndicators(self,dayTradingPos,tradingSignalId):
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "VolumeAvgIndicator.L5V",
                                                                    dayTradingPos.VolumeAvgIndicator.L5V)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "VolumeAvgIndicator.L20V",
                                                                    dayTradingPos.VolumeAvgIndicator.L20V)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "VolumeAvgIndicator.CV",
                                                                    dayTradingPos.VolumeAvgIndicator.CV)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "VolumeAvgIndicator.VR1",
                                                                    dayTradingPos.VolumeAvgIndicator.VR1)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "VolumeAvgIndicator.VR2",
                                                                    dayTradingPos.VolumeAvgIndicator.VR2)
        self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "VolumeAvgIndicator.VR3",
                                                                    dayTradingPos.VolumeAvgIndicator.VR3)

    #endregion


    #region Public Methods

    def PersistMACDRSITradingSignal(self, dayTradingPos, action, side,candlebar,logger,condition=None):
        try:

            persistTradingSignalParam  = self.ModelParametersHandler.Get(ModelParametersHandler.PERSIST_TRADING_SIGNAL(),
                                                                         dayTradingPos.Security.Symbol)

            if persistTradingSignalParam.IntValue!=1:
                return

            self.PersistingLock.acquire(blocking=True)

            now=candlebar.DateTime

            self.TradingSignalManager.PersistTradingSignal(dayTradingPos,now,action, SideConverter.ConvertSideToString(side),candlebar)

            tradingSignalId= self.TradingSignalManager.GetTradingSignal(now,dayTradingPos.Security.Symbol)

            if self.PersistingLock.locked():
                self.PersistingLock.release()

            if tradingSignalId is None:
                raise  Exception("Critical error saving RSI/MACD trading signal. Could not recover trading signal from DB. Symbol={} datetime={}".format(dayTradingPos.Security.Symbol,now))

            symbol = dayTradingPos.Security.Symbol

            if action == TradingSignalHelper._ACTION_OPEN():
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_A(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_MIN_B(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_MIN_B_B(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_30_SLOPE_SKIP_5_C(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_MAX_MIN_D(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_MAX_MIN_D_D(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_MAX_E(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_F(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_F_F(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_30_SLOPE_SKIP_10_G(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.ABS_M_S_MAX_MIN_LAST_5_H(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.ABS_M_S_MAX_MIN_LAST_5_H_H(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.SEC_5_MIN_SLOPE_I(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.MACD_MAX_GAIN_J(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.MACD_GAIN_NOW_MAX_K(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_14_SLOPE_SKIP_3_V(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_3_SLOPE_X(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_3_SLOPE_X_X(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.MACD_RSI_ABS_MAX_MS_PERIOD(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.DAILY_BIAS_MACD_RSI(), symbol))

                self.PersistOpeningRules(dayTradingPos,tradingSignalId,symbol)

                self.PersistBollingerParamters(tradingSignalId,symbol)

                self.PersistBroomsParamters(tradingSignalId,symbol)

                self.PersistVolumeParamters(tradingSignalId,symbol)

                self.PersistPricesIndicators(dayTradingPos, tradingSignalId)

                self.PersistMACDIndicators(dayTradingPos,tradingSignalId)

                self.PersistRSIIndicators(dayTradingPos,tradingSignalId)

                self.PersistVolumeIndicators(dayTradingPos,tradingSignalId)

                self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "LastClose",candlebar.Close)
                self.TradingSignalManager.PersistSignalOtherParameter(tradingSignalId, "OpenCondition",condition if condition is not None else "unk")
                self.TradingSignalManager.PersistSignalOtherParameter(tradingSignalId, "LastDateTime",str(candlebar.DateTime))
                self.PersistBollingerIndicators(dayTradingPos,tradingSignalId)
                self.PersistMSStrengthIndicators(dayTradingPos,tradingSignalId)
                self.PersistBroomsIndicators(dayTradingPos,tradingSignalId)

            elif action == TradingSignalHelper._ACTION_CLOSE():
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_A(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.MACD_MAX_GAIN_J(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.MACD_GAIN_NOW_MAX_K(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_30_SLOPE_SKIP_5_EXIT_L(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_30_5SL_LX(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_EXIT_N(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_EXIT_N_N(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_MAX_MIN_EXIT_N_BIS(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_MAX_MIN_EXIT_N_N_BIS(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_MAX_MIN_EXIT_P(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_EXIT_Q(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_NOW_EXIT_Q_Q(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_30_SLOPE_SKIP_10_EXIT_R(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_MAX_MIN_EXIT_S(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.M_S_MAX_MIN_EXIT_S_S(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.SEC_5_MIN_SLOPE_EXIT_T(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_U(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_U_U(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_W(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_W_W(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_STOP_LOSS_EXIT_Y(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_Z(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_Z_Z(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MAX_TRADE_JJJ(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MAX_TRADE_SDMULT(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MAX_TRADE_FIXEDGAIN(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MIN_TRADE_UUU(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MIN_TRADE_FIXEDLOSS(), symbol))


                self.PersistTGCalculationParameters(tradingSignalId,symbol)

                self.PersistTerminalParameters(tradingSignalId,symbol)

                self.PersistPriceVolatilityParameters(tradingSignalId,symbol)

                self.PersistVolumeParamters(tradingSignalId, symbol)

                self.PersistClosingRules(tradingSignalId,symbol)

                self.PersistPricesIndicators(dayTradingPos, tradingSignalId)

                self.PersistMACDIndicators(dayTradingPos, tradingSignalId)

                self.PersistRSIIndicators(dayTradingPos, tradingSignalId)

                self.PersistProfitIndicators(dayTradingPos,tradingSignalId)

                self.PersistPriceVolatilityIndicators(dayTradingPos,tradingSignalId)

                self.PersistTGCalculationIndicators(dayTradingPos,tradingSignalId)

                self.PersistBollingerIndicators(dayTradingPos, tradingSignalId)

                self.PersistVolumeIndicators(dayTradingPos, tradingSignalId)

                self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "LastClose",candlebar.Close)
                self.TradingSignalManager.PersistSignalOtherParameter(tradingSignalId, "CloseCondition",condition if condition is not None else "unk")
                self.TradingSignalManager.PersistSignalOtherParameter(tradingSignalId, "TerminalCloseCond",dayTradingPos.TerminalCloseCond)

                self.TradingSignalManager.PersistSignalOtherParameter(tradingSignalId, "LastDateTime",str(candlebar.DateTime))


            self.TradingSignalManager.Commit()

        except Exception as e:
            logger.DoLog("Critical error persisting trading signal for symbol {}:{}".format(
                         dayTradingPos.Security.Symbol if (dayTradingPos is not None and dayTradingPos.Security is not None) else "?",str(e)),
                         MessageType.ERROR)
        finally:
            if self.PersistingLock.locked():
                self.PersistingLock.release()


    def PersistTradingSignal(self, dayTradingPos, action, side, statisticalParam,candlebar,logger,condition=None):


        try:

            persistTradingSignalParam = self.ModelParametersHandler.Get(ModelParametersHandler.PERSIST_TRADING_SIGNAL(),
                                                                        dayTradingPos.Security.Symbol)

            if persistTradingSignalParam.IntValue != 1:
                return

            self.PersistingLock.acquire(blocking=True)

            now=candlebar.DateTime

            self.TradingSignalManager.PersistTradingSignal(dayTradingPos,now,action, SideConverter.ConvertSideToString(side),
                                                           candlebar)

            tradingSignalId= self.TradingSignalManager.GetTradingSignal(now,dayTradingPos.Security.Symbol)

            if self.PersistingLock.locked():
                self.PersistingLock.release()

            if tradingSignalId is None:
                raise  Exception("Critical error saving trading signal. Could not recover trading signal from DB. Symbol={} datetime={}".format(dayTradingPos.Security.Symbol,now))

            symbol = dayTradingPos.Security.Symbol

            if action == TradingSignalHelper._ACTION_OPEN():
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.LOW_VOL_ENTRY_THRESHOLD(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.HIGH_VOL_ENTRY_THRESHOLD(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.LOW_VOL_FROM_TIME(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.LOW_VOL_TO_TIME(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.HIGH_VOL_FROM_TIME_1(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.HIGH_VOL_TO_TIME_1(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.HIGH_VOL_FROM_TIME_2(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.HIGH_VOL_TO_TIME_2(), symbol))

                if (side == Side.Buy or side == side.BuyToClose):
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.DAILY_BIAS(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.DAILY_SLOPE(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.MAXIM_PCT_CHANGE_3_MIN(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.POS_LONG_MAX_DELTA(), symbol))

                elif (side == Side.Sell or side == side.SellShort):
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.DAILY_BIAS(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.DAILY_SLOPE(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.MAXIM_SHORT_PCT_CHANGE_3_MIN(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.POS_SHORT_MAX_DELTA(), symbol))

            elif action == TradingSignalHelper._ACTION_CLOSE():
                if dayTradingPos.GetNetOpenShares() > 0:
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.MAX_GAIN_FOR_DAY(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.PCT_MAX_GAIN_CLOSING(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.MAX_LOSS_FOR_DAY(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.PCT_MAX_LOSS_CLOSING(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.TAKE_GAIN_LIMIT(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.STOP_LOSS_LIMIT(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.PCT_SLOPE_TO_CLOSE_LONG(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.END_OF_DAY_LIMIT(), symbol))
                else:
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.MAX_GAIN_FOR_DAY(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.PCT_MAX_GAIN_CLOSING(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.MAX_LOSS_FOR_DAY(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.PCT_MAX_LOSS_CLOSING(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.TAKE_GAIN_LIMIT(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.STOP_LOSS_LIMIT(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.PCT_SLOPE_TO_CLOSE_SHORT(), symbol))
                    self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                        ModelParametersHandler.END_OF_DAY_LIMIT(), symbol))

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "TenMinSkipSlope",
                                                                        statisticalParam.TenMinSkipSlope)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "ThreeMinSkipSlope",
                                                                        statisticalParam.ThreeMinSkipSlope)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "ThreeToSixMinSkipSlope",
                                                                        statisticalParam.ThreeToSixMinSkipSlope)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "SixToNineMinSkipSlope",
                                                                        statisticalParam.SixToNineMinSkipSlope)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "PctChangeLastThreeMinSlope",
                                                                        statisticalParam.PctChangeLastThreeMinSlope)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "DeltaCurrValueAndFiftyMMov",
                                                                        statisticalParam.DeltaCurrValueAndFiftyMMov)

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "NonSmoothed14MinRSI",
                                                                        dayTradingPos.MinuteNonSmoothedRSIIndicator.RSI)

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "PrevNonSmoothed14MinRSI",
                                                                        dayTradingPos.MinuteNonSmoothedRSIIndicator.PrevRSI)

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Smoothed30MinRSI",
                                                                        dayTradingPos.MinuteSmoothedRSIIndicator.RSI)

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "PrevSmoothed30MinRSI",
                                                                        dayTradingPos.MinuteSmoothedRSIIndicator.PrevRSI)

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Daily14DaysRSI",
                                                                        dayTradingPos.DailyRSIIndicator.RSI)

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "CloseCondition",
                                                                        condition if condition is None else "??")

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "CurrentProfit",
                                                                        dayTradingPos.CurrentProfit)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "CurrentProfitLastTrade",
                                                                        dayTradingPos.CurrentProfitLastTrade)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxProfit",
                                                                        dayTradingPos.MaxProfit)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxProfitCurrentTrade",
                                                                        dayTradingPos.MaxProfitCurrentTrade)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxLoss",
                                                                        dayTradingPos.MaxLoss)
            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "MaxLossCurrentTrade",
                                                                        dayTradingPos.MaxLossCurrentTrade)

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "CurrentProfitToSecurity",
                                                                        dayTradingPos.CurrentProfit)

            self.TradingSignalManager.Commit()

        except Exception as e:
            logger.DoLog("Critical error persisting trading signal for symbol {}:{}".format(
                         dayTradingPos.Security.Symbol if (dayTradingPos is not None and dayTradingPos.Security is not None) else "?",str(e)),
                         MessageType.ERROR)
        finally:
            if self.PersistingLock.locked():
                self.PersistingLock.release()

    #endregion