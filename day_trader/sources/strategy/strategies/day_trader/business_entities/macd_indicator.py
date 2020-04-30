from sources.strategy.strategies.day_trader.business_entities.testers.macd_indicator_tester import *
from datetime import *

class MACDIndicator():

        def __init__(self,slow=26, fast=12, signal=9):
                self.UpdateParameters(slow,fast,signal)
                self.Reset()

    #region Private Methods

        def UpdateParameters(self,slow=26, fast=12, signal=9):
                self.Slow = slow
                self.Fast = fast
                self.Sign = signal

        def UpdateLastTradeTimestamp(self):
                self.LastTradeTimestamp= datetime.now()

        def Reset(self):
                self.MACD = None
                self.Signal = None
                self.MS = None
                self.MSPrev = None

                #B) Max Min <Last CrossOver or Last Trade Timestamp>
                self.MaxMS = None
                self.MinMS = None

                self.AbsMaxMS = None
                self.MaxPrice = None
                self.MinPrice = None
                self.PriceHMinusL = None

                self.LastProcessedDateTime = None
                self.MSArray = []
                self.ContextSign = None
                self.LastTradeTimestamp = None

        def GetMaxAbsMS(self,length):

            max = 0
            lastNminArray =  self.MSArray[(-1*length):]

            for ms in lastNminArray:
                if max< abs(ms):
                    max=abs(ms)

            return max

        def UpdatePricesIndicators(self,lastBar):

                if self.MaxPrice is None or self.MaxPrice < lastBar.Close:
                        self.MaxPrice=lastBar.Close

                if self.MinPrice is None or self.MinPrice> lastBar.Close:
                        self.MinPrice = lastBar.Close

                if (self.MaxPrice is not None and self.MinPrice is not None):
                        self.PriceHMinusL=self.MaxPrice - self.MinPrice


        def UpdateMSMaxMin(self,absMaxMSPeriod =0):

                self.MSArray.append(self.MS)

                currentContext = 1 if self.MACD > self.Signal else -1

                if currentContext != self.ContextSign and self.ContextSign is not None:
                        self.MaxMS = self.MS
                        self.MinMS = self.MS

                if self.LastTradeTimestamp is not None:
                        self.MaxMS = self.MS
                        self.MinMS = self.MS
                        self.LastTradeTimestamp=None

                if self.MaxMS is None or self.MaxMS < self.MS:
                        self.MaxMS = self.MS

                if self.MinMS is None or self.MinMS > self.MS:
                        self.MinMS = self.MS

                if absMaxMSPeriod>0:
                        self.AbsMaxMS = self.GetMaxAbsMS(absMaxMSPeriod)
                elif self.AbsMaxMS is None or self.AbsMaxMS < abs(self.MS):
                        self.AbsMaxMS=abs(self.MS)

                self.ContextSign = currentContext


        def GetSlope(self, currValue, prevValue):

                if currValue is not None and prevValue is not None and prevValue != 0:
                        return (currValue - prevValue) / prevValue
                else:
                        return None


     #endregion

     #region Public Methods

        def GetMSSlope(self, index):

                if len(self.MSArray) >= index:
                        lastMSndex = self.MSArray[-1 * index]
                        return self.GetSlope(self.MS, lastMSndex)
                else:
                        return None


        def Update(self,CandleBarArr,slow=26, fast=12, signal=9, absMaxMSPeriod =0):
                sortedBars = sorted(list(filter(lambda x: x is not None, CandleBarArr)), key=lambda x: x.DateTime,reverse=False)

                lastBar = sortedBars[-1]

                if (self.LastProcessedDateTime is not None and self.LastProcessedDateTime==lastBar.DateTime):
                        return

                self.UpdateParameters(slow,fast,signal)

                self.LastProcessedDateTime = lastBar.DateTime

                #print("{}-Open={} Close={}".format(lastBar.DateTime,lastBar.Open,lastBar.Close))

                prices = []

                for bar in sortedBars:
                        prices.append(bar.Close)

                df = pd.Series(prices, name="macd")

                macdEntity = MACD(close=df, n_slow=self.Slow, n_fast=self.Fast, n_sign=self.Sign, fillna=0)
                macdSeries = macdEntity.macd()
                signalSeries= macdEntity.macd_signal()

                if (len(macdSeries)>0 and not math.isnan(macdSeries[len(macdSeries)-1])):
                        self.MACD=macdSeries[len(macdSeries)-1]

                if (len(signalSeries) > 0 and not math.isnan(signalSeries[len(signalSeries) - 1])):
                        self.Signal = signalSeries[len(signalSeries) - 1]


                if lastBar is not None and self.MACD is not None and self.Signal is not None:
                        self.MSPrev=self.MS
                        self.MS = (500* (self.MACD - self.Signal))/lastBar.Close
                        self.UpdateMSMaxMin(absMaxMSPeriod)

                print("MACD print @{}- MACD:{}, Signal:{} Price:{}".format(self.LastProcessedDateTime,self.MACD,self.Signal,lastBar.Close))

     #endregion