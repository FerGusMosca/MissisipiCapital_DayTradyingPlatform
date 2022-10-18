from sources.framework.business_entities.positions.execution_summary import ExecutionSummary
from sources.framework.business_entities.securities.security import *
from sources.framework.business_entities.market_data.candle_bar import *
from sources.framework.common.enums.Side import *
from sources.framework.common.enums.PositionsStatus import PositionStatus
from sources.strategy.common.dto.position_statistical_parameters import *
from sources.strategy.common.dto.position_profits_and_losses import *
from sources.strategy.strategies.day_trader.business_entities.rsi_indicator import *
from sources.strategy.strategies.day_trader.business_entities.testers.rsi_indicator_tester import *
from sources.strategy.strategies.day_trader.business_entities.macd_indicator import *
from sources.strategy.strategies.day_trader.business_entities.macd_indicator_adjusted import *
from sources.strategy.strategies.day_trader.business_entities.testers.macd_indicator_adjusted_tester import *
from sources.strategy.strategies.day_trader.business_entities.bollinger_indicator import *
from sources.strategy.strategies.day_trader.business_entities.MS_strength_indicator import *
from sources.strategy.strategies.day_trader.business_entities.price_volatility_indicators import *
from sources.strategy.strategies.day_trader.business_entities.brooms_indicator import *
from sources.strategy.strategies.day_trader.business_entities.TG_indicator import *
from sources.strategy.strategies.day_trader.business_entities.volume_avg_indicator import *

from scipy import stats
import json
import statistics
import time
from datetime import datetime, timedelta
from json import JSONEncoder

#region Consts

_EXIT_TERM_COND_1="EXIT_TERM_COND_1"
_EXIT_TERM_COND_2="EXIT_TERM_COND_2"
_EXIT_TERM_COND_FLEX_STOP_LOSS="EXIT_TERM_COND_FLEX_STOP_LOSS"

_EXIT_LONG_COND_3="_EXIT_LONG_COND_3"
_EXIT_LONG_COND_4="_EXIT_LONG_COND_4"
_EXIT_LONG_COND_5="EXIT_LONG_COND_5"
_EXIT_LONG_COND_6="EXIT_LONG_COND_6"
_EXIT_TERM_COND_EOF="EXIT_TERM_COND_EOF"

_EXIT_SHORT_COND_1="EXIT_SHORT_COND_1"
_EXIT_SHORT_COND_2="EXIT_SHORT_COND_2"
_EXIT_SHORT_COND_3="EXIT_SHORT_COND_3"
_EXIT_SHORT_COND_4="EXIT_SHORT_COND_4"
_EXIT_SHORT_COND_5="EXIT_SHORT_COND_5"
_EXIT_SHORT_COND_6="EXIT_SHORT_COND_6"
_EXIT_SHORT_COND_EOF="EXIT_SHORT_COND_EOF"

_GENERIC_LONG_RULE_1="GENERIC_LONG_RULE_1"
_GENERIC_SHORT_RULE_1="GENERIC_SHORT_RULE_1"

_EXIT_LONG_MACD_RSI_COND_1="EXIT_LONG_MACD_RSI_COND_1"
_EXIT_LONG_MACD_RSI_COND_2="EXIT_LONG_MACD_RSI_COND_2"
_EXIT_LONG_MACD_RSI_COND_3="EXIT_LONG_MACD_RSI_COND_3"
_EXIT_LONG_MACD_RSI_COND_4="EXIT_LONG_MACD_RSI_COND_4"
_EXIT_LONG_MACD_RSI_COND_5="EXIT_LONG_MACD_RSI_COND_5"
_EXIT_LONG_MACD_RSI_COND_6="EXIT_LONG_MACD_RSI_COND_6"
_EXIT_LONG_MACD_RSI_COND_7="EXIT_LONG_MACD_RSI_COND_7"
_EXIT_LONG_MACD_RSI_COND_8="EXIT_LONG_MACD_RSI_COND_8"
_EXIT_LONG_MACD_RSI_COND_9="EXIT_LONG_MACD_RSI_COND_9"
_EXIT_LONG_MACD_RSI_COND_10="EXIT_LONG_MACD_RSI_COND_10"

_EXIT_SHORT_MACD_RSI_COND_1 = "EXIT_SHORT_MACD_RSI_COND_1"
_EXIT_SHORT_MACD_RSI_COND_2 = "EXIT_SHORT_MACD_RSI_COND_2"
_EXIT_SHORT_MACD_RSI_COND_3 = "EXIT_SHORT_MACD_RSI_COND_3"
_EXIT_SHORT_MACD_RSI_COND_4 = "EXIT_SHORT_MACD_RSI_COND_4"
_EXIT_SHORT_MACD_RSI_COND_5 = "EXIT_SHORT_MACD_RSI_COND_5"
_EXIT_SHORT_MACD_RSI_COND_6 = "EXIT_SHORT_MACD_RSI_COND_6"
_EXIT_SHORT_MACD_RSI_COND_7 = "EXIT_SHORT_MACD_RSI_COND_7"
_EXIT_SHORT_MACD_RSI_COND_8 = "EXIT_SHORT_MACD_RSI_COND_8"
_EXIT_SHORT_MACD_RSI_COND_9 = "EXIT_SHORT_MACD_RSI_COND_9"
_EXIT_SHORT_MACD_RSI_COND_10 = "EXIT_SHORT_MACD_RSI_COND_10"

_LONG_MACD_RSI_RULE_1="LONG_MACD_RSI_RULE_1"
_LONG_MACD_RSI_RULE_2="LONG_MACD_RSI_RULE_2"
_LONG_MACD_RSI_RULE_3="LONG_MACD_RSI_RULE_3"
_LONG_MACD_RSI_RULE_4="LONG_MACD_RSI_RULE_4"
_LONG_MACD_RSI_RULE_5="LONG_MACD_RSI_RULE_5"
_LONG_MACD_RSI_RULE_BROOMS="LONG_MACD_RSI_RULE_BROOMS"


_LONG_MACD_RSI_RULE_11_EXT_2="LONG_MACD_RSI_RULE_11_EXT_2"
_LONG_MACD_RSI_RULE_11_EXT_3="LONG_MACD_RSI_RULE_11_EXT_3"

_SHORT_MACD_RSI_RULE_11_EXT_2="SHORT_MACD_RSI_RULE_11_EXT_2"
_SHORT_MACD_RSI_RULE_11_EXT_3="SHORT_MACD_RSI_RULE_11_EXT_3"

_LONG_MACD_RSI_RULE_11_RED_1="LONG_MACD_RSI_RULE_11_RED_1"
_LONG_MACD_RSI_RULE_11_RED_2="LONG_MACD_RSI_RULE_11_RED_2"
_LONG_MACD_RSI_RULE_11_RED_3="LONG_MACD_RSI_RULE_11_RED_3"

_SHORT_MACD_RSI_RULE_11_RED_1="SHORT_MACD_RSI_RULE_11_RED_1"
_SHORT_MACD_RSI_RULE_11_RED_2="SHORT_MACD_RSI_RULE_11_RED_2"
_SHORT_MACD_RSI_RULE_11_RED_3="SHORT_MACD_RSI_RULE_11_RED_3"

_SHORT_MACD_RSI_RULE_1="SHORT_MACD_RSI_RULE_1"
_SHORT_MACD_RSI_RULE_2="SHORT_MACD_RSI_RULE_2"
_SHORT_MACD_RSI_RULE_3="SHORT_MACD_RSI_RULE_3"
_SHORT_MACD_RSI_RULE_4="SHORT_MACD_RSI_RULE_4"
_SHORT_MACD_RSI_RULE_5="SHORT_MACD_RSI_RULE_5"
_SHORT_MACD_RSI_RULE_BROOMS="SHORT_MACD_RSI_RULE_BROOMS"

_TERMINALLY_CLOSED ="TERMINALLY_CLOSED"
_INVALID_TIME_TRADE ="INVALID_TIME_TRADE"

_LONG_SHORT_ON_CANDLE_LONG_MARKET ="LONG_SHORT_ON_CANDLE_LONG_MARKET"
_LONG_SHORT_ON_CANDLE_SHORT_MARKET ="LONG_SHORT_ON_CANDLE_SHORT_MARKET"
_LONG_SHORT_ON_CANDLE_OFF ="LONG_SHORT_ON_CANDLE_OFF"

_REC_UNDEFINED = -1
_REC_GO_LONG_NOW = 0
_REC_GO_SHORT_NOW = 1
_REC_STAY_LONG = 2
_REC_STAY_SHORT = 3
_REC_EXIT_LONG_NOW = 4
_REC_EXIT_SHORT_NOW = 5
_REC_STAY_OUT= 5

_CANDLE_PRICE_METHOD_OPEN=1
_CANDLE_PRICE_METHOD_CLOSE=2
_CANDLE_PRICE_METHOD_AVERAGE=3
_CANDLE_PRICE_METHOD_CROSS=4

#endregion

class DayTradingPosition():

    #region Constructor

    def __init__(self,id ,security,shares,active,routing,open,longSignal,shortSignal,signalType=None,signalDesc=None):
        self.Id=id
        self.Security = security
        self.SharesQuantity= shares
        self.Active=active

        self.MarketData = None
        self.OpenMarketData=None

        self.ExecutionSummaries={}
        self.InnerSummaries={}
        self.Routing =routing
        #self.Open=open
        self.LongSignal = longSignal
        self.ShortSignal = shortSignal
        self.SignalType=signalType
        self.SignalDesc = signalDesc


        self.CurrentProfitToSecurity = 0
        self.CurrentProfit = 0
        self.CurrentProfitLastTrade = 0
        self.CurrentProfitMonetary = 0
        self.CurrentProfitMonetaryLastTrade = 0
        self.IncreaseDecrease = 0

        self.FirstInnerTradeProfitLastTrade=0
        self.SecondInnerTradeProfitLastTrade = 0

        self.MaxProfit = 0
        self.MaxLoss=0
        self.MaxProfitCurrentTrade = 0
        self.MaxMonetaryProfitCurrentTrade = 0
        self.MaxLossCurrentTrade = 0
        self.MaxMonetaryLossCurrentTrade = 0
        self.LastNDaysStdDev = 0
        self.PosUpdTimestamp = None

        self.RunningBacktest = False


        #region Terminal Conds
        self.TerminalClose = False
        self.TerminalCloseCond = None
        self.Recomendation = _REC_UNDEFINED
        self.ShowTradingRecommndations = False

        self.SoftTerminalCondEvaluated= None
        self.StrongTerminalCondEvaluated = None
        self.MomMarketCondition =None

        #endregion

        self.PricesReggrSlope = None
        self.PricesReggrSlopePeriod = None

        self.MinuteNonSmoothedRSIIndicator = RSIIndicator(False)
        self.MinuteSmoothedRSIIndicator = RSIIndicatorSmoothed()
        self.DailyRSIIndicator = RSIIndicator(False)
        #self.MACDIndicator = MACDIndicator()
        self.MACDIndicator = MACDIndicatorAdjusted()
        self.BollingerIndicator = BollingerIndicator()
        self.MSStrengthIndicator = MSStrengthIndicator()
        self.BroomsIndicator = BroomsIndicator()
        self.PriceVolatilityIndicators=PriceVolatilityIndicators()
        self.TGIndicator = TGIndicator()
        self.VolumeAvgIndicator=VolumeAvgIndicator()

        #tester= RSIIndicatorTester()
        #tester.DoTest()

        #macdTester = MACDIndicatorAdjustedTester()
        #macdTester.DoTest()

    def ResetExecutionSummaries(self):
        self.ExecutionSummaries = {}
        self.InnerSummaries={}

    def ResetProfitCounters(self,now):
        self.CurrentProfit = 0
        self.CurrentProfitLastTrade= 0
        self.CurrentProfitMonetary = 0
        self.CurrentProfitMonetaryLastTrade= 0
        self.CurrentProfitToSecurity = 0

        self.FirstInnerTradeProfitLastTrade = 0
        self.SecondInnerTradeProfitLastTrade = 0

        self.MaxLoss = 0
        self.MaxProfit = 0
        self.MaxProfitCurrentTrade = 0
        self.MaxMonetaryProfitCurrentTrade=0
        self.MaxLossCurrentTrade = 0
        self.MaxMonetaryLossCurrentTrade=0
        self.PosUpdTimestamp = now

        self.MinuteNonSmoothedRSIIndicator.Reset()#14
        self.MinuteSmoothedRSIIndicator.Reset()#30
        self.MACDIndicator.Reset()
        self.BollingerIndicator.Reset()
        self.MSStrengthIndicator.Reset()
        self.PriceVolatilityIndicators.Reset()
        self.TGIndicator.Reset()
        self.VolumeAvgIndicator.Reset()
        self.RunningBacktest= False

        #region Terminal Conditions
        self.TerminalClose = False
        self.TerminalCloseCond = None
        self.SoftTerminalCondEvaluated=None
        self.StrongTerminalCondEvaluated=None
        #endregion

        self.Recomendation=_REC_UNDEFINED
        self.ShowTradingRecommndations=False

        self.PricesReggrSlope = None
        self.PricesReggrSlopePeriod = None

        self.OpenMarketData=None
        self.MarketData = None

    #endregion

    #region Static Methods

    @staticmethod
    def _TERMINALLY_CLOSED():
        return _TERMINALLY_CLOSED

    @staticmethod
    def _INVALID_TIME_TRADE():
        return _INVALID_TIME_TRADE

    @staticmethod
    def _REC_GO_LONG_NOW():
        return _REC_GO_LONG_NOW

    @staticmethod
    def _REC_GO_SHORT_NOW():
        return _REC_GO_SHORT_NOW

    @staticmethod
    def _REC_STAY_OUT():
        return _REC_STAY_OUT

    @staticmethod
    def _REC_EXIT_LONG_NOW():
        return _REC_EXIT_LONG_NOW

    @staticmethod
    def _REC_STAY_LONG():
        return _REC_STAY_LONG

    @staticmethod
    def _REC_EXIT_SHORT_NOW():
        return _REC_EXIT_SHORT_NOW

    @staticmethod
    def _REC_STAY_SHORT():
        return _REC_STAY_SHORT

    #endregion

    #region Private Methods

    #region Summary Management

    def AppendInnerSummary(self,summary,posId):

        if self.GetLastTradedSummary() is not None:
            mainSummary = self.GetLastTradedSummary()
            if not mainSummary.DoInnerTradesExist():
                mainSummary.AppendFirstInnerSummary(summary)
            elif mainSummary.IsFirstInnerTradeOpen() and not mainSummary.IsSecondInnerTradeOpen():
                mainSummary.AppendSecondInnerSummary(summary)
            elif  mainSummary.IsFirstInnerTradeOpen() and  mainSummary.IsSecondInnerTradeOpen():
                raise Exception("First and Second Inner Position already opened for symbol {}".format(self.Security.Symbol))
        else:
            raise Exception("Could not find a Main Position to append an inner position for symbol {}".format(self.Security.Symbol))

        self.InnerSummaries[posId]=summary

    def GetNetOpenShares(self,summaryOrder=ExecutionSummary._MAIN_SUMMARY()):
        todaySummaries = sorted(list(filter(lambda x: x.CumQty >= 0
                                            and (self.RunningBacktest or x.Timestamp.date() == self.PosUpdTimestamp.date()),
                                            self.ExecutionSummaries.values())),
                                            key=lambda x: x.Timestamp, reverse=False)

        netShares = 0
        for summary in todaySummaries: # first we calculate the traded positions

            if summaryOrder==ExecutionSummary._MAIN_SUMMARY():
                netShares= self.UpdateSummaryNetShares(summary)
            elif  (summaryOrder==ExecutionSummary._INNER_SUMMARY_2() and summary.IsFirstInnerTradeOpen()):
                netShares= self.UpdateSummaryNetShares(summary.GetFirstInnerSummary())
            elif  (summaryOrder==ExecutionSummary._INNER_SUMMARY_3() and summary.IsSecondInnerTradeOpen()):
                netShares= self.UpdateSummaryNetShares(summary.GetSecondInnerSummary())
            else:
                raise Exception("Could not find an inner summay of order {} for symbol {}".format(summaryOrder,self.Security.Symbol))

        return netShares

    def GetOpenSummaries(self,summaryOrder):
        openSummaries =  list(filter(lambda x: x.Position.IsOpenPosition(), self.ExecutionSummaries.values()))

        if summaryOrder==ExecutionSummary._MAIN_SUMMARY():
            return openSummaries
        elif summaryOrder==ExecutionSummary._INNER_SUMMARY_2():
            innerSummaries = []

            for summary in openSummaries:
                if(summary.IsFirstInnerTradeOpen()):
                    innerSummaries.append(summary.GetFirstInnerSummary())
            return innerSummaries
        elif summaryOrder==ExecutionSummary._INNER_SUMMARY_3():
            innerSummaries = []

            for summary in openSummaries:
                if (summary.IsSecondInnerTradeOpen()):
                    innerSummaries.append(summary.GetSecondInnerSummary())
            return innerSummaries
        else:
            raise Exception("Could not find an inner summay of order {} for symbol {}".format(summaryOrder,self.Security.Symbol))

    def GetAceptedSummaries(self):

        return  sorted(list(filter(lambda x: x.Position.GetLastOrder() is not None or x.Position.IsRejectedPosition(),
                                   self.ExecutionSummaries.values())),
                                   key=lambda x: x.CreateTime,reverse=True)

    def GetLastTradedSummary(self,side=None):

        #All the traded summaries for a side, order in a descending fashion
        lastTradedSummaries = sorted(list(filter(lambda x: x.GetNetShares() != 0
                                                 and (self.RunningBacktest or x.Timestamp.date() == self.PosUpdTimestamp.date())
                                                 and ( side is None or ( x.Position.LongPositionOpened() if side==Side.Buy else x.Position.ShortPositionOpened())),
                                                 self.ExecutionSummaries.values())), key=lambda x: x.Timestamp, reverse=True)

        return lastTradedSummaries[0] if (len(lastTradedSummaries) > 0) else None

    def GetTradedSummaries(self):
        todaySummaries = sorted(list(filter(lambda x:      x.CumQty >= 0
                                                      and (self.RunningBacktest or x.Timestamp.date() == self.PosUpdTimestamp.date()),
                                            self.ExecutionSummaries.values())),
                                key=lambda x: x.Timestamp, reverse=False)
        return todaySummaries

    def DepurateSummaries(self):
        openSummaries = self.GetOpenSummaries(ExecutionSummary._MAIN_SUMMARY())

        for openSummary in openSummaries:
            openSummary.PosStatus = PositionStatus.Unknown
            openSummary.Position.PosStatus = PositionStatus.Unknown

        self.UpdateRouting()

        return openSummaries

    def UpdateRouting(self):
        firstOrderPos = self.GetOpenSummaries(ExecutionSummary._MAIN_SUMMARY())
        secondOrderPos = self.GetOpenSummaries(ExecutionSummary._INNER_SUMMARY_2())
        thirdOrderPos = self.GetOpenSummaries(ExecutionSummary._INNER_SUMMARY_3())

        self.Routing= (len(firstOrderPos)>0) or(len(secondOrderPos)>0) or (len(thirdOrderPos)>0)

    def UpdateSummaryNetShares(self, summary):
        netShares=0
        if summary.GetTradedSummary() > 0:
            if summary.SharesAcquired():
                netShares += summary.GetNetShares()
            else:
                netShares -= summary.GetNetShares()

        return netShares

    def FindSummary(self,posId):

        if posId in self.ExecutionSummaries:
            return self.ExecutionSummaries[posId]
        elif posId in self.InnerSummaries:
            return self.InnerSummaries[posId]
        else:
            return None

    #endregion

    #region Private Util/Aux

    def ProcessCandlebarPrices(self,msCandlePriceMethod,cbDict,candlebar):
        if msCandlePriceMethod.IntValue == _CANDLE_PRICE_METHOD_OPEN:
            candlebar.Close=candlebar.Open
            candlebar.High=candlebar.Open
            candlebar.Low=candlebar.Open
        elif msCandlePriceMethod.IntValue == _CANDLE_PRICE_METHOD_CLOSE:
            pass
        elif msCandlePriceMethod.IntValue == _CANDLE_PRICE_METHOD_AVERAGE:
            prevDateTime = candlebar.DateTime - timedelta(minutes=1)
            if prevDateTime in cbDict:
                prevCandle = cbDict[prevDateTime]
                avg = (prevCandle.Open + prevCandle.Close) / 2
                prevCandle.Open = avg
                prevCandle.High = avg
                prevCandle.Low = avg
                prevCandle.Close = avg

        elif  msCandlePriceMethod.IntValue == _CANDLE_PRICE_METHOD_CROSS:
            prevDateTime = candlebar.DateTime - timedelta(minutes=1)
            if prevDateTime in cbDict:
                prevCandle=cbDict[prevDateTime]
                prevCandle.Open=candlebar.Open
                prevCandle.High = candlebar.Open
                prevCandle.Low = candlebar.Open
                prevCandle.Close = candlebar.Open

        else:
            raise Exception("Invalid candle price method {}".format(msCandlePriceMethod.IntValue))

    # Formats like a.m. or p.m. times are converted to AM or PM
    def FormatTime(self, time):

        if str(time).endswith("a.m."):
            return time.replace("a.m.", "AM")
        elif str(time).endswith("a. m."):
            return time.replace("a. m.", "AM")
        elif str(time).endswith("p.m."):
            return time.replace("p.m.", "PM")
        elif str(time).endswith("p. m."):
            return time.replace("p. m.", "PM")
        else:
            return time

    def GetMov(self, candleBarArr, skip, length):
        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)),key=lambda x:x.DateTime,reverse = True)

        if sortedBars is None or len(sortedBars)<(length+skip):
            return None

        if length==0:
            raise Exception("Wrong value 0 for length calculating moving average")

        sum=0
        for i in range (skip,skip + length):
            if sortedBars[i] is not None:
                if sortedBars[i].Close is not None:
                    sum+=sortedBars[i].Close
                else:
                    return None
            else:
                return None #Not enough info to calculate

        return sum/length

    def GetReggrSlope (self,candleBarArr,length):

        arrayPrices = []
        arrayIndex = []

        i=length
        for candle in candleBarArr[-1*length:]:
            arrayPrices.append(candle.Close)
            arrayIndex.append(len(candleBarArr)-i)
            i-=1

        reggr= stats.linregress(arrayIndex,arrayPrices)
        #reggr = linregress(arrayPrices, arrayIndex)

        slope = (reggr.slope*100)/arrayPrices[-1]

        self.PricesReggrSlope = slope
        self.PricesReggrSlopePeriod = length

        return slope

    def GetSlope (self,currMovAvg,prevMovAvg):

        if currMovAvg is not None and prevMovAvg is not None and prevMovAvg!=0:
            return (currMovAvg-prevMovAvg)/prevMovAvg
        else:
            return None

    def Open(self):
        return self.GetNetOpenShares()!=0

    def GetSpecificBar(self,candleBarArr, index):
        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)),key=lambda x: x.DateTime, reverse=True)

        if(sortedBars is not None and len(sortedBars)>=index):
            return sortedBars[index-1]
        else:
            return None

    def GetMovOnData(self,candlebarsArr, skip, length):
        if len(candlebarsArr)> (length+skip):
            return self.GetMov(candlebarsArr,skip,length)
        elif len(candlebarsArr)> skip:
            return self.GetMov(candlebarsArr, skip, len(candlebarsArr)-skip)
        else:
            return 0

    def UpdateMarketData(self,marketData):
        if(marketData.MDEntryDate is not None):
            self.PosUpdTimestamp=self.PosUpdTimestamp.replace(hour=marketData.MDEntryDate.hour,
                                                              minute=marketData.MDEntryDate.minute,
                                                              second=marketData.MDEntryDate.second,
                                                              microsecond=0)
        else:
            self.PosUpdTimestamp = self.PosUpdTimestamp.replace(hour=datetime.now().hour,
                                                                minute=datetime.now().minute,
                                                                second=datetime.now().second,
                                                                microsecond=0)
        if self.OpenMarketData is None and marketData is not None and marketData.OpeningPrice is not None:
            self.OpenMarketData=marketData

    def SmoothMACDRSIParam(self,macdRSISmoothedMode,paramToComp,modelParamToSmooth,modelParamToSmoothIndex):
        if macdRSISmoothedMode.IntValue==0:
            return modelParamToSmooth.FloatValue
        else:
            return paramToComp / modelParamToSmoothIndex.FloatValue if paramToComp  is not None else 0

    def EvaluateTimeRange(self,candlebar,timeFromModelParam,timeToModelParam):
        now = candlebar.DateTime
        fromTimeLowVol = time.strptime( self.FormatTime( timeFromModelParam.StringValue), "%I:%M %p")
        toTimeLowVol = time.strptime( self.FormatTime ( timeToModelParam.StringValue), "%I:%M %p")
        todayStart = now.replace(hour=fromTimeLowVol.tm_hour, minute=fromTimeLowVol.tm_min, second=0, microsecond=0)
        todayEnd = now.replace(hour=toTimeLowVol.tm_hour, minute=toTimeLowVol.tm_min,
                               second=0, microsecond=0)
        return todayStart < now and now <todayEnd

    def EvaluateBiggerDate(self,candlebar ,timeFromModelParam):
        now = candlebar.DateTime
        fromTime = time.strptime( self.FormatTime( timeFromModelParam.StringValue), "%I:%M %p")
        todayStart = now.replace(hour=fromTime.tm_hour, minute=fromTime.tm_min, second=0, microsecond=0)
        return todayStart<now

    def EvaluateValidTimeToEnterTrade(self,candlebar,lowVolEntryThresholdModelParam,highVolEntryThresholdModelParam,
                                      lowVolFromTimeModelParam,lowVolToTimeModelParam,
                                      highVolFromTime1,highVolToTime1,highVolFromTime2,highVolToTime2):

        if(self.LastNDaysStdDev is not None):

            if (lowVolEntryThresholdModelParam.FloatValue is None or self.LastNDaysStdDev<lowVolEntryThresholdModelParam.FloatValue):
                if ( lowVolFromTimeModelParam.StringValue is not None and lowVolToTimeModelParam.StringValue is not None):
                    return  self.EvaluateTimeRange(candlebar,lowVolFromTimeModelParam,lowVolToTimeModelParam)
                else:
                    return True #I am in a lowVol env , but no time prefferences


            if (highVolEntryThresholdModelParam.FloatValue is None or self.LastNDaysStdDev >= highVolEntryThresholdModelParam.FloatValue):
                volEntry1 = False
                volEntry2 = False
                if (highVolFromTime1.StringValue is not None and highVolToTime1.StringValue is not None):
                    volEntry1 =  self.EvaluateTimeRange(candlebar,highVolFromTime1, highVolToTime1)

                if (  highVolFromTime2.StringValue is not None and highVolToTime2.StringValue is not None):
                    volEntry2 = self.EvaluateTimeRange(candlebar,highVolFromTime2, highVolToTime2)

                return volEntry1 or volEntry2

            return False

        else:
            return False

    #endregion

    #region Profits/Losses Statistics

    def CalculatePAndLForSummaries(self,summaries,marketData):
        profitsAndLosses = PositionsProfitsAndLosses()

        foundOpenPositions = self.CalculatePositionsProfit(profitsAndLosses, summaries)

        profitsAndLosses.PosMTM = self.CalculateMarkToMarket(marketData, profitsAndLosses, foundOpenPositions)

        profitsAndLosses.Profits = self.CalculatePercentageProfits(profitsAndLosses)
        profitsAndLosses.MonetaryProfits = self.CalculateMonetaryProfits(profitsAndLosses)

        return profitsAndLosses

    def GetNOrderTradedSummary(self,mainTradedSummaries,order):

        innerSummaries=[]

        for summary in mainTradedSummaries:

            if order==ExecutionSummary._INNER_SUMMARY_2() and summary.IsFirstInnerTradeOpen():
                innerSummaries.append(summary)
            elif order==ExecutionSummary._INNER_SUMMARY_3() and summary.IsSecondInnerTradeOpen():
                innerSummaries.append(summary)

        return innerSummaries

    def CalculateCurrentDayProfits(self,marketData):

        self.UpdateMarketData(marketData)

        mainTradedSummaries = self.GetTradedSummaries()
        mainTradesProfitsAndLosses = self.CalculatePAndLForSummaries(mainTradedSummaries,marketData)

        firstOrderSummaries= self.GetNOrderTradedSummary(mainTradedSummaries,ExecutionSummary._INNER_SUMMARY_2())
        firstOrderProfitsAndLosses = self.CalculatePAndLForSummaries(firstOrderSummaries, marketData)

        secondOrderSummaries = self.GetNOrderTradedSummary(mainTradedSummaries, ExecutionSummary._INNER_SUMMARY_3())
        secondOrderProfitsAndLosses = self.CalculatePAndLForSummaries(secondOrderSummaries, marketData)


        if self.Open():

            lastTradedSummary = self.GetLastTradedSummary()

            self.CalculateLastTradeProfit(lastTradedSummary,mainTradesProfitsAndLosses,marketData)

            if(lastTradedSummary.IsFirstInnerTradeOpen()):
                self.CalculateLastTradeProfit(lastTradedSummary.GetFirstInnerSummary(), firstOrderProfitsAndLosses, marketData)

            if (lastTradedSummary.IsSecondInnerTradeOpen()):
                self.CalculateLastTradeProfit(lastTradedSummary.GetSecondInnerSummary(), secondOrderProfitsAndLosses,marketData)

            if(mainTradesProfitsAndLosses.Profits>self.MaxProfit):
                self.MaxProfit=mainTradesProfitsAndLosses.Profits

            if(mainTradesProfitsAndLosses.Profits<self.MaxLoss):
                self.MaxLoss=mainTradesProfitsAndLosses.Profits

            if (mainTradesProfitsAndLosses.ProfitLastTrade > self.MaxProfitCurrentTrade):
                self.MaxProfitCurrentTrade = mainTradesProfitsAndLosses.ProfitLastTrade

            if (mainTradesProfitsAndLosses.ProfitLastTrade < self.MaxLossCurrentTrade):
                self.MaxLossCurrentTrade = mainTradesProfitsAndLosses.ProfitLastTrade

            if (mainTradesProfitsAndLosses.MonetaryProfitLastTrade > self.MaxMonetaryProfitCurrentTrade):
                self.MaxMonetaryProfitCurrentTrade = mainTradesProfitsAndLosses.MonetaryProfitLastTrade

            if (mainTradesProfitsAndLosses.MonetaryProfitLastTrade < self.MaxMonetaryLossCurrentTrade):
                self.MaxMonetaryLossCurrentTrade = mainTradesProfitsAndLosses.MonetaryProfitLastTrade

            self.CurrentProfit=mainTradesProfitsAndLosses.Profits
            self.CurrentProfitMonetary = mainTradesProfitsAndLosses.MonetaryProfits
            self.CurrentProfitLastTrade = mainTradesProfitsAndLosses.ProfitLastTrade
            self.CurrentProfitMonetaryLastTrade = mainTradesProfitsAndLosses.MonetaryProfitLastTrade
            self.IncreaseDecrease=mainTradesProfitsAndLosses.IncreaseDecrease

            self.FirstInnerTradeProfitLastTrade=firstOrderProfitsAndLosses.ProfitLastTrade
            self.SecondInnerTradeProfitLastTrade = secondOrderProfitsAndLosses.ProfitLastTrade

            if (self.SharesQuantity>0 and self.SharesQuantity!=0 and self.OpenMarketData is not None
                and self.OpenMarketData.OpeningPrice is not None and self.OpenMarketData.OpeningPrice!=0):
                self.CurrentProfitToSecurity= (self.CurrentProfitMonetary/(self.SharesQuantity*self.OpenMarketData.OpeningPrice))*100
        else:

            #Last Trade remains as the last estimation while was opened
            self.CurrentProfit = mainTradesProfitsAndLosses.Profits
            self.CurrentProfitMonetary = mainTradesProfitsAndLosses.MonetaryProfits
            self.IncreaseDecrease = 0
            self.MaxLossCurrentTrade=0
            self.MaxProfitCurrentTrade=0
            self.MaxMonetaryLossCurrentTrade = 0
            self.MaxMonetaryProfitCurrentTrade = 0

    def GetStatisticalParameters(self,candlebarsArr):
        fiftyMinNoSkipMovAvg = self.GetMovOnData(candlebarsArr, 0, 50)

        FiftyMinSkipTenMovAvg = self.GetMovOnData(candlebarsArr, 10, 50)

        threeMinNoSkipMovAvg = self.GetMovOnData(candlebarsArr, 0, 3)

        threeMinSkipTrheeMovAvg = self.GetMovOnData(candlebarsArr, 3, 3)

        threeMinSkipSixMovAvg = self.GetMovOnData(candlebarsArr, 6, 3)

        threeMinSkipNineMovAvg = self.GetMovOnData(candlebarsArr, 9, 3)

        barPosNow = self.GetSpecificBar(candlebarsArr, 1)
        barPosMinusThree = self.GetSpecificBar(candlebarsArr, 3)

        # Last 10 minute slope of 50 minute moving average
        tenMinSkipSlope = self.GetSlope(fiftyMinNoSkipMovAvg, FiftyMinSkipTenMovAvg)

        # Last 3 minute slope of 3 minute moving average
        threeMinSkipSlope = self.GetSlope(threeMinNoSkipMovAvg, threeMinSkipTrheeMovAvg)

        # Previous 3 to 6 minute slope of 3 minute moving average
        threeToSixMinSkipSlope = self.GetSlope(threeMinSkipTrheeMovAvg, threeMinSkipSixMovAvg)

        # Previous 6 to 9 minute slope of 3 minute moving average
        sixToNineMinSkipSlope = self.GetSlope(threeMinSkipSixMovAvg, threeMinSkipNineMovAvg)

        # Maximum change in last 3 minutes
        pctChangeLastThreeMinSlope = self.GetSlope(barPosNow.Close if barPosNow is not None else None, barPosMinusThree.Close if barPosMinusThree is not None else None)

        # Delta between current value and 50MMA
        deltaCurrValueAndFiftyMMov = self.GetSlope(barPosNow.Close if barPosNow is not None else None, fiftyMinNoSkipMovAvg)

        return PositionStatisticalParameters( tenMinSkipSlope=tenMinSkipSlope,
                                              threeMinSkipSlope=threeMinSkipSlope,
                                              threeToSixMinSkipSlope=threeToSixMinSkipSlope,
                                              sixToNineMinSkipSlope=sixToNineMinSkipSlope,
                                              pctChangeLastThreeMinSlope=pctChangeLastThreeMinSlope,
                                              deltaCurrValueAndFiftyMMov=deltaCurrValueAndFiftyMMov)

    def CalculateMonetaryProfits(self, profitsAndLosses):

        monProfits = 0  #USD

        if profitsAndLosses.NetShares > 0:
            monProfits = (profitsAndLosses.MoneyIncome + profitsAndLosses.PosMTM - profitsAndLosses.MoneyOutflow)
        elif profitsAndLosses.NetShares < 0: #in short positions, the PosMTM is negative
            monProfits=profitsAndLosses.MoneyIncome + profitsAndLosses.PosMTM - profitsAndLosses.MoneyOutflow
        else:
            monProfits = profitsAndLosses.MoneyIncome - profitsAndLosses.MoneyOutflow

        return monProfits

    def CalculatePercentageProfits(self,profitsAndLosses):

        profits = 0 #as a percentaje

        if profitsAndLosses.NetShares > 0:
            if (profitsAndLosses.MoneyOutflow > 0):
                profits = ((profitsAndLosses.MoneyIncome + profitsAndLosses.PosMTM) / profitsAndLosses.MoneyOutflow) - 1
            else:
                raise Exception("Could not calculate profit for a LONG position (+ {} shares) and not money outflow for symbol {}"
                                .format(profitsAndLosses.NetShares, self.Security.Symbol))
        elif profitsAndLosses.NetShares < 0:
            netToCover = profitsAndLosses.MoneyOutflow + (profitsAndLosses.PosMTM * (-1))#if short PosMTM should be negative

            if netToCover > 0:
                profits = (profitsAndLosses.MoneyIncome / netToCover)-1
            else:
                raise Exception("Could not calculate profit for a SHORT position where the money outflow is {} USD and the net ammount to cover is {} USD for symbol {}"
                                .format(profitsAndLosses.MoneyOutflow, profitsAndLosses.PosMTM, self.Security.Symbol))
        else: #all liquid
            if profitsAndLosses.MoneyOutflow > 0:
                profits = (profitsAndLosses.MoneyIncome / profitsAndLosses.MoneyOutflow)-1
            elif profitsAndLosses.MoneyIncome ==0:
                profits = 0
            else:
                raise Exception( "Could not calculate profit for closed position where money outflow is 0, for symbol {}" .format(self.Security.Symbol))

        #print("Outflow={} Inflow={} MTM={}".format(profitsAndLosses.MoneyOutflow,profitsAndLosses.MoneyIncome, profitsAndLosses.PosMTM))
        return profits*100 #as a percentage

    def CalculateMarkToMarket(self,marketData,profitsAndLosses,foundOpenPositions):

        posMTM=0

        if(marketData.Trade is not None):
            posMTM= marketData.Trade*profitsAndLosses.NetShares
        elif(marketData.ClosingPrice is not None):
            posMTM= marketData.ClosingPrice*profitsAndLosses.NetShares
        elif foundOpenPositions:
            raise Exception("Could not calculate profits as there are not last trade nor closing price for symbol "
                            .format(self.Security.Symbol))

        return posMTM

    def CalculateLastTradeProfit(self, lastTradedSummary,profitsAndLosses, marketData):


        if lastTradedSummary is not None and marketData.Trade is not None and lastTradedSummary.AvgPx is not None:
            profitsAndLosses.IncreaseDecrease = marketData.Trade-  lastTradedSummary.AvgPx
            if lastTradedSummary.SharesAcquired():#LONG
                profitsAndLosses.MonetaryProfitLastTrade=( marketData.Trade-lastTradedSummary.AvgPx)*lastTradedSummary.GetNetShares()
                profitsAndLosses.ProfitLastTrade = ((marketData.Trade/lastTradedSummary.AvgPx)-1)*100 if lastTradedSummary.AvgPx >0 else 0
            else:#SHORT
                profitsAndLosses.MonetaryProfitLastTrade = ( lastTradedSummary.AvgPx - marketData.Trade)*lastTradedSummary.GetNetShares()
                profitsAndLosses.ProfitLastTrade = ((lastTradedSummary.AvgPx/marketData.Trade)-1)*100 if marketData.Trade >0 else 0
        else:
            profitsAndLosses.MonetaryProfitLastTrade = 0
            profitsAndLosses.ProfitLastTrade = 0
            profitsAndLosses.IncreaseDecrease = 0

    def CalculatePositionsProfit(self,profitsAndLosses,todaySummaries):

        foundOpenPositions = False

        for summary in todaySummaries:
            # first we calculate the traded positions
            if summary.GetTradedSummary()>0:
                if summary.SharesAcquired():
                    profitsAndLosses.MoneyOutflow += summary.GetTradedSummary()
                    profitsAndLosses.NetShares += summary.GetNetShares()
                else:
                    profitsAndLosses.MoneyIncome += summary.GetTradedSummary()
                    profitsAndLosses.NetShares -= summary.GetNetShares()

            if summary.Position.IsOpenPosition():
                foundOpenPositions = True

        return foundOpenPositions

    #endregion

    #endregion

    #region Public Methods

    #region Public Util/Aux

    def CalculateStdDevForLastNDays(self,marketDataArr, numDaysModelParam):
        
        if numDaysModelParam.IntValue is None:
            raise Exception("Could not calculate las N days prices std. dev as there is not a number for N")

        prices = []

        for md in list( marketDataArr.values())[-1*numDaysModelParam.IntValue:]:
            prices.append(md.ClosingPrice)

        self.LastNDaysStdDev = statistics.stdev(prices)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    #endregion

    #region Automatic Trading Rules

    def EvaluateGenericShortTrade(self,dailyBiasModelParam,dailySlopeModelParam, posMaximShortChangeParam,
                           posMaxShortDeltaParam,nonSmoothed14MinRSIShortThreshold,candlebarsArr):

        if self.Open():
            #print ("Not opening because is opened:{}".format(self.Security.Symbol))
            return None #Position already opened

        if self.Routing:
            #print("Not opening because is routing:{}".format(self.Security.Symbol))
            return None #cannot open positions that are being routed

        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        #if statisticalParams.TenMinSkipSlope is not None:
            #print("Open Short - Ten Min Skip Slope {} for security {}".format(statisticalParams.TenMinSkipSlope,self.Security.Symbol))

        if  (statisticalParams.TenMinSkipSlope is None or statisticalParams.ThreeMinSkipSlope is None
            or statisticalParams.ThreeToSixMinSkipSlope is None or statisticalParams.SixToNineMinSkipSlope is None
            or statisticalParams.PctChangeLastThreeMinSlope is None or statisticalParams.DeltaCurrValueAndFiftyMMov is None):
            return None

        if  (   (dailyBiasModelParam.FloatValue is None or dailyBiasModelParam.FloatValue<0) #Daily Bias
                # Last 10 minute slope of 50 minute moving average
            and (dailySlopeModelParam.FloatValue is None or statisticalParams.TenMinSkipSlope < dailySlopeModelParam.FloatValue)
                # Last 3 minute slope of 3 minute moving average
            and (dailySlopeModelParam.FloatValue is None or statisticalParams.ThreeMinSkipSlope < dailySlopeModelParam.FloatValue)
                # Previous 3 to 6 minute slope of 3 minute moving average
            and (dailySlopeModelParam.FloatValue is None or statisticalParams.ThreeToSixMinSkipSlope < dailySlopeModelParam.FloatValue)
                # Previous 6 to 9 minute slope of 3 minute moving average
            and (dailySlopeModelParam.FloatValue is None or statisticalParams.SixToNineMinSkipSlope < dailySlopeModelParam.FloatValue)
                # Maximum change in last 3 minutes
            and (posMaximShortChangeParam.FloatValue is None or statisticalParams.PctChangeLastThreeMinSlope > posMaximShortChangeParam.FloatValue)
                # Delta between current value and 50MMA
            and (posMaxShortDeltaParam.FloatValue is None or statisticalParams.DeltaCurrValueAndFiftyMMov > posMaxShortDeltaParam.FloatValue)

        ):
            return _GENERIC_SHORT_RULE_1
        else:
            return None

    def GetShortInnerTradeQty(self, extendShort, subTrades2TradesParam, subTrades3TradesParam):

        if extendShort == _SHORT_MACD_RSI_RULE_11_EXT_2:
            return subTrades2TradesParam.IntValue
        elif extendShort == _SHORT_MACD_RSI_RULE_11_EXT_3:
            return subTrades3TradesParam.IntValue
        else:
            raise Exception("Short position extension condition not recognized for {}".format(extendShort))

    def EvaluateExtendingMACDRSIShortTrade(self,subTrade1AddLimit2,subTrade1AddLimit3):
        if not self.Open():  # we have to be open in order to extend the position
            return None  # Position already opened

        if self.GetNetOpenShares() >= 0:#We have to be a SHORT position
            return None

        if self.Routing:  # But it has to be NOT routing
            return None  # cannot open positions that are being routed

        openSummary1 = self.GetLastTradedSummary(Side.Sell)

        if(openSummary1 is None):
            openSummary1= self.GetLastTradedSummary(Side.SellShort)

        if(not openSummary1.DoInnerTradesExist()):
            if self.CurrentProfitLastTrade is not None and self.CurrentProfitLastTrade<subTrade1AddLimit2.FloatValue:
                return _SHORT_MACD_RSI_RULE_11_EXT_2
        elif (openSummary1.IsFirstInnerTradeOpen()):
            if self.FirstInnerTradeProfitLastTrade is not None and self.FirstInnerTradeProfitLastTrade<subTrade1AddLimit3.FloatValue:
                return _SHORT_MACD_RSI_RULE_11_EXT_3


        return None

    def EvaluateMACDRSIShortTrade(self,msNowParamA,msMinParamB,msMinParamBB,rsi30SlopeSkip5ParamC,msMaxMinParamD,msMaxMinParamDD,
                                  msNowMaxParamE,msNowParamF,msNowParamFF,rsi30SlopeSkip10ParamG,absMSMaxMinLast5ParamH,
                                  absMSMaxMinLast5ParamHH,sec5MinSlopeParamI,rsi14SlopeSkip3ExitParamV,ms3SlopeParamX,
                                  ms3SlopeParamXX,deltaDnParamXXX,broomsParamZ,broomsParamBias,macdRSISmoothedMode,absMaxMSPeriodParam,
                                  macdRsiOpenShortRule1ModelParam,macdRsiOpenShortRule2ModelParam,macdRsiOpenShortRule3ModelParam,
                                  macdRsiOpenShortRule4ModelParam,macdRsiOpenShortRuleBroomsModelParam,macdRsiStartTradingModelParam,
                                  dailyBiasMACDRSI,candlebarsArr):

        if self.Open():
            return None #Position already opened

        if self.Routing:
            return None #cannot open positions that are being routed

        if (self.MACDIndicator.MSPrev is None or self.MACDIndicator.MS is None or self.MACDIndicator.MaxMS is None \
                or self.MACDIndicator.MinMS is None or self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) is None
                or self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) is None or len(candlebarsArr)<5
                or self.MinuteNonSmoothedRSIIndicator.GetRSIReggr(3) is None or self.MACDIndicator.GetMSReggr(3) is None
                or (self.BroomsIndicator.BROOMS is None and macdRsiOpenShortRuleBroomsModelParam.IntValue>=1 )
                or not self.EvaluateBiggerDate(candlebarsArr[-1], macdRsiStartTradingModelParam)
                or self.BollingerIndicator.DeltaDN() is None
            ):
            return None

        # NO TRADE ON --> SHORT ON
        # line 1
        if (        self.MACDIndicator.MSPrev < msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MACDIndicator.MinMS < (-1 * self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMinParamB,msMinParamBB))
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) < (-1* rsi30SlopeSkip5ParamC.FloatValue)
                and macdRsiOpenShortRule1ModelParam.IntValue>=1):
            self.BollingerIndicator.OnTradeSignal()
            return _SHORT_MACD_RSI_RULE_1

        # line 2
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MACDIndicator.MinMS <  (-1 * self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMinParamB,msMinParamBB))
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) < (-1* rsi30SlopeSkip5ParamC.FloatValue)
                and macdRsiOpenShortRule2ModelParam.IntValue>=1
            ):
            self.BollingerIndicator.OnTradeSignal()
            return _SHORT_MACD_RSI_RULE_2

        # line 3
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS >= msNowParamA.FloatValue
                and self.MACDIndicator.MaxMS >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinParamD,msMaxMinParamDD)
                and (self.MACDIndicator.MaxMS > 0 and (self.MACDIndicator.MS / self.MACDIndicator.MaxMS) < msNowMaxParamE.FloatValue)
                and self.MACDIndicator.MS < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowParamF,msNowParamFF)
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) < (-1 * rsi30SlopeSkip5ParamC.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) < rsi30SlopeSkip10ParamG.FloatValue
                and self.MinuteNonSmoothedRSIIndicator.GetRSIReggr(3) < (-1*rsi14SlopeSkip3ExitParamV.FloatValue)
                and self.MACDIndicator.GetMSReggr(3) < (-1* self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,ms3SlopeParamX,ms3SlopeParamXX) )
                and macdRsiOpenShortRule3ModelParam.IntValue>=1
          ):
            self.BollingerIndicator.OnTradeSignal()
            return _SHORT_MACD_RSI_RULE_3

        # line 4
        if (    self.MACDIndicator.GetMaxAbsMSCrossover(absMaxMSPeriodParam.IntValue) < self.SmoothMACDRSIParam(macdRSISmoothedMode, self.MACDIndicator.AbsMaxMS, absMSMaxMinLast5ParamH, absMSMaxMinLast5ParamHH)
                and self.GetReggrSlope(candlebarsArr,5) < (-1 * sec5MinSlopeParamI.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) < (-1 *  rsi30SlopeSkip5ParamC.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) < rsi30SlopeSkip10ParamG.FloatValue
                and self.BollingerIndicator.DeltaDN() < deltaDnParamXXX.FloatValue
                and self.VolumeAvgIndicator.ValidateRule4()
                and macdRsiOpenShortRule4ModelParam.IntValue >= 1
                and dailyBiasMACDRSI.FloatValue<=0
            ):
            self.BollingerIndicator.OnTradeSignal()
            return _SHORT_MACD_RSI_RULE_4


        # line Brooms
        if (
                self.BroomsIndicator.BROOMS == broomsParamZ.FloatValue
            and broomsParamBias.FloatValue <=0
            and self.VolumeAvgIndicator.ValidateBroomsRule()
            and macdRsiOpenShortRuleBroomsModelParam.IntValue>=1
            and dailyBiasMACDRSI.FloatValue<=0
        ):
            self.BollingerIndicator.OnTradeSignal()
            return _SHORT_MACD_RSI_RULE_BROOMS



        return None

    def GetLongInnerTradeQty(self,extendLong,subTrades2TradesParam,subTrades3TradesParam ):

        if extendLong==_LONG_MACD_RSI_RULE_11_EXT_2:
            return subTrades2TradesParam.IntValue
        elif extendLong==_LONG_MACD_RSI_RULE_11_EXT_3:
            return subTrades3TradesParam.IntValue
        else:
            raise Exception("Long position extension condition not recognized for {}".format(extendLong))


    def EvaluateExtendingMACDRSILongTrade(self,subTrade1AddLimit2,subTrade1AddLimit3):

        if not self.Open():#we have to be open in order to extend the position
            return None  # Position already opened

        if self.GetNetOpenShares()<=0:#We have to be LONG
            return None

        if self.Routing:#But it has to be NOT routing
            return None  # cannot open positions that are being routed

        openSummary1 = self.GetLastTradedSummary(Side.Buy)

        if openSummary1 is not None:

            if (not openSummary1.DoInnerTradesExist()):#No inner trades (trade #2 or trade #3)
                if self.CurrentProfitLastTrade is not None and self.CurrentProfitLastTrade < subTrade1AddLimit2.FloatValue:
                    return _LONG_MACD_RSI_RULE_11_EXT_2
            elif (openSummary1.IsFirstInnerTradeOpen()):
                if self.FirstInnerTradeProfitLastTrade is not None and self.FirstInnerTradeProfitLastTrade < subTrade1AddLimit3.FloatValue:
                    return _LONG_MACD_RSI_RULE_11_EXT_3

        return None

    def EvaluateMACDRSILongTrade(self,msNowParamA,msMinParamB,msMinParamBB,rsi30SlopeSkip5ParamC,broomsParamCC,broomsParamBias,
                                 msMaxMinParamD,msMaxMinParamDD,msNowMaxParamE,msNowParamF,msNowParamFF, rsi30SlopeSkip10ParamG,
                                 absMSMaxMinLast5ParamH,absMSMaxMinLast5ParamHH,sec5MinSlopeParamI, rsi14SlopeSkip3ExitParamV,
                                 ms3SlopeParamX,ms3SlopeParamXX,deltaUpParamYYY,macdRSISmoothedMode,absMaxMSPeriodParam,
                                 macdRsiOpenLongRule1ModelParam,macdRsiOpenLongRule2ModelParam,macdRsiOpenLongRule3ModelParam,
                                 macdRsiOpenLongRule4ModelParam,macdRsiOpenLongRuleBroomsModelParam,macdRsiStartTradingModelParam,
                                 dailyBiasMACDRSI,candlebarsArr):

        if self.Open():
            return None  # Position already opened

        if self.Routing:
            return None  # cannot open positions that are being routed


        if (self.MACDIndicator.MSPrev is None or self.MACDIndicator.MS is None or self.MACDIndicator.MaxMS is None\
            or self.MACDIndicator.MinMS is None or self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) is None
            or self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) is None or len(candlebarsArr)<5
            or self.MinuteNonSmoothedRSIIndicator.GetRSIReggr(3) is None or self.MACDIndicator.GetMSReggr(3) is None
            or not self.EvaluateBiggerDate(candlebarsArr[-1],macdRsiStartTradingModelParam)
            or (self.BroomsIndicator.BROOMS is None and macdRsiOpenLongRuleBroomsModelParam.IntValue>=1)
            or self.BollingerIndicator.DeltaUP() is None
            ):
            return None

        #NO TRADE ON --> LONG ON
        #line 1
        if (self.MACDIndicator.MSPrev >=msNowParamA.FloatValue and self.MACDIndicator.MS >=msNowParamA.FloatValue
            and self.MACDIndicator.MaxMS >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMinParamB,msMinParamBB)
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5)>rsi30SlopeSkip5ParamC.FloatValue
            and macdRsiOpenLongRule1ModelParam.IntValue>=1
            ):
            self.BollingerIndicator.OnTradeSignal()
            return _LONG_MACD_RSI_RULE_1

        # line 2
        if (self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS >=msNowParamA.FloatValue
            and self.MACDIndicator.MaxMS >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMinParamB,msMinParamBB)
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5)>rsi30SlopeSkip5ParamC.FloatValue
            and macdRsiOpenLongRule2ModelParam.IntValue>=1
            ):
            self.BollingerIndicator.OnTradeSignal()
            return _LONG_MACD_RSI_RULE_2

        # line 3
        if (self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS < msNowParamA.FloatValue
            and self.MACDIndicator.MinMS < (-1* self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinParamD,msMaxMinParamDD))
            and (self.MACDIndicator.MinMS>0 and (self.MACDIndicator.MS / self.MACDIndicator.MinMS ) < msNowMaxParamE.FloatValue)
            and self.MACDIndicator.MS >=(-1*  self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowParamF,msNowParamFF))
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) > rsi30SlopeSkip5ParamC.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) >= (-1 * rsi30SlopeSkip10ParamG.FloatValue)
            and self.MinuteNonSmoothedRSIIndicator.GetRSIReggr(3) >= rsi14SlopeSkip3ExitParamV.FloatValue
            and self.MACDIndicator.GetMSReggr(3) >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,ms3SlopeParamX,ms3SlopeParamXX)
            and macdRsiOpenLongRule3ModelParam.IntValue>=1

            ):
            self.BollingerIndicator.OnTradeSignal()
            return _LONG_MACD_RSI_RULE_3


        # line 4
        if (    self.MACDIndicator.GetMaxAbsMSCrossover(absMaxMSPeriodParam.IntValue) < self.SmoothMACDRSIParam(macdRSISmoothedMode, self.MACDIndicator.AbsMaxMS, absMSMaxMinLast5ParamH, absMSMaxMinLast5ParamHH)
            and self.GetReggrSlope(candlebarsArr,5) >= sec5MinSlopeParamI.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) > rsi30SlopeSkip5ParamC.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) >= (-1 * rsi30SlopeSkip10ParamG.FloatValue)
            and self.BollingerIndicator.DeltaUP() > deltaUpParamYYY.FloatValue
            and self.VolumeAvgIndicator.ValidateRule4()
            and macdRsiOpenLongRule4ModelParam.IntValue >= 1
            and dailyBiasMACDRSI.FloatValue >= 0
          ):
            self.BollingerIndicator.OnTradeSignal()
            return _LONG_MACD_RSI_RULE_4

        # line BROOMS
        if(
                self.BroomsIndicator.BROOMS ==broomsParamCC.FloatValue
            and broomsParamBias.FloatValue >=0
            and self.VolumeAvgIndicator.ValidateBroomsRule()
            and macdRsiOpenLongRuleBroomsModelParam.IntValue>=1
            and dailyBiasMACDRSI.FloatValue >= 0

        ):
            self.BollingerIndicator.OnTradeSignal()
            return _LONG_MACD_RSI_RULE_BROOMS


        return None

    def EvaluateGenericLongTrade(self,dailyBiasModelParam,dailySlopeModelParam, posMaximChangeParam,
                          posMaxLongDeltaParam,nonSmoothed14MinRSILongThreshold,candlebarsArr):

        if self.Open():
            #print ("Not opening because is opened:{}".format(self.Security.Symbol))
            return None #Position already opened

        if self.Routing:
            #print("Not opening because is routing:{}".format(self.Security.Symbol))
            return None #cannot open positions that are being routed

        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        if  (statisticalParams.TenMinSkipSlope is None or statisticalParams.ThreeMinSkipSlope is None
            or statisticalParams.ThreeToSixMinSkipSlope is None or statisticalParams.SixToNineMinSkipSlope is None
            or statisticalParams.PctChangeLastThreeMinSlope is None or statisticalParams.DeltaCurrValueAndFiftyMMov is None):
            return None


        if  (   (dailyBiasModelParam.FloatValue is None or dailyBiasModelParam.FloatValue>=0 ) #Daily Bias
                # Last 10 minute slope of 50 minute moving average
            and  (dailySlopeModelParam.FloatValue is None or  statisticalParams.TenMinSkipSlope >= dailySlopeModelParam.FloatValue)
                # Last 3 minute slope of 3 minute moving average
            and (dailySlopeModelParam.FloatValue is None or statisticalParams.ThreeMinSkipSlope >= dailySlopeModelParam.FloatValue)
                # Previous 3 to 6 minute slope of 3 minute moving average
            and (dailySlopeModelParam.FloatValue is None  or statisticalParams.ThreeToSixMinSkipSlope > dailySlopeModelParam.FloatValue)
                # Previous 6 to 9 minute slope of 3 minute moving average
            and (dailySlopeModelParam.FloatValue is None or statisticalParams.SixToNineMinSkipSlope > dailySlopeModelParam.FloatValue)
                # Maximum change in last 3 minutes
            and (posMaximChangeParam.FloatValue is None or statisticalParams.PctChangeLastThreeMinSlope < posMaximChangeParam.FloatValue)
                # Delta between current value and 50MMA
            and (posMaximChangeParam.FloatValue is None or statisticalParams.DeltaCurrValueAndFiftyMMov < posMaxLongDeltaParam.FloatValue)

            ):
            return _GENERIC_LONG_RULE_1
        else:
            return None

    def RunRuleTenShortPos(self,slFlipModelParam,changeFixedLossAtThisGainParam,gainMinTradeParamFixedLoss,gainMinTradeParamFixedLoss2):

        if (slFlipModelParam.IntValue == 1):  # enabled

            if (self.MaxProfitCurrentTrade > changeFixedLossAtThisGainParam.FloatValue):
                if self.CurrentProfit < gainMinTradeParamFixedLoss2.FloatValue:
                    return _EXIT_SHORT_MACD_RSI_COND_10
                else:
                    return None
            else:
                if self.CurrentProfit < gainMinTradeParamFixedLoss.FloatValue:
                    return _EXIT_SHORT_MACD_RSI_COND_10
                else:
                    return None
        else:
            return None

    def ConvertReducingCondToSummaryOrder(self, reducingCond):
        if (reducingCond==_SHORT_MACD_RSI_RULE_11_RED_1 or reducingCond==_LONG_MACD_RSI_RULE_11_RED_1 ):
            return ExecutionSummary._MAIN_SUMMARY()
        elif (reducingCond==_SHORT_MACD_RSI_RULE_11_RED_2 or reducingCond==_LONG_MACD_RSI_RULE_11_RED_2 ):
            return ExecutionSummary._INNER_SUMMARY_2()
        elif (reducingCond==_SHORT_MACD_RSI_RULE_11_RED_3 or reducingCond==_LONG_MACD_RSI_RULE_11_RED_3 ):
            return ExecutionSummary._INNER_SUMMARY_3()
        else:
            raise Exception("Could not find a reducing Condigtion {} to translate for Symbol {} @ConvertReducingCondToSummaryOrder",reducingCond,self.Security.Symbol)

    def EvaluateReducingMACDRSIShortTrade(self,subTrade1GainLimit1,subTrade2GainLimit2,subTrade1GainLimit2,subTrade2LossLimit2,subTrade3GainLimit3,subTrade3LossLimit3):
        if not  self.Open():  # we have to be open in order to extend the position
            return None  # Position already opened

        if self.GetNetOpenShares() < 0:
            return None

        if self.Routing:  # But it has to be NOT routing
            return None  # cannot open positions that are being routed

        if self.CurrentProfitLastTrade is None:
            return

        reducingConds=[]

        openSummary1 = self.GetLastTradedSummary(Side.Sell)

        if (openSummary1 is None):
            openSummary1 = self.GetLastTradedSummary(Side.SellShort)

            if (not openSummary1.DoInnerTradesExist()):
                if self.CurrentProfitLastTrade is not None and self.CurrentProfitLastTrade >= subTrade1GainLimit1.FloatValue:
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_1)
            elif (openSummary1.IsFirstInnerTradeOpen()):
                if self.FirstInnerTradeProfitLastTrade is not None and self.FirstInnerTradeProfitLastTrade >= subTrade2GainLimit2.FloatValue:
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_1)
                    if self.CurrentProfitLastTrade is not None and self.FirstInnerTradeProfitLastTrade >= subTrade1GainLimit2.FloatValue:
                        reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_2)
                if self.FirstInnerTradeProfitLastTrade is not None and self.FirstInnerTradeProfitLastTrade < subTrade2LossLimit2.FloatValue:
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_1)
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_2)
            elif (openSummary1.IsSecondInnerTradeOpen()):
                if self.SecondInnerTradeProfitLastTrade is not None and self.SecondInnerTradeProfitLastTrade >= subTrade3GainLimit3.FloatValue:
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_1)
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_2)
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_3)
                if self.SecondInnerTradeProfitLastTrade is not None and self.SecondInnerTradeProfitLastTrade < subTrade3LossLimit3.FloatValue:
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_1)
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_2)
                    reducingConds.append(_SHORT_MACD_RSI_RULE_11_RED_3)

        return None if len(reducingConds)==0 else reducingConds

    def EvaluateClosingMACDRSIShortTrade(self,candlebarsArr,msNowParamA,macdMaxGainParamJ,macdMaxGainParamJJ,gainMaxTradeParamJJJ,
                                         gainMaxTradeParamSDMult,gainMaxTradeParamFixedGain,macdGainNowMaxParamK,
                                         rsi30SlopeSkip5ExitParamL,rsi30Skip5ParamLX,msNowExitParamN,msNowExitParamNN,msMaxMinExitParamNBis,
                                         msMaxMinExitParamNNBis,msNowMaxMinExitParamP,msNowExitParamQ,msNowExitParamQQ,
                                         rsi30SlopeSkip10ExitParamR,msMaxMinExitParamS,msMaxMinExitParamSS,sec5MinSlopeExitParamT,
                                         gainMinStopLossExitParamU,gainMinStopLossExitParamUU,gainMinTradeParamUUU,
                                         gainMinTradeParamFixedLoss,gainMinTradeParamFixedLoss2,changeFixedLossAtThisGainParam,gainMinStopLossExitParamW,
                                         gainMinStopLossExitParamWW,gainStopLossExitParamY, gainMinStopLossExitParamZ,
                                         gainMinStopLossExitParamZZ,endOfdayLimitModelParam,takeGainLimitModelParam,
                                         stopLossLimitModelParam,implFlexibeStopLoss,flexibleStopLossL1ModelParam,
                                         macdRSISmoothedMode,absMaxMSPeriodParam,macdRsiCloseShortRule1ModelParam,
                                         macdRsiCloseShortRule2ModelParam,macdRsiCloseShortRule3ModelParam,
                                         macdRsiCloseShortRule4ModelParam,macdRsiCloseShortRule5ModelParam,
                                         macdRsiCloseShortRule6ModelParam,macdRsiCloseShortRule7ModelParam,
                                         macdRsiCloseShortRule8ModelParam,macdRsiCloseShortRule9ModelParam,
                                         slFlipModelParam):


        openQty=1
        if not self.Open():
            return None  # Position not opened

        if self.GetNetOpenShares() >0 :
            return None  # We are in a LONG position
        else:
            openQty= abs(self.GetNetOpenShares()) if self.GetNetOpenShares()!=0 else 1

        '''
        #Rule TERMINAL --> Positions are not closed. They won't just be opened again
        terminalCond = self.EvaluateSoftTerminalCondition(candlebarsArr,takeGainLimitModelParam,stopLossLimitModelParam,
                                                             implFlexibeStopLoss, flexibleStopLossL1ModelParam)

        if terminalCond is not None:
            self.TerminalClose =True
            self.TerminalCloseCond = terminalCond #This won't be closed. It won't just open another position again
            #return terminalCond
        '''

        # Rule STRONG TERMINAL --> Positions are closed and They won't just be opened again
        eodCond = self.EvaluateStrongTerminal(candlebarsArr, endOfdayLimitModelParam)

        if eodCond is not None:
            self.TerminalClose = True
            self.TerminalCloseCond = eodCond  # This WILL be closed
            return eodCond

        if (self.CurrentProfitLastTrade is None or self.MaxMonetaryLossCurrentTrade is None or self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) is None
                or self.MACDIndicator.MSPrev is None or self.MACDIndicator.MS is None or self.MACDIndicator.MaxMS is None
                or self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) is None
                or self.MaxMonetaryLossCurrentTrade is None or self.MaxMonetaryProfitCurrentTrade is None
                or self.CurrentProfitMonetaryLastTrade is None or self.BollingerIndicator.TPSDStartOfTrade is None
                or self.PriceVolatilityIndicators.LastSDDDaysOpenStdDev is None
                or len(candlebarsArr)<5
                #or self.MACDIndicator.GetMaxABSMaxMinMS(5) is None
            ):
            return None

        #=================== NOW WE START WITH THE ALGO NON TERMINAL RULES =============================
        # SHORT ON --> NO TRADE ON
        # rule 1
        if (    (self.MaxMonetaryProfitCurrentTrade/openQty) >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,macdMaxGainParamJ,macdMaxGainParamJJ)
            and (self.MaxMonetaryProfitCurrentTrade > 0 and self.TGIndicator.HasValidValue() and ((self.CurrentProfitMonetaryLastTrade / self.MaxMonetaryProfitCurrentTrade) < self.TGIndicator.K))
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) > rsi30Skip5ParamLX.FloatValue
            and (self.MaxMonetaryProfitCurrentTrade/openQty) >= (self.BollingerIndicator.TPSDStartOfTrade*gainMaxTradeParamJJJ.FloatValue)
            and (self.MaxProfitCurrentTrade  >= gainMaxTradeParamSDMult.FloatValue * self.PriceVolatilityIndicators.LastSDDDaysOpenStdDev)
            and (self.MaxProfitCurrentTrade >= gainMaxTradeParamFixedGain.FloatValue)
            and macdRsiCloseShortRule1ModelParam.IntValue>=1
            ):
            return _EXIT_SHORT_MACD_RSI_COND_1

        # rule 2
        if (    self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
            and self.MACDIndicator.MS >= msNowParamA.FloatValue
            and self.MACDIndicator.MS >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowExitParamN,msNowExitParamNN)
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) > rsi30SlopeSkip5ExitParamL.FloatValue
            and macdRsiCloseShortRule2ModelParam.IntValue>=1
        ):
            return _EXIT_SHORT_MACD_RSI_COND_2

        # rule 3
        if (    self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
            and self.MACDIndicator.MS >= msNowParamA.FloatValue
            and (self.MaxMonetaryLossCurrentTrade/openQty) < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamW,gainMinStopLossExitParamWW))
            and self.VolumeAvgIndicator.ValidateIfEnoughData()
            and macdRsiCloseShortRule3ModelParam.IntValue>=1
        ):
            return _EXIT_SHORT_MACD_RSI_COND_3

        # rule 4
        if (    self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS >= msNowParamA.FloatValue
            and self.MACDIndicator.MS >=  ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinExitParamNBis,msMaxMinExitParamNNBis))
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) > rsi30SlopeSkip5ExitParamL.FloatValue
            and self.VolumeAvgIndicator.ValidateIfEnoughData()
            and macdRsiCloseShortRule4ModelParam.IntValue>=1
        ):
            return _EXIT_SHORT_MACD_RSI_COND_4

        # rule 5
        if (    self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS >= msNowParamA.FloatValue
            and (self.MaxMonetaryLossCurrentTrade/openQty) < gainMinStopLossExitParamW.FloatValue
            and self.VolumeAvgIndicator.ValidateIfEnoughData()
            and macdRsiCloseShortRule5ModelParam.IntValue>=1
        ):
            return _EXIT_SHORT_MACD_RSI_COND_5

        # rule 6
        if (    self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS < msNowParamA.FloatValue
            and self.MACDIndicator.MinMS < (-1* self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinExitParamNBis,msMaxMinExitParamNNBis))
            and (self.MACDIndicator.MinMS >0 and ((self.MACDIndicator.MS/self.MACDIndicator.MinMS)<msNowMaxMinExitParamP.FloatValue))
            and self.MACDIndicator.MS >= (-1 * self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowExitParamQ,msNowExitParamQQ))
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) > rsi30SlopeSkip5ExitParamL.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) >= (-1*rsi30SlopeSkip10ExitParamR.FloatValue)
            and self.VolumeAvgIndicator.ValidateIfEnoughData()
            and macdRsiCloseShortRule6ModelParam.IntValue>=1
        ):
            return _EXIT_SHORT_MACD_RSI_COND_6


        # rule 7
        if (
                self.MACDIndicator.GetMaxAbsMSCrossover(absMaxMSPeriodParam.IntValue) < self.SmoothMACDRSIParam(macdRSISmoothedMode, self.MACDIndicator.AbsMaxMS, msMaxMinExitParamS, msMaxMinExitParamSS)
            and self.GetReggrSlope(candlebarsArr,5) >= sec5MinSlopeExitParamT.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) >  rsi30SlopeSkip5ExitParamL.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) >= (-1* rsi30SlopeSkip10ExitParamR.FloatValue)
            and self.VolumeAvgIndicator.ValidateIfEnoughData()
            and macdRsiCloseShortRule7ModelParam.IntValue>=1
        ):
            return _EXIT_SHORT_MACD_RSI_COND_7

        #rule 8
        if (    self.MACDIndicator.GetMaxAbsMSCrossover(absMaxMSPeriodParam.IntValue) < msMaxMinExitParamS.FloatValue
            and (self.MaxMonetaryLossCurrentTrade/openQty) < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamZ,gainMinStopLossExitParamZZ))
            and self.VolumeAvgIndicator.ValidateIfEnoughData()
            and macdRsiCloseShortRule8ModelParam.IntValue>=1
            ):
            return _EXIT_SHORT_MACD_RSI_COND_8

        # rule 9
        if (        (self.MaxMonetaryLossCurrentTrade/openQty) < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamU,gainMinStopLossExitParamUU))
                and (self.MaxMonetaryLossCurrentTrade/openQty) < (-1*self.BollingerIndicator.TPSDStartOfTrade*gainMinTradeParamUUU.FloatValue)
                #and (self.MaxMonetaryLossCurrentTrade / openQty) < gainMinTradeParamFixedLoss.FloatValue
                and (self.MaxLossCurrentTrade<gainMinTradeParamFixedLoss.FloatValue)
                and macdRsiCloseShortRule9ModelParam.IntValue>=1
            ):
            return _EXIT_SHORT_MACD_RSI_COND_9


        ruleTenCond=self.RunRuleTenShortPos(slFlipModelParam,changeFixedLossAtThisGainParam,gainMinTradeParamFixedLoss,gainMinTradeParamFixedLoss2)

        if(ruleTenCond is not None):
            return ruleTenCond


        return None



    def EvaluateClosingGenericShortTrade(self,candlebarsArr,
                                  maxGainForClosingModelParam,pctMaxGainForClosingModelParam,
                                  maxLossForClosingModelParam,pctMaxLossForClosingModelParam,
                                  takeGainLimitModelParam,stopLossLimitModelParam,
                                  implFlexibeStopLoss, flexibleStopLossL1ModelParam,
                                  pctSlopeToCloseShortModelParam,
                                  endOfdayLimitModelParam,
                                  nonSmoothed14MinRSILongThreshold):



        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        #if statisticalParams.TenMinSkipSlope is not None:
            #print( "Close Short Trade - Ten Min Skip Slope {} for security {}".format(statisticalParams.TenMinSkipSlope, self.Security.Symbol))


        if not self.Open():
            return None #Position not opened

        if self.GetNetOpenShares()>0:
            return None#We are in a long position


        '''
        # Rule TERMINAL --> Positions are not closed. They won't just be opened again
        terminalCond = self.EvaluateSoftTerminalCondition(candlebarsArr, takeGainLimitModelParam,stopLossLimitModelParam,
                                                             implFlexibeStopLoss, flexibleStopLossL1ModelParam)

        if terminalCond is not None:
            self.TerminalClose = True
            self.TerminalCloseCond = terminalCond  # This won't be closed. It won't just open another position again
            # return terminalCond
        '''

        # Rule STRONG TERMINAL --> Positions are closed and They won't just be opened again
        eodCond = self.EvaluateStrongTerminal(candlebarsArr, endOfdayLimitModelParam)

        if eodCond is not None:
            self.TerminalClose = True
            self.TerminalCloseCond = eodCond  # This WILL be closed
            return eodCond

        # Maximum Gain during the trade exceeds a certain value and then drops to a percentage of that value
        #rule 3
        if (    self.MaxProfitCurrentTrade is not None
            and self.CurrentProfitLastTrade is not None
            and (maxGainForClosingModelParam.FloatValue is not None and self.MaxProfitCurrentTrade >= maxGainForClosingModelParam.FloatValue * 100)
            and (pctMaxGainForClosingModelParam.FloatValue is not None and (self.CurrentProfitLastTrade < pctMaxGainForClosingModelParam.FloatValue * self.MaxProfitCurrentTrade))
        ):
            return _EXIT_SHORT_COND_3

        # Maximum Loss during the trade exceeds (worse than) a certain value and then drops to a percentage of that value
        #rule 4
        if (    self.CurrentProfitLastTrade is not None
            and self.MaxLossCurrentTrade is not None
            and (maxLossForClosingModelParam.FloatValue is not None and self.MaxLossCurrentTrade <= (maxLossForClosingModelParam.FloatValue * 100))
            and self.CurrentProfit < 0
        ):
            absProfit = self.CurrentProfitLastTrade if self.CurrentProfitLastTrade > 0 else (-1 * self.CurrentProfit)
            absMaxLoss = self.MaxLossCurrentTrade if self.MaxLossCurrentTrade > 0 else (-1 * self.MaxLossCurrentTrade)
            if (absProfit < (pctMaxLossForClosingModelParam.FloatValue * absMaxLoss)):
                return _EXIT_SHORT_COND_4

        #Last 3 minute slope of 3 minute moving average exceeds a certain value AGAINST the Trade
        #rule 5
        if(     statisticalParams.ThreeMinSkipSlope is not None
            and ( pctSlopeToCloseShortModelParam.FloatValue is not None and statisticalParams.ThreeMinSkipSlope >= pctSlopeToCloseShortModelParam.FloatValue)):
            return _EXIT_SHORT_COND_5


        return None


    def RunRuleTenLongPos(self,slFlipModelParam,changeFixedLossAtThisGainParam,gainMinTradeParamFixedLoss,gainMinTradeParamFixedLoss2):
        # rule 10
        if (slFlipModelParam.IntValue == 1):  # enabled

            if (self.MaxProfitCurrentTrade > changeFixedLossAtThisGainParam.FloatValue):
                if self.CurrentProfit < gainMinTradeParamFixedLoss2.FloatValue:
                    return _EXIT_LONG_MACD_RSI_COND_10
                else:
                    return None
            else:
                if self.CurrentProfit < gainMinTradeParamFixedLoss.FloatValue:
                    return _EXIT_LONG_MACD_RSI_COND_10
                else:
                    return None
        else:
            return None

    def EvaluateReducingMACDRSILongTrade(self,subTrade1GainLimit1,subTrade2GainLimit2,subTrade1GainLimit2,subTrade2LossLimit2,subTrade3GainLimit3,subTrade3LossLimit3):
        if not self.Open():  # we have to be open in order to extend the position
            return None  # Position already opened

        if self.GetNetOpenShares() >0: #we must have a LONG trade
            return None

        if self.Routing:  # But it has to be NOT routing
            return None  # cannot open positions that are being routed

        if self.CurrentProfitLastTrade is None:
            return

        reducingConds = []

        openSummary1 = self.GetLastTradedSummary(Side.Sell)

        if (openSummary1 is None):
            openSummary1 = self.GetLastTradedSummary(Side.SellShort)

            if (not openSummary1.DoInnerTradesExist()):
                if self.CurrentProfitLastTrade is not None and self.CurrentProfitLastTrade >= subTrade1GainLimit1.FloatValue:
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_1)
            elif (openSummary1.IsFirstInnerTradeOpen()):
                if self.FirstInnerTradeProfitLastTrade is not None and self.FirstInnerTradeProfitLastTrade >= subTrade2GainLimit2.FloatValue:
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_1)
                    if self.CurrentProfitLastTrade is not None and self.FirstInnerTradeProfitLastTrade >= subTrade1GainLimit2.FloatValue:
                        reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_2)
                if self.FirstInnerTradeProfitLastTrade is not None and self.FirstInnerTradeProfitLastTrade < subTrade2LossLimit2.FloatValue:
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_1)
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_2)
            elif (openSummary1.IsSecondInnerTradeOpen()):
                if self.SecondInnerTradeProfitLastTrade is not None and self.SecondInnerTradeProfitLastTrade >= subTrade3GainLimit3.FloatValue:
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_1)
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_2)
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_3)
                if self.SecondInnerTradeProfitLastTrade is not None and self.SecondInnerTradeProfitLastTrade < subTrade3LossLimit3.FloatValue:
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_1)
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_2)
                    reducingConds.append(_LONG_MACD_RSI_RULE_11_RED_3)

    def EvaluateClosingMACDRSILongTrade(self,candlebarsArr,msNowParamA,macdMaxGainParamJ,macdMaxGainParamJJ,gainMaxTradeParamJJJ,
                                            gainMaxTradeParamSDMult,gainMaxTradeParamFixedGain,macdGainNowMaxParamK,
                                            rsi30SlopeSkip5ExitParamL,rsi30Skip5ParamLX,msNowExitParamN,msNowExitParamNN,msMaxMinExitParamNBis,
                                            msMaxMinExitParamNNBis,msNowMaxMinExitParamP,msNowExitParamQ,msNowExitParamQQ,
                                            rsi30SlopeSkip10ExitParamR,msMaxMinExitParamS,msMaxMinExitParamSS,
                                            sec5MinSlopeExitParamT,gainMinStopLossExitParamU,gainMinStopLossExitParamUU,
                                            gainMinTradeParamUUU, gainMinTradeParamFixedLoss,gainMinTradeParamFixedLoss2,
                                            changeFixedLossAtThisGainParam,
                                            gainMinStopLossExitParamW,gainMinStopLossExitParamWW,gainStopLossExitParamY,
                                            gainMinStopLossExitParamZ,gainMinStopLossExitParamZZ,endOfdayLimitModelParam,
                                            takeGainLimitModelParam,stopLossLimitModelParam,
                                            implFlexibeStopLoss, flexibleStopLossL1ModelParam,
                                            macdRSISmoothedMode,absMaxMSPeriodParam,
                                            macdRsiCloseLongRule1ModelParam,macdRsiCloseLongRule2ModelParam,macdRsiCloseLongRule3ModelParam,
                                            macdRsiCloseLongRule4ModelParam,macdRsiCloseLongRule5ModelParam,macdRsiCloseLongRule6ModelParam,
                                            macdRsiCloseLongRule7ModelParam,macdRsiCloseLongRule8ModelParam,macdRsiCloseLongRule9ModelParam,
                                            slFlipModelParam):


        openQty = 1
        if not self.Open():
            return None  # Position not opened

        if self.GetNetOpenShares() < 0:
            return None  # We are in a SHORT position
        else:
            openQty=abs(self.GetNetOpenShares()) if self.GetNetOpenShares()!=0 else 1

        '''
        # Rule TERMINAL --> Positions are not closed. They won't just be opened again
        terminalCond = self.EvaluateSoftTerminalCondition(candlebarsArr,takeGainLimitModelParam,stopLossLimitModelParam,
                                                             implFlexibeStopLoss, flexibleStopLossL1ModelParam)

        if terminalCond is not None:
            self.TerminalClose=True
            self.TerminalCloseCond = terminalCond #This won't be closed. It won't just open another position again
            #return terminalCond
        '''

        # Rule STRONG TERMINAL --> Positions are closed and They won't just be opened again
        eodCond = self.EvaluateStrongTerminal(candlebarsArr, endOfdayLimitModelParam)

        if eodCond is not None:
            self.TerminalClose = True
            self.TerminalCloseCond = eodCond  # This WILL be closed
            return eodCond

        if (
                self.CurrentProfitLastTrade is None or self.MaxProfitCurrentTrade is None or self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) is None
                or self.MACDIndicator.MSPrev is None or self.MACDIndicator.MS is None or self.MACDIndicator.MaxMS is None
                or self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) is None or self.MaxMonetaryLossCurrentTrade is None
                or self.MaxMonetaryProfitCurrentTrade is None or self.CurrentProfitMonetaryLastTrade is None
                or len(candlebarsArr)<5 or self.MACDIndicator.PriceHMinusL is None
                #or self.MACDIndicato.GetMaxABSMaxMinMS(5) is None
           ):
            return None

        # =================== NOW WE START WITH THE ALGO NON TERMINAL RULES =============================

        # LONG ON --> NO TRADE ON
        # rule 1
        if (
                    (self.MaxMonetaryProfitCurrentTrade/openQty) >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,macdMaxGainParamJ,macdMaxGainParamJJ)
                and (self.MaxMonetaryProfitCurrentTrade> 0 and self.TGIndicator.HasValidValue()  and ((self.CurrentProfitMonetaryLastTrade/self.MaxMonetaryProfitCurrentTrade)<self.TGIndicator.K))
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) < (-1*rsi30Skip5ParamLX.FloatValue)
                and (self.MaxMonetaryProfitCurrentTrade / openQty) >= (self.BollingerIndicator.TPSDStartOfTrade * gainMaxTradeParamJJJ.FloatValue)
                and (self.MaxMonetaryProfitCurrentTrade / openQty) >= gainMaxTradeParamSDMult.FloatValue * self.PriceVolatilityIndicators.LastSDDDaysOpenStdDev
                and (self.MaxProfitCurrentTrade >= gainMaxTradeParamSDMult.FloatValue * self.PriceVolatilityIndicators.LastSDDDaysOpenStdDev)
                and (self.MaxProfitCurrentTrade>=gainMaxTradeParamFixedGain.FloatValue)
                and macdRsiCloseLongRule1ModelParam.IntValue>=1
           ):
            return _EXIT_LONG_MACD_RSI_COND_1

        # rule 2
        if (        self.MACDIndicator.MSPrev < msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MACDIndicator.MS < (-1 * self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowExitParamN,msNowExitParamNN))
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) < (-1*rsi30SlopeSkip5ExitParamL.FloatValue)
                and self.VolumeAvgIndicator.ValidateIfEnoughData()
                and macdRsiCloseLongRule2ModelParam.IntValue>=1

        ):
            return _EXIT_LONG_MACD_RSI_COND_2

        # rule 3
        if (self.MACDIndicator.MSPrev < msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and (self.MaxMonetaryLossCurrentTrade/openQty) < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamW,gainMinStopLossExitParamWW)
                and self.VolumeAvgIndicator.ValidateIfEnoughData()
                and macdRsiCloseLongRule3ModelParam.IntValue>=1

        ):
            return _EXIT_LONG_MACD_RSI_COND_3

        # rule 4
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MACDIndicator.MS < (-1 * self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowExitParamN,msNowExitParamNN))
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) < (-1 * rsi30SlopeSkip5ExitParamL.FloatValue)
                and self.VolumeAvgIndicator.ValidateIfEnoughData()
                and macdRsiCloseLongRule4ModelParam.IntValue>=1

        ):
            return _EXIT_LONG_MACD_RSI_COND_4

        # rule 5
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and (self.MaxMonetaryLossCurrentTrade/openQty) < gainMinStopLossExitParamW.FloatValue
                and macdRsiCloseLongRule5ModelParam.IntValue>=1

        ):
            return _EXIT_LONG_MACD_RSI_COND_5

        # rule 6
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS >= msNowParamA.FloatValue
                and self.MACDIndicator.MaxMS >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinExitParamNBis,msMaxMinExitParamNNBis)
                and (self.MACDIndicator.MaxMS > 0 and ((self.MACDIndicator.MS / self.MACDIndicator.MaxMS) < msNowMaxMinExitParamP.FloatValue))
                and self.MACDIndicator.MS < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowExitParamQ,msNowExitParamQQ)
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) < (-1 * rsi30SlopeSkip5ExitParamL.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) < rsi30SlopeSkip10ExitParamR.FloatValue
                and self.VolumeAvgIndicator.ValidateIfEnoughData()
                and macdRsiCloseLongRule6ModelParam.IntValue >=1
            ):
                return _EXIT_LONG_MACD_RSI_COND_6

        # rule 7
        if (        self.MACDIndicator.GetMaxAbsMSCrossover(absMaxMSPeriodParam.IntValue) < self.SmoothMACDRSIParam(macdRSISmoothedMode, self.MACDIndicator.AbsMaxMS, msMaxMinExitParamS, msMaxMinExitParamSS)
                and self.GetReggrSlope(candlebarsArr,5) < ( -1 * sec5MinSlopeExitParamT.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(5) < (-1 * rsi30SlopeSkip5ExitParamL.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSIReggr(10) < rsi30SlopeSkip10ExitParamR.FloatValue
                and self.VolumeAvgIndicator.ValidateIfEnoughData()
                and macdRsiCloseLongRule7ModelParam.IntValue>=1
            ):
            return _EXIT_LONG_MACD_RSI_COND_7


        # rule 8
        if (        self.MACDIndicator.GetMaxAbsMSCrossover(absMaxMSPeriodParam.IntValue) < self.SmoothMACDRSIParam(macdRSISmoothedMode, self.MACDIndicator.AbsMaxMS, msMaxMinExitParamS, msMaxMinExitParamSS)
                and (self.MaxMonetaryLossCurrentTrade/openQty) < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamZ,gainMinStopLossExitParamZZ))
                and self.VolumeAvgIndicator.ValidateIfEnoughData()
                and macdRsiCloseLongRule8ModelParam.IntValue >=1
            ):
            return _EXIT_LONG_MACD_RSI_COND_8

        # rule 9
        if (        (self.MaxMonetaryLossCurrentTrade/openQty) < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamU,gainMinStopLossExitParamUU))
                    and (self.BollingerIndicator.TPSDStartOfTrade is None or ( (self.MaxMonetaryLossCurrentTrade / openQty) < ( -1 * self.BollingerIndicator.TPSDStartOfTrade * gainMinTradeParamUUU.FloatValue)))
                    #and (self.MaxMonetaryLossCurrentTrade / openQty) < gainMinTradeParamFixedLoss.FloatValue
                    and (self.MaxLossCurrentTrade <gainMinTradeParamFixedLoss.FloatValue)
                and macdRsiCloseLongRule9ModelParam.IntValue>=1
            ):
            return  _EXIT_LONG_MACD_RSI_COND_9


        #rule #10
        ruleTenExitCond=self.RunRuleTenLongPos(slFlipModelParam,changeFixedLossAtThisGainParam,gainMinTradeParamFixedLoss,gainMinTradeParamFixedLoss2)
        if(ruleTenExitCond is not None):
            return ruleTenExitCond

        return None #No condition to exit

    def EvaluateClosingMACDRSILongTradeByTick(self,slFlipModelParam,changeFixedLossAtThisGainParam,gainMinTradeParamFixedLoss,gainMinTradeParamFixedLoss2):

        if not self.Open():
            return None

        # rule #10
        ruleTenExitCond = self.RunRuleTenLongPos(slFlipModelParam, changeFixedLossAtThisGainParam,gainMinTradeParamFixedLoss, gainMinTradeParamFixedLoss2)
        if (ruleTenExitCond is not None):
            return ruleTenExitCond

        return None

    def EvaluateClosingMACDRSIShortTradeByTick(self, slFlipModelParam, changeFixedLossAtThisGainParam,gainMinTradeParamFixedLoss, gainMinTradeParamFixedLoss2):

        if not self.Open():
            return None

        # rule #10
        ruleTenExitCond = self.RunRuleTenShortPos(slFlipModelParam, changeFixedLossAtThisGainParam,gainMinTradeParamFixedLoss, gainMinTradeParamFixedLoss2)
        if (ruleTenExitCond is not None):
            return ruleTenExitCond

        return None


    def EvaluateClosingGenericLongTrade(self,candlebarsArr,
                                  maxGainForClosingModelParam,pctMaxGainForClosingModelParam,
                                  maxLossForClosingModelParam,pctMaxLossForClosingModelParam,
                                  takeGainLimitModelParam,stopLossLimitModelParam,
                                  implFlexibeStopLoss, flexibleStopLossL1ModelParam,
                                  pctSlopeToCloseLongModelParam,
                                  endOfdayLimitModelParam,
                                  nonSmoothed14MinRSIShortThreshold):



        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        if not self.Open():
            return None  # Position not opened

        if self.GetNetOpenShares() < 0:
            return None  # We are in a short position

        '''
        # Rule TERMINAL --> Positions are not closed. They won't just be opened again
        terminalCond = self.EvaluateSoftTerminalCondition(candlebarsArr, takeGainLimitModelParam,stopLossLimitModelParam,
                                                             implFlexibeStopLoss, flexibleStopLossL1ModelParam)

        if terminalCond is not None:
            self.TerminalClose = True
            self.TerminalCloseCond = terminalCond  # This won't be closed. It won't just open another position again
            # return terminalCond
        '''

        # Rule STRONG TERMINAL --> Positions are closed and They won't just be opened again
        eodCond = self.EvaluateStrongTerminal(candlebarsArr, endOfdayLimitModelParam)

        if eodCond is not None:
            self.TerminalClose = True
            self.TerminalCloseCond = eodCond  # This WILL be closed
            return eodCond

        # Maximum Gain during the trade exceeds a certain value and then drops to a percentage of that value
        #rule 3
        if (    self.MaxProfitCurrentTrade is not None
            and self.CurrentProfitLastTrade is not None
            and (maxGainForClosingModelParam.FloatValue is not None and self.MaxProfitCurrentTrade >= maxGainForClosingModelParam.FloatValue * 100)
            and (pctMaxGainForClosingModelParam.FloatValue is not None and (self.CurrentProfitLastTrade < pctMaxGainForClosingModelParam.FloatValue * self.MaxProfitCurrentTrade))
        ):
            return _EXIT_LONG_COND_3

        # Maximum Loss during the trade exceeds (worse than) a certain value and then drops to a percentage of that value
        #rule 4
        if (    self.CurrentProfitLastTrade is not None
            and self.MaxLossCurrentTrade is not None
            and (maxLossForClosingModelParam.FloatValue is not None and self.MaxLossCurrentTrade <= (maxLossForClosingModelParam.FloatValue * 100))
            and self.CurrentProfit < 0
        ):
            absProfit = self.CurrentProfitLastTrade if self.CurrentProfitLastTrade > 0 else (-1 * self.CurrentProfit)
            absMaxLoss = self.MaxLossCurrentTrade if self.MaxLossCurrentTrade > 0 else (-1 * self.MaxLossCurrentTrade)
            if (absProfit < (pctMaxLossForClosingModelParam.FloatValue * absMaxLoss)):
                return _EXIT_LONG_COND_4

        #Last 3 minute slope of 3 minute moving average exceeds a certain value AGAINST the Trade
        #rule 5
        if(     statisticalParams.ThreeMinSkipSlope is not None
            and (pctSlopeToCloseLongModelParam.FloatValue is not None and statisticalParams.ThreeMinSkipSlope < pctSlopeToCloseLongModelParam.FloatValue)
          ):
            return _EXIT_LONG_COND_5


        return None


    #endregion

    #region Manual Trading Rules

    def EvaluateClosingOnEndOfDay(self, candlebar, endOfdayLimitModelParam):
        if not self.Open():
            return False  # Position not opened

        openSummary = self.GetLastTradedSummary(Side.Buy if self.GetNetOpenShares() > 0 else Side.Sell)

        if (openSummary is not None
                and openSummary.Position.CloseEndOfDay is not None
                and openSummary.Position.CloseEndOfDay == True
                and self.EvaluateBiggerDate(candlebar, endOfdayLimitModelParam)
                and self.GetNetOpenShares() != 0):
            return True
        else:
            return False

    def EvaluateClosingOnStopLoss(self, candlebar):

        if not self.Open():
            return False  # Position not opened

        if self.GetNetOpenShares() < 0:  # Stop loss on short position
            openSummary = self.GetLastTradedSummary(Side.Sell)

            if (openSummary is not None
                    and openSummary.AvgPx is not None
                    and openSummary.Position.StopLoss is not None
                    and candlebar.Close is not None
                    and candlebar.Close > (openSummary.AvgPx + openSummary.Position.StopLoss)  # Short --> bigger than
            ):
                return True
            else:
                return False

        elif self.GetNetOpenShares() > 0:  # Stop loss on long position
            openSummary = self.GetLastTradedSummary(Side.Buy)

            if (openSummary is not None
                    and openSummary.Position.StopLoss is not None
                    and openSummary.AvgPx is not None
                    and candlebar.Close is not None
                    and candlebar.Close < (openSummary.AvgPx - openSummary.Position.StopLoss)  # Long --> lower than
            ):
                return True
            else:
                return False
        else:
            return False

    def EvaluateClosingOnTakeProfit(self, candlebar):

        if not self.Open():
            return False  # Position not opened

        if self.GetNetOpenShares() < 0:  # take profit on short position
            openSummary = self.GetLastTradedSummary(Side.Sell)

            if (openSummary is not None
                    and openSummary.Position.TakeProfit is not None
                    and openSummary.AvgPx is not None
                    and candlebar.Close is not None
                    and candlebar.Close < (openSummary.AvgPx - openSummary.Position.TakeProfit)
            ):  # Short position --> lower than AvgPx - take profit
                return True
            else:
                return False
        elif self.GetNetOpenShares() > 0:  # Stop loss on long position

            openSummary = self.GetLastTradedSummary(Side.Buy)

            if (
                    openSummary is not None
                    and openSummary.AvgPx is not None
                    and candlebar.Close is not None
                    and openSummary.Position.TakeProfit is not None
                    and candlebar.Close > (openSummary.AvgPx + openSummary.Position.TakeProfit)
            ):
                return True
            else:
                return False
        else:
            return False

    #endregion

    #region Strong and simple Terminal

    def CanOpenPosition(self,candlebarArr,TAKE_GAIN_LIMIT,STOP_LOSS_LIMIT,IMPL_FLEXIBLE_STOP_LOSSES,FLEXIBLE_STOP_LOSS_L1,END_OF_DAY_LIMIT,
                            LONG_SHORT_ON_CANDLE,longTrade):

        self.SoftTerminalCondEvaluated = self.EvaluateSoftTerminalCondition (candlebarArr,TAKE_GAIN_LIMIT,STOP_LOSS_LIMIT,
                                                                             IMPL_FLEXIBLE_STOP_LOSSES,FLEXIBLE_STOP_LOSS_L1 )
        self.StrongTerminalCondEvaluated = self.EvaluateStrongTerminal(candlebarArr,END_OF_DAY_LIMIT)

        momentumCond= self.EvaluateMomentumConditions(candlebarArr,LONG_SHORT_ON_CANDLE,longTrade)

        return (not self.TerminalClose  and  self.SoftTerminalCondEvaluated is  None and self.StrongTerminalCondEvaluated is None
                and momentumCond is not None)

    def TerminalConditionActivated(self):

        if not self.TerminalClose:
            if self.SoftTerminalCondEvaluated is not None:
                return self.SoftTerminalCondEvaluated
            elif self.StrongTerminalCondEvaluated is not None:
                return self.StrongTerminalCondEvaluated
            else:
                return None
                #raise Exception("Inconsistent state where the is no a terminal close and no soft terminal and strong terminals activated")
        else:
            return self.StrongTerminalCondEvaluated if self.StrongTerminalCondEvaluated is not None else self._TERMINALLY_CLOSED()

    def IsTerminalCondition(self,condition):
        return (condition==_EXIT_TERM_COND_EOF or condition==_EXIT_TERM_COND_1 or condition==_EXIT_TERM_COND_2
                or condition == _TERMINALLY_CLOSED or condition==_EXIT_TERM_COND_FLEX_STOP_LOSS)

        # Defines if the condition for closing the day, will imply not opening another position during the day

    def EvaluateMomentumConditions(self,candlebarsArr,longShortOnCandleParam,longTrade):
        lastCandlebar = candlebarsArr[-1]

        if(longShortOnCandleParam.IntValue is not None and longShortOnCandleParam.IntValue>0 and self.OpenMarketData is not None
            and self.OpenMarketData.OpeningPrice is not None):

            if longTrade:
                if lastCandlebar.Close> self.OpenMarketData.OpeningPrice:
                    return _LONG_SHORT_ON_CANDLE_LONG_MARKET
                else:
                    return None
            else:
                if lastCandlebar.Close< self.OpenMarketData.OpeningPrice:
                    return _LONG_SHORT_ON_CANDLE_SHORT_MARKET
                else:
                    return None
        else:
            return _LONG_SHORT_ON_CANDLE_OFF

    def EvaluateStrongTerminal(self, candlebarsArr, endOfdayLimitModelParam):

            lastCandlebar = candlebarsArr[-1]

            # EXIT any open trades at 2:59 PM central time
            if (endOfdayLimitModelParam.StringValue is not None and self.EvaluateBiggerDate(lastCandlebar,
                                                                                            endOfdayLimitModelParam)):
                return _EXIT_TERM_COND_EOF

            return None

    #Defines if the condition for closing the day, will imply not opening another position during the day
    def EvaluateSoftTerminalCondition(self,candlebarsArr,takeGainLimitModelParam,stopLossLimitModelParam,
                                         implFlexibeStopLoss, flexibleStopLossL1ModelParam):

        lastCandlebar = candlebarsArr[-1]

        #print("{} - CurrentProfit = {} StopLoss={}".format(lastCandlebar.DateTime,self.CurrentProfit,stopLossLimitModelParam.FloatValue))

        # CUMULATIVE Gain for the Day exceeds Take Gain Limit
        if (takeGainLimitModelParam.FloatValue is not None and (self.CurrentProfitToSecurity is not None and self.CurrentProfitToSecurity > takeGainLimitModelParam.FloatValue * 100)):
        #if ( takeGainLimitModelParam.FloatValue is not None and (self.CurrentProfit is not None and self.CurrentProfit > takeGainLimitModelParam.FloatValue*100)):
            return _EXIT_TERM_COND_1

        # CUMULATIVE Loss for the Day exceeds (worse than) Stop Loss Limit
        if (stopLossLimitModelParam.FloatValue is not None and (self.CurrentProfitToSecurity is not None and self.CurrentProfitToSecurity < stopLossLimitModelParam.FloatValue * 100)):
            #if (stopLossLimitModelParam.FloatValue is not None and (self.CurrentProfit is not None and self.CurrentProfit < stopLossLimitModelParam.FloatValue*100)):
            return _EXIT_TERM_COND_2

        # L1- Flexible Stop Loss

        if (    implFlexibeStopLoss.IntValue >=1 and self.PriceVolatilityIndicators.FlexibleStopLoss is not None
            and self.PriceVolatilityIndicators.FlexibleStopLoss!=0):
            openQty = abs(self.GetNetOpenShares()) if self.GetNetOpenShares() != 0 else 1
            if (self.CurrentProfitMonetary/openQty) < self.PriceVolatilityIndicators.FlexibleStopLoss:
                return _EXIT_TERM_COND_FLEX_STOP_LOSS

        return None

    #endregion

    #endregion