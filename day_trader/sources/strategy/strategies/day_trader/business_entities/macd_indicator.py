from sources.strategy.strategies.day_trader.business_entities.testers.macd_indicator_tester import *

class MACDIndicator():

        def __init__(self,slow=26, fast=12, signal=9,MSMaxMinMinutes = 30):
                self.UpdateParameters(slow,fast,signal,MSMaxMinMinutes)
                self.Reset()

    #region Private Methods

        def UpdateParameters(self,slow=26, fast=12, signal=9,MSMaxMinMinutes = 30):
                self.Slow = slow
                self.Fast = fast
                self.Sign = signal
                self.MSMaxMinMinutes = MSMaxMinMinutes

        def Reset(self):
                self.MACD = None
                self.Signal = None
                self.MS = None
                self.MSPrev = None

                #A)MS Max Min since last MS going from - to + or viceversa
                self.MaxMSLastCrossover = None
                self.MinMSLastCrossover = None

                #B) Max Min Last N minutes
                self.MaxMS = None
                self.MinMS = None

                self.LastProcessedDateTime = None
                self.MSArray = []
                self.ContextSign = None


        def UpdateMSMaxMinOnLastCrossover(self):
                currentContext = 1 if self.MACD > self.Signal else -1

                if currentContext != self.ContextSign and self.ContextSign is not None:
                        self.MaxMSLastCrossover = self.MS
                        self.MinMSLastCrossover = self.MS

                if self.MinMSLastCrossover is None or self.MinMSLastCrossover < self.MS:
                        self.MinMSLastCrossover = self.MS

                if self.MinMSLastCrossover is None or self.MinMSLastCrossover > self.MS:
                        self.MinMSLastCrossover = self.MS

                self.ContextSign = currentContext

        def UpdateMSMaxMinOnLastNMinutes(self):


                maxAbsMS = None
                minAbsMS = None
                if len(self.MSArray)>=self.MSMaxMinMinutes:
                        lastNMinutesMSArray = self.MSArray[-1 * self.MSMaxMinMinutes:]

                        for MS in lastNMinutesMSArray:
                                absMS = MS if MS>0 else MS*-1
                                if maxAbsMS is None or maxAbsMS<absMS:
                                        maxAbsMS=absMS

                                if  minAbsMS is None or minAbsMS> absMS:
                                        minAbsMS = absMS

                        self.MaxMS=maxAbsMS
                        self.MinMS=minAbsMS




        def UpdateMSMaxMin(self):

                self.MSArray.append(self.MS)

                #A - Update MS Max Min since last MS going from - to + or viceversa
                self.UpdateMSMaxMinOnLastCrossover()

                #B - Update Max Min Last N minutes
                self.UpdateMSMaxMinOnLastNMinutes()


     #endregion

     #region Public Methods

        def GetMaxABSMaxMinMS(self, count):

                if len(self.MSMaxMinArray)<count:
                   return None

                arrayToConsider = self.MSMaxMinArray[-1*count:] #Last count elements

                max = None

                for msMinMax in arrayToConsider:
                        msMinMax=msMinMax if msMinMax>0 else -1*msMinMax

                        if max is None or max < msMinMax:
                                max=msMinMax

                return max

        def Update(self,CandleBarArr,slow=26, fast=12, signal=9,MSMaxMinMinutes = 30):
                sortedBars = sorted(list(filter(lambda x: x is not None, CandleBarArr)), key=lambda x: x.DateTime,reverse=False)

                lastBar = sortedBars[-1]

                if (self.LastProcessedDateTime is not None and self.LastProcessedDateTime==lastBar.DateTime):
                        return

                self.UpdateParameters(slow,fast,signal,MSMaxMinMinutes)

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
                        self.UpdateMSMaxMin()

                print("MACD print @{}- MACD:{}, Signal:{} Price:{}".format(self.LastProcessedDateTime,self.MACD,self.Signal,lastBar.Close))

     #endregion