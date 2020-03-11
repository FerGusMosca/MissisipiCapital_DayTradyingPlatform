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

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Smoothed14MinRSI",
                                                                        dayTradingPos.MinuteSmoothedRSIIndicator.RSI)

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "PrevSmoothed14MinRSI",
                                                                        dayTradingPos.MinuteSmoothedRSIIndicator.PrevRSI)

            self.TradingSignalManager.PersistSignalStatisticalParameter(tradingSignalId, "Daily41DaysRSI",
                                                                        dayTradingPos.DailyRSIIndicator.RSI)

            self.TradingSignalManager.Commit()

        except Exception as e:
            logger.DoLog("Critical error persisting trading signal for symbol {}:{}".format(
                         dayTradingPos.Security.Symbol if (dayTradingPos is not None and dayTradingPos.Security is not None) else "?",str(e)),
                         MessageType.ERROR)
        finally:
            if self.PersistingLock.locked():
                self.PersistingLock.release()

