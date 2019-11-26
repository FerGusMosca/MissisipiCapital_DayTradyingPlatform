from sources.framework.business_entities.securities.security import *
from sources.framework.business_entities.market_data.candle_bar import *

from sources.strategy.common.dto.position_statistical_parameters import *
from sources.strategy.common.dto.position_profits_and_losses import *

import json
from datetime import datetime, timedelta
from json import JSONEncoder

_EXIT_LONG_COND_1="EXIT_LONG_COND_1"
_EXIT_LONG_COND_2="EXIT_LONG_COND_2"
_EXIT_LONG_COND_3="EXIT_LONG_COND_3"
_EXIT_LONG_COND_4="EXIT_LONG_COND_4"
_EXIT_LONG_COND_5="EXIT_LONG_COND_5"

_EXIT_SHORT_COND_1="EXIT_SHORT_COND_1"
_EXIT_SHORT_COND_2="EXIT_SHORT_COND_2"
_EXIT_SHORT_COND_3="EXIT_SHORT_COND_3"
_EXIT_SHORT_COND_4="EXIT_SHORT_COND_4"
_EXIT_SHORT_COND_5="EXIT_SHORT_COND_5"


class DayTradingPosition():

    def __init__(self,id ,security,shares,active,routing,open,longSignal,shortSignal,signalType,signalDesc):
        self.Id=id
        self.Security = security
        self.SharesQuantity= shares
        self.Active=active
        self.MarketData=None
        self.ExecutionSummaries={}
        self.Routing =routing
        self.Open=open
        self.LongSignal = longSignal
        self.ShortSignal = shortSignal
        self.SignalType=signalType
        self.SignalDesc = signalDesc
        self.CurrentProfit = 0
        self.MaxProxit = 0
        self.MaxLoss=0


    #region Private Methods

    def GetMmmov(self, candleBarArr, skip, length):
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
        fiftyMinNoSkipMovAvg = self.GetMmmov(candlebarsArr, 0, 50)
        FiftyMinSkipTenMovAvg = self.GetMmmov(candlebarsArr, 10, 50)

        threeMinNoSkipMovAvg = self.GetMmmov(candlebarsArr, 0, 3)
        threeMinSkipTrheeMovAvg = self.GetMmmov(candlebarsArr, 3, 3)

        threeMinSkipSixMovAvg = self.GetMmmov(candlebarsArr, 6, 3)

        threeMinSkipNineMovAvg = self.GetMmmov(candlebarsArr, 9, 3)

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


    def CalculateProfits(self,profitsAndLosses):

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

    def CalculateCurrentDayProfits(self,marketData):

        profitsAndLosses = PositionsProfitsAndLosses()

        foundOpenPositions = self.CalculatePositionsProfit(profitsAndLosses)
        profitsAndLosses.PosMTM = self.CalculateMarkToMarket(marketData,profitsAndLosses,foundOpenPositions)
        profitsAndLosses.Profits = self.CalculateProfits(profitsAndLosses)

        if(profitsAndLosses.Profits>self.MaxProxit):
            self.MaxProxit=profitsAndLosses.Profits

        if(profitsAndLosses.Profits<self.MaxLoss):
            self.MaxLoss=profitsAndLosses.Profits

        self.CurrentProfit=profitsAndLosses.Profits

    def EvaluateLongTrade(self,dailyBiasModelParam,dailySlopeModelParam, posMaximChangeParam,
                          posMaxLongDeltaParam,candlebarsArr):

        if self.Open:
            return False #Position already opened

        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        if  (statisticalParams.TenMinSkipSlope is None or statisticalParams.ThreeMinSkipSlope
            or statisticalParams.ThreeToSixMinSkipSlope or statisticalParams.SixToNineMinSkipSlope
            or statisticalParams.PctChangeLastThreeMinSlope or statisticalParams.DeltaCurrValueAndFiftyMMov):
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

    def EvaluateClosingLongTrade(self,candlebarsArr,
                                  maxGainForClosingModelParam,pctMaxGainForClosingModelParam,
                                  maxLossForClosingModelParam,pctMaxLossForClosingModelParam,
                                  takeGainLimitModelParam,stopLossLimitModelParam,
                                  pctSlopeToCloseLongModelParam):
        if not self.Open:
            return None #Position not opened

        statisticalParams = self.GetStatisticalParameters(candlebarsArr)

        #Maximum Gain during the trade exceeds a certain value and then drops to a percentage of that value
        if(self.MaxProxit > maxGainForClosingModelParam.FloatValue
            and self.CurrentProfit<pctMaxGainForClosingModelParam.FloatValue*self.MaxProxit):
            return _EXIT_LONG_COND_1

        #Maximum Loss during the trade exceeds (worse than) a certain value and then drops to a percentage of that value
        if (self.MaxLoss < maxLossForClosingModelParam.FloatValue):
            absProfit = self.CurrentProfit if self.CurrentProfit>0 else (-1*self.CurrentProfit)
            absMaxLoss= self.MaxLoss if self.MaxLoss>0 else (-1*self.MaxLoss)
            if(absProfit < (pctMaxLossForClosingModelParam.FloatValue*absMaxLoss)):
                return _EXIT_LONG_COND_2

        #CUMULATIVE Gain for the Day exceeds Take Gain Limit
        if(self.CurrentProfit > takeGainLimitModelParam.FloatValue):
            return _EXIT_LONG_COND_3

        #CUMULATIVE Loss for the Day exceeds (worse than) Stop Loss Limit
        if (self.CurrentProfit < stopLossLimitModelParam.FloatValue):
            return _EXIT_LONG_COND_4

        #Last 3 minute slope of 3 minute moving average exceeds a certain value AGAINST the Trade
        if(statisticalParams.ThreeMinSkipSlope < pctSlopeToCloseLongModelParam.FloatValue):
            return _EXIT_LONG_COND_5



    #endregion