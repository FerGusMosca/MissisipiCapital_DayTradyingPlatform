import ta
from ta.trend import MACD
import pandas as pd
import math
from sources.strategy.strategies.day_trader.business_entities.macd_indicator_tester import *

class MACDIndicator():

        def __init__(self,slow=26, fast=12, sign=9):

                self.Slow = slow
                self.Fast = fast
                self.Sign = sign
                self.MACD = None
                self.Signal = None
                self.LastProcessedDateTime = None



        def update(self,CandleBarArr):
                sortedBars = sorted(list(filter(lambda x: x is not None, CandleBarArr)), key=lambda x: x.DateTime,reverse=False)

                lastBar = sortedBars[len(sortedBars)-1]

                if (self.LastProcessedDateTime is not None and self.LastProcessedDateTime==lastBar.DateTime):
                        return

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

                print("MACD @{}- MACD:{}, Signal:{}".format(self.LastProcessedDateTime,self.MACD,self.Signal))

