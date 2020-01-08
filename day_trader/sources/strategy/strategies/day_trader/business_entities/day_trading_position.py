from sources.framework.business_entities.securities.security import *
from sources.framework.business_entities.market_data.candle_bar import *
from sources.framework.common.enums.Side import *
from sources.strategy.common.dto.position_statistical_parameters import *
from sources.strategy.common.dto.position_profits_and_losses import *

import json
import statistics
import time
from datetime import datetime, timedelta
from json import JSONEncoder

_EXIT_LONG_COND_1="EXIT_LONG_COND_1"
_EXIT_LONG_COND_2="EXIT_LONG_COND_2"
_EXIT_LONG_COND_3="EXIT_LONG_COND_3"
_EXIT_LONG_COND_4="EXIT_LONG_COND_4"
_EXIT_LONG_COND_5="EXIT_LONG_COND_5"
_EXIT_LONG_COND_EOF="EXIT_LONG_COND_EOF"

_EXIT_SHORT_COND_1="EXIT_SHORT_COND_1"
_EXIT_SHORT_COND_2="EXIT_SHORT_COND_2"
_EXIT_SHORT_COND_3="EXIT_SHORT_COND_3"
_EXIT_SHORT_COND_4="EXIT_SHORT_COND_4"
_EXIT_SHORT_COND_5="EXIT_SHORT_COND_5"
_EXIT_SHORT_COND_EOF="EXIT_SHORT_COND_EOF"

class DayTradingPosition():

    def __init__(self,id ,security,shares,active,routing,open,longSignal,shortSignal,signalType,signalDesc):
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
        self.LastNDaysStdDev = 0
        self.LastProfitCalculationDay = None


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

        if currMovAvg is not None and prevMovAvg is not None:
            return (currMovAvg-prevMovAvg)/prevMovAvg
        else:
            return None

    def GetSpecificBar(self,candleBarArr, index):
        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)),key=lambda x: x.DateTime, reverse=True)

        if(sortedBars is not None and len(sortedBars)>=index):
            return sortedBars[index-1]
        else:
            return None


    def GetStatisticalParameters(self,candlebarsArr):
        fiftyMinNoSkipMovAvg = self.GetMov(candlebarsArr, 0, 50)
        FiftyMinSkipTenMovAvg = self.GetMov(candlebarsArr, 10, 50)

        #if we don't have enough values --> we use what we have!
        if(fiftyMinNoSkipMovAvg is None and len(candlebarsArr)>=3):
            fiftyMinNoSkipMovAvg = self.GetMov(candlebarsArr,0,len(candlebarsArr))
        # if we don't have enough values --> we use what we have!
        if (FiftyMinSkipTenMovAvg is None and len(candlebarsArr)>=3):
            FiftyMinSkipTenMovAvg = self.GetMov(candlebarsArr, 0, len(candlebarsArr))

        threeMinNoSkipMovAvg = self.GetMov(candlebarsArr, 0, 3)
        threeMinSkipTrheeMovAvg = self.GetMov(candlebarsArr, 3, 3)

        threeMinSkipSixMovAvg = self.GetMov(candlebarsArr, 6, 3)

        threeMinSkipNineMovAvg = self.GetMov(candlebarsArr, 9, 3)

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
        elif profitsAndLosses.NetShares < 0:
            monProfits=profitsAndLosses.MoneyIncome - profitsAndLosses.PosMTM - profitsAndLosses.MoneyOutflow
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
        else:
            if profitsAndLosses.MoneyOutflow > 0:
                profits = (profitsAndLosses.MoneyIncome / profitsAndLosses.MoneyOutflow)-1
            elif profitsAndLosses.MoneyIncome ==0:
                profits = 0
            else:
                raise Exception( "Could not calculate profit for closed position where money outflow is 0, for symbol {}" .format(self.Security.Symbol))
        return profits

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
                if summary.IsLongPosition():
                    netShares += summary.GetNetShares()
                else:
                    netShares -= summary.GetNetShares()

        return netShares

    def CalculateLastTradeProfit(self, profitsAndLosses, marketData):

        lastTradedSummaries = sorted(list(filter(lambda x: x.Timestamp.date() == datetime.now().date() and x.GetNetShares() != 0
                                                 and (x.Position.Side==Side.Buy if self.GetNetOpenShares()>0 else x.Position.Side==Side.Sell),
                           self.ExecutionSummaries.values())),key=lambda x: x.Timestamp, reverse=True)

        lastTradedSummary=None
        if(len(lastTradedSummaries)>0):
            lastTradedSummary=lastTradedSummaries[0]

        if lastTradedSummary is not None and marketData.Trade is not None and lastTradedSummary.AvgPx is not None:
            profitsAndLosses.IncreaseDecrease = marketData.Trade-  lastTradedSummary.AvgPx
            if lastTradedSummary.IsLongPosition():#LONG
                profitsAndLosses.MonetaryProfitLastTrade=( marketData.Trade-lastTradedSummary.AvgPx)*lastTradedSummary.GetNetShares()
                profitsAndLosses.ProfitLastTrade = ((marketData.Trade/lastTradedSummary.AvgPx)-1)*100 if lastTradedSummary.AvgPx >0 else 0
            else:#SHORT
                profitsAndLosses.MonetaryProfitLastTrade = ( lastTradedSummary.AvgPx - marketData.Trade)*lastTradedSummary.GetNetShares()
                profitsAndLosses.ProfitLastTrade = ((lastTradedSummary.AvgPx/marketData.Trade)-1)*100 if marketData.Trade >0 else 0
        else:
            profitsAndLosses.MonetaryProfitLastTrade = 0
            profitsAndLosses.ProfitLastTrade = 0


    def CalculatePositionsProfit(self,profitsAndLosses):
        todaySummaries = sorted(list(filter(lambda x: x.Timestamp.date() == datetime.now().date() and x.CumQty >= 0, self.ExecutionSummaries.values())),
                                            key=lambda x: x.Timestamp, reverse=False)
        foundOpenPositions = False

        for summary in todaySummaries:
            # first we calculate the traded positions
            if summary.GetTradedSummary()>0:
                if summary.IsLongPosition():
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

    def UpdateRouting(self):
        nextOpenPos = next(iter(list(filter(lambda x: x.Position.IsOpenPosition(), self.ExecutionSummaries.values()))), None)

        self.Routing= nextOpenPos is not None

    def GetOpenSummaries(self):
        return list(filter(lambda x: x.Position.IsOpenPosition(), self.ExecutionSummaries.values()))

    def ResetProfitCounters(self,now):
        self.CurrentProfit = 0
        self.CurrentProfitLastTrade= 0
        self.CurrentProfitMonetary = 0
        self.CurrentProfitMonetaryLastTrade= 0

        self.MaxLoss = 0
        self.MaxProfit = 0
        self.LastProfitCalculationDay = datetime.now()

    def CalculateCurrentDayProfits(self,marketData):

        profitsAndLosses = PositionsProfitsAndLosses()

        foundOpenPositions = self.CalculatePositionsProfit(profitsAndLosses)
        profitsAndLosses.PosMTM = self.CalculateMarkToMarket(marketData,profitsAndLosses,foundOpenPositions)

        profitsAndLosses.Profits = self.CalculatePercentageProfits(profitsAndLosses)
        profitsAndLosses.MonetaryProfits = self.CalculateMonetaryProfits(profitsAndLosses)

        if foundOpenPositions:
            self.CalculateLastTradeProfit(profitsAndLosses,marketData)

        if(profitsAndLosses.Profits>self.MaxProfit):
            self.MaxProfit=profitsAndLosses.Profits

        if(profitsAndLosses.Profits<self.MaxLoss):
            self.MaxLoss=profitsAndLosses.Profits

        self.CurrentProfit=profitsAndLosses.Profits
        self.CurrentProfitMonetary = profitsAndLosses.MonetaryProfits
        self.CurrentProfitLastTrade = profitsAndLosses.ProfitLastTrade
        self.CurrentProfitMonetaryLastTrade = profitsAndLosses.MonetaryProfitLastTrade
        self.LastProfitCalculationDay=datetime.now()
        self.IncreaseDecrease=profitsAndLosses.IncreaseDecrease

    def EvaluateShortTrade(self,dailyBiasModelParam,dailySlopeModelParam, posMaximShortChangeParam,
                           posMaxShortDeltaParam,candlebarsArr):

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

        if  (    dailyBiasModelParam.FloatValue<0 #Daily Bias
                # Last 10 minute slope of 50 minute moving average
            and  statisticalParams.TenMinSkipSlope < dailySlopeModelParam.FloatValue
                # Last 3 minute slope of 3 minute moving average
            and statisticalParams.ThreeMinSkipSlope < dailySlopeModelParam.FloatValue
                # Previous 3 to 6 minute slope of 3 minute moving average
            and statisticalParams.ThreeToSixMinSkipSlope < dailySlopeModelParam.FloatValue
                # Previous 6 to 9 minute slope of 3 minute moving average
            and statisticalParams.SixToNineMinSkipSlope < dailySlopeModelParam.FloatValue
                # Maximum change in last 3 minutes
            and statisticalParams.PctChangeLastThreeMinSlope > posMaximShortChangeParam.FloatValue
                # Delta between current value and 50MMA
            and statisticalParams.DeltaCurrValueAndFiftyMMov > posMaxShortDeltaParam.FloatValue
        ):
            return True
        else:
            return False

    def EvaluateLongTrade(self,dailyBiasModelParam,dailySlopeModelParam, posMaximChangeParam,
                          posMaxLongDeltaParam,candlebarsArr):

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

        if  (    dailyBiasModelParam.FloatValue>=0 #Daily Bias
                # Last 10 minute slope of 50 minute moving average
            and  statisticalParams.TenMinSkipSlope >= dailySlopeModelParam.FloatValue
                # Last 3 minute slope of 3 minute moving average
            and statisticalParams.ThreeMinSkipSlope >= dailySlopeModelParam.FloatValue
                # Previous 3 to 6 minute slope of 3 minute moving average
            and statisticalParams.ThreeToSixMinSkipSlope > dailySlopeModelParam.FloatValue
                # Previous 6 to 9 minute slope of 3 minute moving average
            and statisticalParams.SixToNineMinSkipSlope > dailySlopeModelParam.FloatValue
                # Maximum change in last 3 minutes
            and statisticalParams.PctChangeLastThreeMinSlope < posMaximChangeParam.FloatValue
                # Delta between current value and 50MMA
            and statisticalParams.DeltaCurrValueAndFiftyMMov < posMaxLongDeltaParam.FloatValue
        ):
            return True
        else:
            return False

    def EvaluateClosingShortTrade(self,candlebarsArr,
                                  maxGainForClosingModelParam,pctMaxGainForClosingModelParam,
                                  maxLossForClosingModelParam,pctMaxLossForClosingModelParam,
                                  takeGainLimitModelParam,stopLossLimitModelParam,
                                  pctSlopeToCloseShortModelParam,
                                  endOfdayLimitModelParam):



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
            return terminalCond

        #Last 3 minute slope of 3 minute moving average exceeds a certain value AGAINST the Trade
        if(     statisticalParams.ThreeMinSkipSlope is not None
            and statisticalParams.ThreeMinSkipSlope >= pctSlopeToCloseShortModelParam.FloatValue):
            return _EXIT_LONG_COND_5

        return None

    #Defines if the condition for closing the day, will imply not opening another position during the day
    def EvaluateClosingTerminalCondition(self,candlebarsArr,endOfdayLimitModelParam,maxGainForClosingModelParam	,pctMaxGainForClosingModelParam,
                                         maxLossForClosingModelParam,pctMaxLossForClosingModelParam,takeGainLimitModelParam,stopLossLimitModelParam):

        # EXIT any open trades at 2:59 PM central time
        if self.EvaluateBiggerDate(endOfdayLimitModelParam):
            return _EXIT_LONG_COND_EOF

        # Maximum Gain during the trade exceeds a certain value and then drops to a percentage of that value
        if (self.MaxProfit is not None
                and self.CurrentProfit is not None
                and self.MaxProfit >= maxGainForClosingModelParam.FloatValue
                and self.CurrentProfit < pctMaxGainForClosingModelParam.FloatValue * self.MaxProfit):
            return _EXIT_LONG_COND_1

        # Maximum Loss during the trade exceeds (worse than) a certain value and then drops to a percentage of that value
        if (self.CurrentProfit is not None
            and self.MaxLoss is not None
            and self.MaxLoss <= maxLossForClosingModelParam.FloatValue
            and self.CurrentProfit < 0):
            absProfit = self.CurrentProfit if self.CurrentProfit > 0 else (-1 * self.CurrentProfit)
            absMaxLoss = self.MaxLoss if self.MaxLoss > 0 else (-1 * self.MaxLoss)
            if (absProfit < (pctMaxLossForClosingModelParam.FloatValue * absMaxLoss)):
                return _EXIT_LONG_COND_2

        # CUMULATIVE Gain for the Day exceeds Take Gain Limit
        if (self.CurrentProfit is not None and self.CurrentProfit > takeGainLimitModelParam.FloatValue):
            return _EXIT_LONG_COND_3

        # CUMULATIVE Loss for the Day exceeds (worse than) Stop Loss Limit
        if (self.CurrentProfit is not None and self.CurrentProfit < stopLossLimitModelParam.FloatValue):
            return _EXIT_LONG_COND_4

        return None

    def EvaluateClosingLongTrade(self,candlebarsArr,
                                  maxGainForClosingModelParam,pctMaxGainForClosingModelParam,
                                  maxLossForClosingModelParam,pctMaxLossForClosingModelParam,
                                  takeGainLimitModelParam,stopLossLimitModelParam,
                                  pctSlopeToCloseLongModelParam,
                                  endOfdayLimitModelParam):



        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        #if statisticalParams.TenMinSkipSlope is not None:
            #print( "Close Long Trade - Ten Min Skip Slope {} for security {}".format(statisticalParams.TenMinSkipSlope,self.Security.Symbol))

        terminalCond = self.EvaluateClosingTerminalCondition(candlebarsArr,endOfdayLimitModelParam,maxGainForClosingModelParam,pctMaxGainForClosingModelParam,
                                                             maxLossForClosingModelParam,pctMaxLossForClosingModelParam,takeGainLimitModelParam,stopLossLimitModelParam)

        if terminalCond is not None:
            return terminalCond

        if not self.Open():
            return None  # Position not opened

        if self.GetNetOpenShares() < 0:
            return None  # We are in a short position

        #Last 3 minute slope of 3 minute moving average exceeds a certain value AGAINST the Trade
        if(     statisticalParams.ThreeMinSkipSlope is not None
            and statisticalParams.ThreeMinSkipSlope < pctSlopeToCloseLongModelParam.FloatValue):
            return _EXIT_LONG_COND_5

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

            if self.LastNDaysStdDev<lowVolEntryThresholdModelParam.FloatValue:
                if (self.EvaluateTimeRange(lowVolFromTimeModelParam,lowVolToTimeModelParam)):
                    return True

            if self.LastNDaysStdDev >= highVolEntryThresholdModelParam.FloatValue:
                if (self.EvaluateTimeRange(highVolFromTime1, highVolToTime1)):
                    return True

                if (self.EvaluateTimeRange(highVolFromTime2, highVolToTime2)):
                    return True

            return False

        else:
            return False


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