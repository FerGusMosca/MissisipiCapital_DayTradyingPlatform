from sources.framework.business_entities.securities.security import *
from sources.framework.business_entities.market_data.candle_bar import *
from sources.framework.common.enums.Side import *
from sources.framework.common.enums.PositionsStatus import PositionStatus
from sources.strategy.common.dto.position_statistical_parameters import *
from sources.strategy.common.dto.position_profits_and_losses import *
from sources.strategy.strategies.day_trader.business_entities.rsi_indicator import *
from sources.strategy.strategies.day_trader.business_entities.macd_indicator import *
from sources.strategy.strategies.day_trader.business_entities.macd_indicator_adjusted import *

import json
import statistics
import time
from datetime import datetime, timedelta
from json import JSONEncoder

_EXIT_TERM_COND_1="EXIT_TERM_COND_1"
_EXIT_TERM_COND_2="EXIT_TERM_COND_2"
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

_EXIT_LONG_MACD_RSI_COND_1="EXIT_LONG_MACD_RSI_COND_1"
_EXIT_LONG_MACD_RSI_COND_2="EXIT_LONG_MACD_RSI_COND_2"
_EXIT_LONG_MACD_RSI_COND_3="EXIT_LONG_MACD_RSI_COND_3"
_EXIT_LONG_MACD_RSI_COND_4="EXIT_LONG_MACD_RSI_COND_4"
_EXIT_LONG_MACD_RSI_COND_5="EXIT_LONG_MACD_RSI_COND_5"
_EXIT_LONG_MACD_RSI_COND_6="EXIT_LONG_MACD_RSI_COND_6"
_EXIT_LONG_MACD_RSI_COND_7="EXIT_LONG_MACD_RSI_COND_7"
_EXIT_LONG_MACD_RSI_COND_8="EXIT_LONG_MACD_RSI_COND_8"
_EXIT_LONG_MACD_RSI_COND_9="EXIT_LONG_MACD_RSI_COND_9"

_EXIT_SHORT_MACD_RSI_COND_1 = "EXIT_SHORT_MACD_RSI_COND_1"
_EXIT_SHORT_MACD_RSI_COND_2 = "EXIT_SHORT_MACD_RSI_COND_2"
_EXIT_SHORT_MACD_RSI_COND_3 = "EXIT_SHORT_MACD_RSI_COND_3"
_EXIT_SHORT_MACD_RSI_COND_4 = "EXIT_SHORT_MACD_RSI_COND_4"
_EXIT_SHORT_MACD_RSI_COND_5 = "EXIT_SHORT_MACD_RSI_COND_5"
_EXIT_SHORT_MACD_RSI_COND_6 = "EXIT_SHORT_MACD_RSI_COND_6"
_EXIT_SHORT_MACD_RSI_COND_7 = "EXIT_SHORT_MACD_RSI_COND_7"
_EXIT_SHORT_MACD_RSI_COND_8 = "EXIT_SHORT_MACD_RSI_COND_8"
_EXIT_SHORT_MACD_RSI_COND_9 = "EXIT_SHORT_MACD_RSI_COND_9"

_LONG_MACD_RSI_RULE_1="LONG_MACD_RSI_RULE_1"
_LONG_MACD_RSI_RULE_2="LONG_MACD_RSI_RULE_2"
_LONG_MACD_RSI_RULE_3="LONG_MACD_RSI_RULE_3"
_LONG_MACD_RSI_RULE_4="LONG_MACD_RSI_RULE_4"
_LONG_MACD_RSI_RULE_5="LONG_MACD_RSI_RULE_5"

_SHORT_MACD_RSI_RULE_1="SHORT_MACD_RSI_RULE_1"
_SHORT_MACD_RSI_RULE_2="SHORT_MACD_RSI_RULE_2"
_SHORT_MACD_RSI_RULE_3="SHORT_MACD_RSI_RULE_3"
_SHORT_MACD_RSI_RULE_4="SHORT_MACD_RSI_RULE_4"
_SHORT_MACD_RSI_RULE_5="SHORT_MACD_RSI_RULE_5"

_TERMINALLY_CLOSED ="TERMINALLY_CLOSED"

_REC_UNDEFINED = -1
_REC_GO_LONG_NOW = 0
_REC_GO_SHORT_NOW = 1
_REC_STAY_LONG = 2
_REC_STAY_SHORT = 3
_REC_EXIT_LONG_NOW = 4
_REC_EXIT_SHORT_NOW = 5
_REC_STAY_OUT= 5

class DayTradingPosition():

    def __init__(self,id ,security,shares,active,routing,open,longSignal,shortSignal,signalType=None,signalDesc=None):
        self.Id=id
        self.Security = security
        self.SharesQuantity= shares
        self.Active=active
        self.MarketData=None
        self.ExecutionSummaries={}
        self.Routing =routing
        #self.Open=open
        self.LongSignal = longSignal
        self.ShortSignal = shortSignal
        self.SignalType=signalType
        self.SignalDesc = signalDesc

        self.CurrentProfit = 0
        self.CurrentProfitLastTrade = 0
        self.CurrentProfitMonetary = 0
        self.CurrentProfitMonetaryLastTrade = 0
        self.IncreaseDecrease = 0

        self.MaxProfit = 0
        self.MaxLoss=0
        self.MaxProfitCurrentTrade = 0
        self.MaxLossCurrentTrade = 0
        self.LastNDaysStdDev = 0
        self.LastProfitCalculationDay = None
        self.TerminalClose = False
        self.TerminalCloseCond = None
        self.Recomendation = _REC_UNDEFINED
        self.ShowTradingRecommndations = False

        self.MinuteNonSmoothedRSIIndicator = RSIIndicator(False)
        self.MinuteSmoothedRSIIndicator = RSIIndicator(True)
        self.DailyRSIIndicator = RSIIndicator(False)
        #self.MACDIndicator = MACDIndicator()
        self.MACDIndicator = MACDIndicatorAdjusted()


    #region Static Methods

    @staticmethod
    def _TERMINALLY_CLOSED():
        return _TERMINALLY_CLOSED

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

    def Open(self):
        return self.GetNetOpenShares()!=0


    def GetSlope (self,currMovAvg,prevMovAvg):

        if currMovAvg is not None and prevMovAvg is not None and prevMovAvg!=0:
            return (currMovAvg-prevMovAvg)/prevMovAvg
        else:
            return None

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

    def GetNetOpenShares(self):
        todaySummaries = sorted(list(filter(lambda x: x.Timestamp.date() == datetime.now().date() and x.CumQty >= 0,
                                            self.ExecutionSummaries.values())),
                                key=lambda x: x.Timestamp, reverse=False)
        netShares = 0
        for summary in todaySummaries:
            # first we calculate the traded positions
            if summary.GetTradedSummary() > 0:
                if summary.SharesAcquired():
                    netShares += summary.GetNetShares()
                else:
                    netShares -= summary.GetNetShares()

        return netShares

    def CalculateLastTradeProfit(self, profitsAndLosses, marketData):

        lastTradedSummaries = sorted(list(filter(lambda x: x.Timestamp.date() == datetime.now().date() and x.GetNetShares() != 0
                                                 and (x.Position.LongPositionOpened() if self.GetNetOpenShares()>0 else x.Position.ShortPositionOpened()),
                           self.ExecutionSummaries.values())),key=lambda x: x.Timestamp, reverse=True)

        lastTradedSummary=None
        if(len(lastTradedSummaries)>0):
            lastTradedSummary=lastTradedSummaries[0]

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


    def CalculatePositionsProfit(self,profitsAndLosses):
        todaySummaries = sorted(list(filter(lambda x: x.Timestamp.date() == datetime.now().date() and x.CumQty >= 0, self.ExecutionSummaries.values())),
                                            key=lambda x: x.Timestamp, reverse=False)
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

    #region Public Methods
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def DepurateSummaries(self):
        openSummaries = list(filter(lambda x: x.Position.IsOpenPosition(), self.ExecutionSummaries.values()))

        for openSummary in openSummaries:
            openSummary.PosStatus = PositionStatus.Unknown
            openSummary.Position.PosStatus = PositionStatus.Unknown

        self.UpdateRouting()

        return openSummaries

    def UpdateRouting(self):
        nextOpenPos = next(iter(list(filter(lambda x: x.Position.IsOpenPosition(), self.ExecutionSummaries.values()))), None)

        self.Routing= nextOpenPos is not None

    def GetOpenSummaries(self):
        return list(filter(lambda x: x.Position.IsOpenPosition(), self.ExecutionSummaries.values()))


    def GetLastTradedSummary(self,side):

        #All the traded summaries for a side, order in a descending fashion
        lastTradedSummaries = sorted(list(filter(lambda x: x.GetNetShares() != 0
                                                 and x.Position.LongPositionOpened() if side==Side.Buy else x.Position.ShortPositionOpened(),
                                                 self.ExecutionSummaries.values())), key=lambda x: x.Timestamp, reverse=True)

        return lastTradedSummaries[0] if (len(lastTradedSummaries) > 0) else None


    def ResetProfitCounters(self,now):
        self.CurrentProfit = 0
        self.CurrentProfitLastTrade= 0
        self.CurrentProfitMonetary = 0
        self.CurrentProfitMonetaryLastTrade= 0

        self.MaxLoss = 0
        self.MaxProfit = 0
        self.MaxProfitCurrentTrade = 0
        self.MaxLossCurrentTrade = 0
        self.LastProfitCalculationDay = datetime.now()

        self.MinuteNonSmoothedRSIIndicator.Reset()#14
        self.MinuteSmoothedRSIIndicator.Reset()#30
        self.MACDIndicator.Reset()
        self.TerminalClose = False
        self.TerminalCloseCond = None
        self.Recomendation=_REC_UNDEFINED
        self.ShowTradingRecommndations=False

    def CalculateCurrentDayProfits(self,marketData):

        profitsAndLosses = PositionsProfitsAndLosses()

        foundOpenPositions = self.CalculatePositionsProfit(profitsAndLosses)

        profitsAndLosses.PosMTM = self.CalculateMarkToMarket(marketData, profitsAndLosses, foundOpenPositions)

        profitsAndLosses.Profits = self.CalculatePercentageProfits(profitsAndLosses)
        profitsAndLosses.MonetaryProfits = self.CalculateMonetaryProfits(profitsAndLosses)

        if self.Open():

            self.CalculateLastTradeProfit(profitsAndLosses,marketData)

            if(profitsAndLosses.Profits>self.MaxProfit):
                self.MaxProfit=profitsAndLosses.Profits

            if(profitsAndLosses.Profits<self.MaxLoss):
                self.MaxLoss=profitsAndLosses.Profits

            if (profitsAndLosses.ProfitLastTrade > self.MaxProfitCurrentTrade):
                self.MaxProfitCurrentTrade = profitsAndLosses.ProfitLastTrade

            if (profitsAndLosses.ProfitLastTrade < self.MaxLossCurrentTrade):
                self.MaxLossCurrentTrade = profitsAndLosses.ProfitLastTrade

            self.CurrentProfit=profitsAndLosses.Profits
            self.CurrentProfitMonetary = profitsAndLosses.MonetaryProfits
            self.CurrentProfitLastTrade = profitsAndLosses.ProfitLastTrade
            self.CurrentProfitMonetaryLastTrade = profitsAndLosses.MonetaryProfitLastTrade
            self.LastProfitCalculationDay=datetime.now()
            self.IncreaseDecrease=profitsAndLosses.IncreaseDecrease
        else:
            #Last Trade remains as the last estimation while was opened
            self.CurrentProfit = profitsAndLosses.Profits
            self.CurrentProfitMonetary = profitsAndLosses.MonetaryProfits
            self.LastProfitCalculationDay = datetime.now()
            self.IncreaseDecrease = 0
            self.MaxLossCurrentTrade=0
            self.MaxProfitCurrentTrade=0


    def EvaluateGenericShortTrade(self,dailyBiasModelParam,dailySlopeModelParam, posMaximShortChangeParam,
                           posMaxShortDeltaParam,nonSmoothed14MinRSIShortThreshold,candlebarsArr):

        if self.Open():
            #print ("Not opening because is opened:{}".format(self.Security.Symbol))
            return False #Position already opened

        if self.Routing:
            #print("Not opening because is routing:{}".format(self.Security.Symbol))
            return False #cannot open positions that are being routed

        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        #if statisticalParams.TenMinSkipSlope is not None:
            #print("Open Short - Ten Min Skip Slope {} for security {}".format(statisticalParams.TenMinSkipSlope,self.Security.Symbol))

        if  (statisticalParams.TenMinSkipSlope is None or statisticalParams.ThreeMinSkipSlope is None
            or statisticalParams.ThreeToSixMinSkipSlope is None or statisticalParams.SixToNineMinSkipSlope is None
            or statisticalParams.PctChangeLastThreeMinSlope is None or statisticalParams.DeltaCurrValueAndFiftyMMov is None):
            return False

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
                #RSI 14 Minutes (NOT smoothed) --> IF crossing from above 70 to below 70
            #and
            #   (nonSmoothed14MinRSIShortThreshold.FloatValue is None or self.MinuteNonSmoothedRSIIndicator.BearishSignal(nonSmoothed14MinRSIShortThreshold.FloatValue))

        ):
            return True
        else:
            return False

    def SmoothMACDRSIParam(self,macdRSISmoothedMode,paramToComp,modelParamToSmooth,modelParamToSmoothIndex):
        if macdRSISmoothedMode.IntValue==0:
            return modelParamToSmooth.FloatValue
        else:
            return paramToComp / modelParamToSmoothIndex.FloatValue if self.MACDIndicator.paramToComp  is not None else 0

    def EvaluateMACDRSIShortTrade(self,msNowParamA,msMinParamB,msMinParamBB,rsi30SlopeSkip5ParamC,msMaxMinParamD,msMaxMinParamDD,
                                  msNowMaxParamE,msNowParamF,msNowParamFF,rsi30SlopeSkip10ParamG,absMSMaxMinLast5ParamH,
                                  absMSMaxMinLast5ParamHH,sec5MinSlopeParamI,rsi14SlopeSkip3ExitParamV,ms3SlopeParamX,
                                  ms3SlopeParamXX,macdRSISmoothedMode,candlebarsArr):

        if self.Open():
            return None #Position already opened

        if self.Routing:
            return None #cannot open positions that are being routed

        if (self.MACDIndicator.MSPrev is None or self.MACDIndicator.MS is None or self.MACDIndicator.MaxMS is None \
                or self.MACDIndicator.MinMS is None or self.MinuteSmoothedRSIIndicator.GetRSISlope(5) is None
                or self.MinuteSmoothedRSIIndicator.GetRSISlope(10) is None or len(candlebarsArr)<5
                or self.MinuteNonSmoothedRSIIndicator.GetRSISlope(3) is None or self.MACDIndicator.GetMSSlope(3) is None
            ):
            return None

        # NO TRADE ON --> SHORT ON
        # line 1
        if (        self.MACDIndicator.MSPrev < msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MACDIndicator.MinMS < (-1 * self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMinParamB,msMinParamBB))
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) < (-1* rsi30SlopeSkip5ParamC.FloatValue)):
            return _SHORT_MACD_RSI_RULE_1

        # line 2
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MACDIndicator.MinMS < (-1* msMinParamB.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) < (-1* rsi30SlopeSkip5ParamC.FloatValue)
            ):
            return _SHORT_MACD_RSI_RULE_2

        # line 3
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS >= msNowParamA.FloatValue
                and self.MACDIndicator.MaxMS >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinParamD,msMaxMinParamDD)
                and (self.MACDIndicator.MaxMS > 0 and (self.MACDIndicator.MS % self.MACDIndicator.MaxMS) < msNowMaxParamE.FloatValue)
                and self.MACDIndicator.MS < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowParamF,msNowParamFF)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) < (-1 * rsi30SlopeSkip5ParamC.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(10) < rsi30SlopeSkip10ParamG.FloatValue
                and self.MinuteNonSmoothedRSIIndicator.GetRSISlope(3) < rsi14SlopeSkip3ExitParamV.FloatValue
                and self.MACDIndicator.GetMSSlope(3) < (-1* self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,self.MACDIndicator.AbsMaxMS,ms3SlopeParamX,ms3SlopeParamXX) )
          ):
            return _SHORT_MACD_RSI_RULE_3

        # line 4
        if (    self.MACDIndicator.GetMaxAbsMS(15) < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,absMSMaxMinLast5ParamH,absMSMaxMinLast5ParamHH)
                and self.GetSlope(candlebarsArr[-1].Close,candlebarsArr[-5].Close) < (-1 * sec5MinSlopeParamI.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) < (-1 *  rsi30SlopeSkip5ParamC.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(10) < rsi30SlopeSkip10ParamG.FloatValue
            ):
            return _SHORT_MACD_RSI_RULE_4


        return None

    def EvaluateMACDRSILongTrade(self,msNowParamA,msMinParamB,msMinParamBB,rsi30SlopeSkip5ParamC,msMaxMinParamD,msMaxMinParamDD,
                                 msNowMaxParamE,msNowParamF,msNowParamFF, rsi30SlopeSkip10ParamG,absMSMaxMinLast5ParamH,
                                 absMSMaxMinLast5ParamHH,sec5MinSlopeParamI, rsi14SlopeSkip3ExitParamV,ms3SlopeParamX,
                                 ms3SlopeParamXX,macdRSISmoothedMode,candlebarsArr):

        if self.Open():
            return None  # Position already opened

        if self.Routing:
            return None  # cannot open positions that are being routed


        if (self.MACDIndicator.MSPrev is None or self.MACDIndicator.MS is None or self.MACDIndicator.MaxMS is None\
            or self.MACDIndicator.MinMS is None or self.MinuteSmoothedRSIIndicator.GetRSISlope(5) is None
            or self.MinuteSmoothedRSIIndicator.GetRSISlope(10) is None or len(candlebarsArr)<5
            or self.MinuteNonSmoothedRSIIndicator.GetRSISlope(3) is None or self.MACDIndicator.GetMSSlope(3) is None
            ):
            return None

        #NO TRADE ON --> LONG ON
        #line 1
        if (self.MACDIndicator.MSPrev >=msNowParamA.FloatValue and self.MACDIndicator.MS >=msNowParamA.FloatValue
            and self.MACDIndicator.MaxMS >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMinParamB,msMinParamBB)
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(5)>rsi30SlopeSkip5ParamC.FloatValue):
            return _LONG_MACD_RSI_RULE_1

        # line 2
        if (self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS >=msNowParamA.FloatValue
            and self.MACDIndicator.MaxMS >= msMinParamB.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(5)>rsi30SlopeSkip5ParamC.FloatValue):
            return _LONG_MACD_RSI_RULE_2

        # line 3
        if (self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS < msNowParamA.FloatValue
            and self.MACDIndicator.MinMS < (-1* self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinParamD,msMaxMinParamDD))
            and (self.MACDIndicator.MinMS>0 and (self.MACDIndicator.MS % self.MACDIndicator.MinMS ) < msNowMaxParamE.FloatValue)
            and self.MACDIndicator.MS >=(-1*  self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowParamF,msNowParamFF))
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) > rsi30SlopeSkip5ParamC.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(10) >= (-1 * rsi30SlopeSkip10ParamG.FloatValue
            and self.MinuteNonSmoothedRSIIndicator.GetRSISlope(3) >= rsi14SlopeSkip3ExitParamV.FloatValue
            and self.MACDIndicator.GetMSSlope(3) >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,ms3SlopeParamX,ms3SlopeParamXX))
            ):
            return _LONG_MACD_RSI_RULE_3


        # line 4
        if (    self.MACDIndicator.GetMaxAbsMS(15) < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,absMSMaxMinLast5ParamH,absMSMaxMinLast5ParamHH)
            and self.GetSlope(candlebarsArr[-1].Close,candlebarsArr[-5].Close) >= sec5MinSlopeParamI.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) > rsi30SlopeSkip5ParamC.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(10) >= (-1 * rsi30SlopeSkip10ParamG.FloatValue)
          ):
            return _LONG_MACD_RSI_RULE_4


        return None

    def EvaluateGenericLongTrade(self,dailyBiasModelParam,dailySlopeModelParam, posMaximChangeParam,
                          posMaxLongDeltaParam,nonSmoothed14MinRSILongThreshold,candlebarsArr):

        if self.Open():
            #print ("Not opening because is opened:{}".format(self.Security.Symbol))
            return False #Position already opened

        if self.Routing:
            #print("Not opening because is routing:{}".format(self.Security.Symbol))
            return False #cannot open positions that are being routed

        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        if  (statisticalParams.TenMinSkipSlope is None or statisticalParams.ThreeMinSkipSlope is None
            or statisticalParams.ThreeToSixMinSkipSlope is None or statisticalParams.SixToNineMinSkipSlope is None
            or statisticalParams.PctChangeLastThreeMinSlope is None or statisticalParams.DeltaCurrValueAndFiftyMMov is None):
            return False


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
                # RSI 14 Minutes (NOT smoothed) --> IF crossing from below 30 to above 30
            #and  (nonSmoothed14MinRSILongThreshold.FloatValue is None or  self.MinuteNonSmoothedRSIIndicator.BullishSignal(nonSmoothed14MinRSILongThreshold.FloatValue))
            ):
            return True
        else:
            return False

    def EvaluateClosingMACDRSIShortTrade(self,candlebarsArr,msNowParamA,macdMaxGainParamJ,macdMaxGainParamJJ,macdGainNowMaxParamK,
                                         rsi30SlopeSkip5ExitParamL,msNowExitParamN,msNowExitParamNN,msMaxMinExitParamNBis,
                                         msMaxMinExitParamNNBis,msNowMaxMinExitParamP,msNowExitParamQ,msNowExitParamQQ,
                                         rsi30SlopeSkip10ExitParamR,msMaxMinExitParamS,msMaxMinExitParamSS,sec5MinSlopeExitParamT,
                                         gainMinStopLossExitParamU,gainMinStopLossExitParamUU,gainMinStopLossExitParamW,
                                         gainMinStopLossExitParamWW,gainStopLossExitParamY, gainMinStopLossExitParamZ,
                                         gainMinStopLossExitParamZZ,endOfdayLimitModelParam,maxGainForDayModelParam,
                                         pctMaxGainForClosingModelParam,maxLossForClosingModelParam,pctMaxLossForClosingModelParam,
                                         takeGainLimitModelParam,stopLossLimitModelParam,macdRSISmoothedMode):
        if not self.Open():
            return None  # Position not opened

        if self.GetNetOpenShares() >0 :
            return None  # We are in a LONG position

        terminalCond = self.EvaluateClosingTerminalCondition(candlebarsArr, endOfdayLimitModelParam,
                                                             maxGainForDayModelParam,
                                                             pctMaxGainForClosingModelParam,
                                                             maxLossForClosingModelParam,
                                                             pctMaxLossForClosingModelParam, takeGainLimitModelParam,
                                                             stopLossLimitModelParam)

        if terminalCond is not None:
            self.TerminalClose =True
            self.TerminalCloseCond = terminalCond
            return terminalCond

        if (self.CurrentProfitLastTrade is None or self.MaxProfitCurrentTrade is None or self.MinuteSmoothedRSIIndicator.GetRSISlope(5) is None
                or self.MACDIndicator.MSPrev is None or self.MACDIndicator.MS is None or self.MACDIndicator.MaxMS is None
                or self.MinuteSmoothedRSIIndicator.GetRSISlope(10) is None or self.MaxLossCurrentTrade is None or len(candlebarsArr)<5
                #or self.MACDIndicator.GetMaxABSMaxMinMS(5) is None
            ):
            return None

        # SHORT ON --> NO TRADE ON
        # rule 1
        if (    self.MaxProfitCurrentTrade >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,self.MACDIndicator.PriceHMinusL,macdMaxGainParamJ,macdMaxGainParamJJ)*100 #MaxProfix is calcualted as base 100 (ex: 72.23%)
            and (self.MaxProfitCurrentTrade > 0 and ((self.CurrentProfitLastTrade / self.MaxProfitCurrentTrade) < macdGainNowMaxParamK.FloatValue))
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) > rsi30SlopeSkip5ExitParamL.FloatValue
            ):
            return _EXIT_SHORT_MACD_RSI_COND_1

        # rule 2
        if (    self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
            and self.MACDIndicator.MS >= msNowParamA.FloatValue
            and self.MACDIndicator.MS >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowExitParamN,msNowExitParamNN)
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) > rsi30SlopeSkip5ExitParamL.FloatValue
        ):
            return _EXIT_SHORT_MACD_RSI_COND_2

        # rule 3
        if (    self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
            and self.MACDIndicator.MS >= msNowParamA.FloatValue
            and self.MaxLossCurrentTrade < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamW,gainMinStopLossExitParamWW)*100)
        ):
            return _EXIT_SHORT_MACD_RSI_COND_3

        # rule 4
        if (    self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS >= msNowParamA.FloatValue
            and self.MACDIndicator.MS >= msNowExitParamN.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) > rsi30SlopeSkip5ExitParamL.FloatValue
        ):
            return _EXIT_SHORT_MACD_RSI_COND_4

        # rule 5
        if (    self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS >= msNowParamA.FloatValue
            and self.MaxLossCurrentTrade < (gainMinStopLossExitParamW.FloatValue*100)
        ):
            return _EXIT_SHORT_MACD_RSI_COND_5

        # rule 6
        if (    self.MACDIndicator.MSPrev < msNowParamA.FloatValue
            and self.MACDIndicator.MS < msNowParamA.FloatValue
            and self.MACDIndicator.MinMS < (-1* self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinExitParamNBis,msMaxMinExitParamNNBis))
            and (self.MACDIndicator.MinMS >0 and ((self.MACDIndicator.MS/self.MACDIndicator.MinMS)<msNowMaxMinExitParamP.FloatValue))
            and self.MACDIndicator.MS >= (-1 * self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowExitParamQ,msNowExitParamQQ))
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) > rsi30SlopeSkip5ExitParamL.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(10) >= (-1*rsi30SlopeSkip10ExitParamR.FloatValue)
        ):
            return _EXIT_SHORT_MACD_RSI_COND_6


        # rule 7
        if (
                self.MACDIndicator.GetMaxAbsMS(15) < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinExitParamS,msMaxMinExitParamSS)
            and self.GetSlope(candlebarsArr[-1].Close,candlebarsArr[-5].Close) >= sec5MinSlopeExitParamT.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) >  rsi30SlopeSkip5ExitParamL.FloatValue
            and self.MinuteSmoothedRSIIndicator.GetRSISlope(10) >= (-1* rsi30SlopeSkip10ExitParamR.FloatValue)
        ):
            return _EXIT_SHORT_MACD_RSI_COND_7

        #rule 8
        if (    self.MACDIndicator.GetMaxAbsMS(15) < msMaxMinExitParamS.FloatValue
            and self.MaxLossCurrentTrade < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamZ,gainMinStopLossExitParamZZ)*100)
            ):  # MaxLoss is express in base 100 (ex: 71.23%)
            return _EXIT_SHORT_MACD_RSI_COND_8

        # rule 9
        if (    self.MaxLossCurrentTrade < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamU,gainMinStopLossExitParamUU)*100)): #MaxLoss is express in base 100 (ex: 71.23%)
            return _EXIT_SHORT_MACD_RSI_COND_9
            



    def EvaluateClosingGenericShortTrade(self,candlebarsArr,
                                  maxGainForClosingModelParam,pctMaxGainForClosingModelParam,
                                  maxLossForClosingModelParam,pctMaxLossForClosingModelParam,
                                  takeGainLimitModelParam,stopLossLimitModelParam,
                                  pctSlopeToCloseShortModelParam,
                                  endOfdayLimitModelParam,
                                  nonSmoothed14MinRSILongThreshold):



        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        #if statisticalParams.TenMinSkipSlope is not None:
            #print( "Close Short Trade - Ten Min Skip Slope {} for security {}".format(statisticalParams.TenMinSkipSlope, self.Security.Symbol))

        terminalCond = self.EvaluateClosingTerminalCondition(candlebarsArr, endOfdayLimitModelParam,
                                                             maxGainForClosingModelParam,
                                                             pctMaxGainForClosingModelParam,
                                                             maxLossForClosingModelParam,
                                                             pctMaxGainForClosingModelParam, takeGainLimitModelParam,
                                                             stopLossLimitModelParam)

        if not self.Open():
            return None #Position not opened

        if self.GetNetOpenShares()>0:
            return None#We are in a long position

        if terminalCond is not None:
            self.TerminalClose=True
            self.TerminalCloseCond=terminalCond
            return terminalCond

        # Maximum Gain during the trade exceeds a certain value and then drops to a percentage of that value
        if (    self.MaxProfitCurrentTrade is not None
            and self.CurrentProfitLastTrade is not None
            and (maxGainForClosingModelParam.FloatValue is not None and self.MaxProfitCurrentTrade >= maxGainForClosingModelParam.FloatValue * 100)
            and (pctMaxGainForClosingModelParam.FloatValue is not None and (self.CurrentProfitLastTrade < pctMaxGainForClosingModelParam.FloatValue * self.MaxProfit))
        ):
            return _EXIT_SHORT_COND_3

        # Maximum Loss during the trade exceeds (worse than) a certain value and then drops to a percentage of that value
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
        if(     statisticalParams.ThreeMinSkipSlope is not None
            and ( pctSlopeToCloseShortModelParam.FloatValue is not None and statisticalParams.ThreeMinSkipSlope >= pctSlopeToCloseShortModelParam.FloatValue)):
            return _EXIT_SHORT_COND_5

       # if ( self.MinuteNonSmoothedRSIIndicator.BullishSignal(nonSmoothed14MinRSILongThreshold.FloatValue)):
       #     return _EXIT_SHORT_COND_6

        return None

    #Defines if the condition for closing the day, will imply not opening another position during the day
    def EvaluateClosingTerminalCondition(self,candlebarsArr,endOfdayLimitModelParam,maxGainForClosingModelParam	,pctMaxGainForClosingModelParam,
                                         maxLossForClosingModelParam,pctMaxLossForClosingModelParam,takeGainLimitModelParam,stopLossLimitModelParam):

        # EXIT any open trades at 2:59 PM central time
        if (endOfdayLimitModelParam.StringValue is not None and self.EvaluateBiggerDate(endOfdayLimitModelParam)):
            return _EXIT_TERM_COND_EOF


        # CUMULATIVE Gain for the Day exceeds Take Gain Limit
        if ( takeGainLimitModelParam.FloatValue is not None and (self.CurrentProfit is not None and self.CurrentProfit > takeGainLimitModelParam.FloatValue*100)):
            return _EXIT_TERM_COND_1

        # CUMULATIVE Loss for the Day exceeds (worse than) Stop Loss Limit
        if (stopLossLimitModelParam.FloatValue is not None and (self.CurrentProfit is not None and self.CurrentProfit < stopLossLimitModelParam.FloatValue*100)):
            return _EXIT_TERM_COND_2

        return None

    def EvaluateClosingOnEndOfDay(self,candlebar,endOfdayLimitModelParam):
        if not self.Open():
            return False  # Position not opened

        openSummary = self.GetLastTradedSummary(Side.Buy if self.GetNetOpenShares()>0 else Side.Sell)

        if ( openSummary is not None
            and openSummary.Position.CloseEndOfDay is not None
            and openSummary.Position.CloseEndOfDay ==True
            and self.EvaluateBiggerDate( endOfdayLimitModelParam)
            and self.GetNetOpenShares()!=0):
            return True
        else:
            return False

    def EvaluateClosingOnStopLoss(self, candlebar):

        if not self.Open():
            return False  # Position not opened

        if self.GetNetOpenShares() < 0: #Stop loss on short position
            openSummary = self.GetLastTradedSummary(Side.Sell)

            if (openSummary is not None
                and openSummary.AvgPx is not None
                and openSummary.Position.StopLoss is not None
                and candlebar.Close is not None
                and candlebar.Close > (openSummary.AvgPx + openSummary.Position.StopLoss)#Short --> bigger than
                ):
                return True
            else:
                return False

        elif self.GetNetOpenShares() > 0: #Stop loss on long position
            openSummary = self.GetLastTradedSummary(Side.Buy)

            if (openSummary is not None
                and openSummary.Position.StopLoss is not None
                and openSummary.AvgPx is not None
                and candlebar.Close is not None
                and  candlebar.Close < (openSummary.AvgPx - openSummary.Position.StopLoss)#Long --> lower than
                ):
                return True
            else:
                return False
        else:
            return False

    def EvaluateClosingOnTakeProfit(self, candlebar):

        if not self.Open():
            return False  # Position not opened

        if self.GetNetOpenShares() < 0: #take profit on short position
            openSummary = self.GetLastTradedSummary(Side.Sell)

            if ( openSummary is not None
                and openSummary.Position.TakeProfit is not None
                and openSummary.AvgPx is not None
                and candlebar.Close is not None
                and  candlebar.Close < (openSummary.AvgPx - openSummary.Position.TakeProfit)
                ):#Short position --> lower than AvgPx - take profit
                return True
            else:
                return False
        elif self.GetNetOpenShares() > 0: #Stop loss on long position

            openSummary = self.GetLastTradedSummary(Side.Buy)

            if  (
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

    def EvaluateClosingMACDRSILongTrade(self,candlebarsArr,msNowParamA,macdMaxGainParamJ,macdMaxGainParamJJ,macdGainNowMaxParamK,
                                            rsi30SlopeSkip5ExitParamL,msNowExitParamN,msNowExitParamNN,msMaxMinExitParamNBis,
                                            msMaxMinExitParamNNBis,msNowMaxMinExitParamP,msNowExitParamQ,msNowExitParamQQ,
                                            rsi30SlopeSkip10ExitParamR,msMaxMinExitParamS,msMaxMinExitParamSS,
                                            sec5MinSlopeExitParamT,gainMinStopLossExitParamU,gainMinStopLossExitParamUU,
                                            gainMinStopLossExitParamW,gainMinStopLossExitParamWW,gainStopLossExitParamY,
                                            gainMinStopLossExitParamZ,gainMinStopLossExitParamZZ,endOfdayLimitModelParam,
                                            maxGainForDayModelParam,pctMaxGainForClosingModelParam,maxLossForClosingModelParam,
                                            pctMaxLossForClosingModelParam,takeGainLimitModelParam,stopLossLimitModelParam,
                                            macdRSISmoothedMode):
        if not self.Open():
            return None  # Position not opened

        if self.GetNetOpenShares() < 0:
            return None  # We are in a SHORT position

        terminalCond = self.EvaluateClosingTerminalCondition(candlebarsArr,endOfdayLimitModelParam, maxGainForDayModelParam,
                                                             pctMaxGainForClosingModelParam,maxLossForClosingModelParam,
                                                             pctMaxLossForClosingModelParam,takeGainLimitModelParam,
                                                             stopLossLimitModelParam)

        if terminalCond is not None:
            self.TerminalClose=True
            self.TerminalCloseCond = terminalCond
            return terminalCond


        if (
                self.CurrentProfitLastTrade is None or self.MaxProfitCurrentTrade is None or self.MinuteSmoothedRSIIndicator.GetRSISlope(5) is None
                or self.MACDIndicator.MSPrev is None or self.MACDIndicator.MS is None or self.MACDIndicator.MaxMS is None
                or self.MinuteSmoothedRSIIndicator.GetRSISlope(10) is None or self.MaxLossCurrentTrade is None
                or len(candlebarsArr)<5 or self.MACDIndicator.PriceHMinusL is None
                #or self.MACDIndicato.GetMaxABSMaxMinMS(5) is None
           ):
            return None

        # LONG ON --> NO TRADE ON
        # rule 1
        if (
                    self.MaxProfitCurrentTrade >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,macdMaxGainParamJ,macdMaxGainParamJJ)*100 #MaxProfixs is calculated in base 100 (ex: 73.22%)
                and (self.MaxProfitCurrentTrade> 0  and ((self.CurrentProfitLastTrade/self.MaxProfitCurrentTrade)<macdGainNowMaxParamK.FloatValue))
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) < (-1*rsi30SlopeSkip5ExitParamL.FloatValue)
           ):
            return _EXIT_LONG_MACD_RSI_COND_1

        # rule 2
        if (        self.MACDIndicator.MSPrev < msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MACDIndicator.MS < (-1 * self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowExitParamN,msNowExitParamNN))
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) < (-1*rsi30SlopeSkip5ExitParamL.FloatValue)

        ):
            return _EXIT_LONG_MACD_RSI_COND_2

        # rule 3
        if (self.MACDIndicator.MSPrev < msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MaxLossCurrentTrade < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamW,gainMinStopLossExitParamWW)*100

        ):
            return _EXIT_LONG_MACD_RSI_COND_3

        # rule 4
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MACDIndicator.MS < (-1 * msNowExitParamN.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) < (-1 * rsi30SlopeSkip5ExitParamL.FloatValue)

        ):
            return _EXIT_LONG_MACD_RSI_COND_4

        # rule 5
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS < msNowParamA.FloatValue
                and self.MaxLossCurrentTrade < (gainMinStopLossExitParamW.FloatValue*100)

        ):
            return _EXIT_LONG_MACD_RSI_COND_5

        # rule 6
        if (        self.MACDIndicator.MSPrev >= msNowParamA.FloatValue
                and self.MACDIndicator.MS >= msNowParamA.FloatValue
                and self.MACDIndicator.MaxMS >= self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinExitParamNBis,msMaxMinExitParamNNBis)
                and (self.MACDIndicator.MaxMS > 0 and ((self.MACDIndicator.MS / self.MACDIndicator.MaxMS) < msNowMaxMinExitParamP.FloatValue))
                and self.MACDIndicator.MS < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msNowExitParamQ,msNowExitParamQQ)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) < (-1 * rsi30SlopeSkip5ExitParamL.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(10) < rsi30SlopeSkip10ExitParamR.FloatValue
            ):
                return _EXIT_LONG_MACD_RSI_COND_6

        # rule 7
        if (        self.MACDIndicator.GetMaxAbsMS(15) < self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.AbsMaxMS,msMaxMinExitParamS,msMaxMinExitParamSS)
                and self.GetSlope(candlebarsArr[-1].Close, candlebarsArr[-5].Close) < ( -1 * sec5MinSlopeExitParamT.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(5) < (-1 * rsi30SlopeSkip5ExitParamL.FloatValue)
                and self.MinuteSmoothedRSIIndicator.GetRSISlope(10) < rsi30SlopeSkip10ExitParamR.FloatValue
            ):
            return _EXIT_LONG_MACD_RSI_COND_7


        # rule 8
        if (        self.MACDIndicator.GetMaxAbsMS(15) < msMaxMinExitParamS.FloatValue
                and self.MaxLossCurrentTrade < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamZ,gainMinStopLossExitParamZZ)*100)
            ):
            return _EXIT_LONG_MACD_RSI_COND_8

        # rule 9
        if (        self.MaxLossCurrentTrade < ( self.SmoothMACDRSIParam(macdRSISmoothedMode,self.MACDIndicator.PriceHMinusL,gainMinStopLossExitParamU,gainMinStopLossExitParamUU)*100)): #MaxLoss is calculated in base 100 (ex: 73.22%)
            return  _EXIT_LONG_MACD_RSI_COND_9


        return None #No condition to exit



    def EvaluateClosingGenericLongTrade(self,candlebarsArr,
                                  maxGainForClosingModelParam,pctMaxGainForClosingModelParam,
                                  maxLossForClosingModelParam,pctMaxLossForClosingModelParam,
                                  takeGainLimitModelParam,stopLossLimitModelParam,
                                  pctSlopeToCloseLongModelParam,
                                  endOfdayLimitModelParam,
                                  nonSmoothed14MinRSIShortThreshold):



        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        #if statisticalParams.TenMinSkipSlope is not None:
            #print( "Close Long Trade - Ten Min Skip Slope {} for security {}".format(statisticalParams.TenMinSkipSlope,self.Security.Symbol))

        terminalCond = self.EvaluateClosingTerminalCondition(candlebarsArr,endOfdayLimitModelParam,maxGainForClosingModelParam,pctMaxGainForClosingModelParam,
                                                             maxLossForClosingModelParam,pctMaxLossForClosingModelParam,takeGainLimitModelParam,stopLossLimitModelParam)

        if terminalCond is not None:
            self.TerminalClose=True
            self.TerminalCloseCond=terminalCond
            return terminalCond

        if not self.Open():
            return None  # Position not opened

        if self.GetNetOpenShares() < 0:
            return None  # We are in a short position

        # Maximum Gain during the trade exceeds a certain value and then drops to a percentage of that value
        if (    self.MaxProfitCurrentTrade is not None
            and self.CurrentProfitLastTrade is not None
            and (maxGainForClosingModelParam.FloatValue is not None and self.MaxProfitCurrentTrade >= maxGainForClosingModelParam.FloatValue * 100)
            and (pctMaxGainForClosingModelParam.FloatValue is not None and (self.CurrentProfitLastTrade < pctMaxGainForClosingModelParam.FloatValue * self.MaxProfit))
        ):
            return _EXIT_LONG_COND_3

        # Maximum Loss during the trade exceeds (worse than) a certain value and then drops to a percentage of that value
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
        if(     statisticalParams.ThreeMinSkipSlope is not None
            and (pctSlopeToCloseLongModelParam.FloatValue is not None and statisticalParams.ThreeMinSkipSlope < pctSlopeToCloseLongModelParam.FloatValue)
          ):
            return _EXIT_LONG_COND_5

        #if ( self.MinuteNonSmoothedRSIIndicator.BearishSignal(nonSmoothed14MinRSIShortThreshold.FloatValue)):
        #    return _EXIT_LONG_COND_6

        return None


    def EvaluateTimeRange(self,timeFromModelParam,timeToModelParam):
        now = datetime.now()
        fromTimeLowVol = time.strptime(timeFromModelParam.StringValue, "%I:%M %p")
        toTimeLowVol = time.strptime(timeToModelParam.StringValue, "%I:%M %p")
        todayStart = now.replace(hour=fromTimeLowVol.tm_hour, minute=fromTimeLowVol.tm_min, second=0, microsecond=0)
        todayEnd = now.replace(hour=toTimeLowVol.tm_hour, minute=toTimeLowVol.tm_min,
                               second=0, microsecond=0)
        return todayStart < now and now <todayEnd

    def EvaluateBiggerDate(self, timeFromModelParam):
        now = datetime.now()
        fromTime = time.strptime(timeFromModelParam.StringValue, "%I:%M %p")
        todayStart = now.replace(hour=fromTime.tm_hour, minute=fromTime.tm_min, second=0, microsecond=0)
        return todayStart<now

    def EvaluateValidTimeToEnterTrade(self,lowVolEntryThresholdModelParam,highVolEntryThresholdModelParam,
                                      lowVolFromTimeModelParam,lowVolToTimeModelParam,
                                      highVolFromTime1,highVolToTime1,highVolFromTime2,highVolToTime2):

        if(self.LastNDaysStdDev is not None):

            if (lowVolEntryThresholdModelParam.FloatValue is None or self.LastNDaysStdDev<lowVolEntryThresholdModelParam.FloatValue):
                if ( lowVolFromTimeModelParam.StringValue is not None and lowVolToTimeModelParam.StringValue is not None):
                    return  self.EvaluateTimeRange(lowVolFromTimeModelParam,lowVolToTimeModelParam)
                else:
                    return True #I am in a lowVol env , but no time prefferences


            if (highVolEntryThresholdModelParam.FloatValue is None or self.LastNDaysStdDev >= highVolEntryThresholdModelParam.FloatValue):
                volEntry1 = False
                volEntry2 = False
                if (highVolFromTime1.StringValue is not None and highVolToTime1.StringValue is not None):
                    volEntry1 =  self.EvaluateTimeRange(highVolFromTime1, highVolToTime1)

                if (  highVolFromTime2.StringValue is not None and highVolToTime2.StringValue is not None):
                    volEntry2 = self.EvaluateTimeRange(highVolFromTime2, highVolToTime2)

                return volEntry1 or volEntry2

            return False

        else:
            return False


    def GetAceptedSummaries(self):

        return  sorted(list(filter(lambda x: x.Position.GetLastOrder() is not None or x.Position.IsRejectedPosition(),
                                   self.ExecutionSummaries.values())),
                                   key=lambda x: x.CreateTime,reverse=True)

    def CalculateStdDevForLastNDays(self,marketDataArr,nDaysModelParam):

        if nDaysModelParam is not None:

            sortedMDArr= sorted(list(filter(lambda x: x.ClosingPrice is not None, marketDataArr.values())), key=lambda x: x.MDEntryDate,
                                reverse=True)[:nDaysModelParam.IntValue]

            closingPrices = []

            for md in sortedMDArr:
                closingPrices.append(md.ClosingPrice)

            self.LastNDaysStdDev = statistics.stdev(closingPrices)

        else:
            self.LastNDaysStdDev = None


    #endregion