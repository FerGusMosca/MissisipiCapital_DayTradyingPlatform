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

    def PersistMACDRSITradingSignal(self, dayTradingPos, action, side,candlebar,logger):
        try:

            self.PersistingLock.acquire()

            now=datetime.datetime.now()

            self.TradingSignalManager.PersistTradingSignal(dayTradingPos,now,action, SideConverter.ConvertSideToString(side),candlebar)

            tradingSignalId= self.TradingSignalManager.GetTradingSignal(now,dayTradingPos.Security.Symbol)

            if tradingSignalId is None:
                raise  Exception("Critical error saving RSI/MACD trading signal. Could not recover trading signal from DB. Symbol={} datetime={}".format(dayTradingPos.Security.Symbol,now))

            symbol = dayTradingPos.Security.Symbol

            if action == TradingSignalHelper._ACTION_OPEN():
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_NOW_A(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_MIN_B(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_30_SLOPE_SKIP_5_C(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_MAX_MIN_D(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_NOW_MAX_E(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_NOW_F(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_30_SLOPE_SKIP_10_G(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.ABS_N_S_MAX_MIN_LAST_5_H(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.SEC_5_MIN_SLOPE_I(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.MACD_MAX_GAIN_J(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.MACD_GAIN_NOW_MAX_K(), symbol))


            elif action == TradingSignalHelper._ACTION_CLOSE():
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_NOW_A(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.MACD_MAX_GAIN_J(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.MACD_GAIN_NOW_MAX_K(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_30_SLOPE_SKIP_5_EXIT_L(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_NOW_EXIT_N(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_MAX_MIN_EXIT_N_BIS(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_NOW_MAX_MIN_EXIT_P(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_NOW_EXIT_Q(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.RSI_30_SLOPE_SKIP_10_EXIT_R(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.N_S_MAX_MIN_EXIT_S(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.SEC_5_MIN_SLOPE_EXIT_T(), symbol))
                self.TradingSignalManager.PersistSignalModelParameter(tradingSignalId, self.ModelParametersHandler.Get(
                    ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_U(), symbol))

            #TODO: Save RSI/MACD and the REST

            self.TradingSignalManager.Commit()

        except Exception as e:
            logger.DoLog("Critical error persisting trading signal for symbol {}:{}".format(
                         dayTradingPos.Security.Symbol if (dayTradingPos is not None and dayTradingPos.Security is not None) else "?",str(e)),
                         MessageType.ERROR)
        finally:
            if self.PersistingLock.locked():
                self.PersistingLock.release()


    def PersistTradingSignal(self, dayTradingPos, action, side, statisticalParam,candlebar,logger):


        try:

            self.PersistingLock.acquire()

            now=datetime.datetime.now()

            self.TradingSignalManager.PersistTradingSignal(dayTradingPos,now,action, SideConverter.ConvertSideToString(side),
                                                           candlebar)

            tradingSignalId= self.TradingSignalManager.GetTradingSignal(now,dayTradingPos.Security.Symbol)

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

            self.TradingSignalManager.Commit()

        except Exception as e:
            logger.DoLog("Critical error persisting trading signal for symbol {}:{}".format(
                         dayTradingPos.Security.Symbol if (dayTradingPos is not None and dayTradingPos.Security is not None) else "?",str(e)),
                         MessageType.ERROR)
        finally:
            if self.PersistingLock.locked():
                self.PersistingLock.release()

