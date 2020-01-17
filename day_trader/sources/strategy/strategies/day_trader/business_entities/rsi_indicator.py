from sources.framework.business_entities.market_data.candle_bar import *
class RSIIndicator():

    @staticmethod
    def RSI_LENGTH():
        return 14

    def __init__(self):
        self.UpOpen=0
        self.DownOpen = 0
        self.SmoothUp=0
        self.SmoothDown = 0
        self.BootstrapUpOpen = 0
        self.BootstrapDownOpen = 0
        self.RSI= 0



    def Reset(self):
        self.UpOpen=0
        self.DownOpen = 0
        self.SmoothUp=0
        self.SmoothDown = 0
        self.BootstrapUpOpen = 0
        self.BootstrapDownOpen = 0
        self.RSI= 0

    def CalculatedCumAvg(self,sortedBars,bootStrap, xOpen, prevValue):

        if len(sortedBars)==(RSIIndicator.RSI_LENGTH()+1):
            return bootStrap/(RSIIndicator.RSI_LENGTH()+1)
        elif len(sortedBars)>(RSIIndicator.RSI_LENGTH()+1):
            return ( (prevValue*(RSIIndicator.RSI_LENGTH()-1))  + xOpen)/(RSIIndicator.RSI_LENGTH())
        else:
            return 0


    def Update(self,candleBarArr):

        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)), key=lambda x: x.DateTime, reverse=True)

        if len(sortedBars)>=2:

            if sortedBars[0].Close is None or sortedBars[1].Close is None:
                return

            self.UpOpen= sortedBars[0].Close  if (sortedBars[0].Close >= sortedBars[1].Close) else 0
            self.DownOpen = sortedBars[0].Close if (sortedBars[0].Close < sortedBars[1].Close) else 0

            self.BootstrapUpOpen += self.UpOpen if len(sortedBars)<=(RSIIndicator.RSI_LENGTH()+1) else 0
            self.BootstrapDownOpen += self.DownOpen if len(sortedBars)<=(RSIIndicator.RSI_LENGTH()+1) else 0

            self.SmoothUp = self.CalculatedCumAvg(sortedBars,self.BootstrapUpOpen,self.UpOpen,self.SmoothUp)
            self.SmoothDown = self.CalculatedCumAvg(sortedBars,self.BootstrapDownOpen,self.DownOpen,self.SmoothDown)
            self.RSI= (100-(100/(1+(self.SmoothUp/self.SmoothDown)))) if self.SmoothDown>0 else 0
