from sources.strategy.strategies.day_trader.business_entities.testers.macd_indicator_tester import *

class MACDIndicator():

        def __init__(self,slow=26, fast=12, signal=9):

                self.Slow = slow
                self.Fast = fast
                self.Sign = signal
                self.MACD = None
                self.Signal = None
                self.MSPrev = None
                self.MS = None
                self.MaxMS = None
                self.MinMS = None
                self.LastProcessedDateTime = None

    #region Private Methods

        def UpdateParameters(self,slow=26, fast=12, signal=9):
                self.Slow = slow
                self.Fast = fast
                self.Sign = signal

        def Reset(self):
                self.MACD = None
                self.Signal = None
                self.MS = None
                self.MSPrev = None
                self.MaxMS = None
                self.MinMS = None
                self.LastProcessedDateTime = None



     #endregion

     #region Public Methods


        def Update(self,CandleBarArr,slow=26, fast=12, signal=9):
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

                if self.MaxMS is None or self.MaxMS< self.MS:
                        self.MaxMS= self.MS

                if self.MinMS is None or self.MaxMS > self.MS:
                        self.MinMS = self.MS

                print("MACD print @{}- MACD:{}, Signal:{} Price:{}".format(self.LastProcessedDateTime,self.MACD,self.Signal,lastBar.Close))

     #endregion