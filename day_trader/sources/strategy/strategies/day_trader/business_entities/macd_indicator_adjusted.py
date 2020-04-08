from sources.strategy.strategies.day_trader.business_entities.testers.macd_indicator_tester import *
from sources.strategy.strategies.day_trader.business_entities.macd_indicator import *

class MACDIndicatorAdjusted(MACDIndicator):

    def __init__(self, slow=26, fast=12, signal=9):
        self.UpdateParameters(slow, fast, signal)
        self.PrevFast=0
        self.PrevSlow=0
        self.MACDArray = []
        self.Reset()


    def UpdateAverage(self,price,index,prevValue):
        return price * (2 /(index + 1)) + prevValue * (1 - (2 / (index + 1)))

    def UpdateMACD(self,prices,length):

        if(len(prices)<length):
            self.PrevFast = 0
            self.PrevSlow = 0
            self.MACDArray=[]
            self.MACD=None
        elif len(prices)==length:
            fast = sum(prices)/length
            slow = sum(prices)/length
            self.MACD = fast-slow
            self.PrevFast = fast
            self.PrevSlow = slow

        else:
            fast = self.UpdateAverage(prices[-1],self.Fast,self.PrevFast)
            slow = self.UpdateAverage(prices[-1], self.Slow, self.PrevSlow)
            self.MACD=fast-slow
            self.PrevFast=fast
            self.PrevSlow=slow
            self.MACDArray.append(self.MACD)

    def UpdateSignal(self,index):

        if len(self.MACDArray)< index:
            self.Signal = None
        elif len(self.MACDArray) == index:
            self.Signal = sum(self.MACDArray) / index
        else:
            self.Signal = self.UpdateAverage(self.MACDArray[-1], self.Sign, self.Signal)


    def Update(self, CandleBarArr, slow=26, fast=12, signal=9):
        sortedBars = sorted(list(filter(lambda x: x is not None, CandleBarArr)), key=lambda x: x.DateTime,
                            reverse=False)

        lastBar = sortedBars[-1]

        if (self.LastProcessedDateTime is not None and self.LastProcessedDateTime == lastBar.DateTime):
            return

        self.UpdateParameters(slow, fast, signal)

        self.LastProcessedDateTime = lastBar.DateTime


        prices = []

        for bar in sortedBars:
            prices.append(bar.Close)

        index= 10

        self.UpdateMACD(prices,index)
        self.UpdateSignal(index)

        if lastBar is not None and self.MACD is not None and self.Signal is not None:
            self.MSPrev = self.MS
            self.MS = (500 * (self.MACD - self.Signal)) / lastBar.Close
            self.UpdateMSMaxMin()
        '''
        print("MACD print @{}- MACD:{}, Signal:{} Price:{}".format(self.LastProcessedDateTime, self.MACD, self.Signal,
                                                                   lastBar.Close))
        '''
