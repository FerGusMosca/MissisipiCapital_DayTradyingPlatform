from sources.framework.business_entities.market_data.candle_bar import *
class RSIIndicator():


    def __init__(self):
        self.UpOpen=0
        self.DownOpen = 0
        self.SmoothUp=0
        self.SmoothDown = 0
        self.BootstrapUpOpen = 0
        self.BootstrapDownOpen = 0
        self.LastProcessedDateTime = None
        self.RSI= 0
        self.PrevRSI = None



    def Reset(self):
        self.UpOpen=0
        self.DownOpen = 0
        self.SmoothUp=0
        self.SmoothDown = 0
        self.BootstrapUpOpen = 0
        self.BootstrapDownOpen = 0
        self.RSI= 0
        self.PrevRSI = None

    def CalculatedCumAvg(self,sortedBars,bootStrap, xOpen, prevValue,MINUTES_RSI_LENGTH,direction):

        if len(sortedBars)==MINUTES_RSI_LENGTH:
            return bootStrap/MINUTES_RSI_LENGTH
        elif len(sortedBars)>MINUTES_RSI_LENGTH:
            #if (sortedBars[0].Security.Symbol == "SPY"):
            #    print("SPY-{}-(RSI{}-{} calc: prevRSI={},newOpen={}".format(sortedBars[0].DateTime,MINUTES_RSI_LENGTH,direction,prevValue,xOpen))
            return ( (prevValue*(MINUTES_RSI_LENGTH-2))  + xOpen)/((MINUTES_RSI_LENGTH-1))
        else:
            return 0


    def Update(self,candleBarArr,MINUTES_RSI_LENGTH):

        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)), key=lambda x: x.DateTime, reverse=True)

        if len(sortedBars)>=2:

            if sortedBars[0].Close is None or sortedBars[1].Close is None:
                return

            if self.LastProcessedDateTime==sortedBars[0].DateTime:
                return #Already Processed

            self.UpOpen= sortedBars[0].Close - sortedBars[1].Close  if (sortedBars[0].Close >= sortedBars[1].Close) else 0
            self.DownOpen = sortedBars[1].Close - sortedBars[0].Close if (sortedBars[0].Close < sortedBars[1].Close) else 0

            self.BootstrapUpOpen += self.UpOpen if len(sortedBars)<=(MINUTES_RSI_LENGTH) else 0
            self.BootstrapDownOpen += self.DownOpen if len(sortedBars)<=(MINUTES_RSI_LENGTH) else 0

            self.SmoothUp = self.CalculatedCumAvg(sortedBars,self.BootstrapUpOpen,self.UpOpen,self.SmoothUp,MINUTES_RSI_LENGTH,"up")
            self.SmoothDown = self.CalculatedCumAvg(sortedBars,self.BootstrapDownOpen,self.DownOpen,self.SmoothDown,MINUTES_RSI_LENGTH,"down")
            self.PrevRSI = self.RSI if self.RSI !=0 else None
            self.RSI= (100-(100/(1+(self.SmoothUp/self.SmoothDown)))) if self.SmoothDown>0 else 0
            self.LastProcessedDateTime=sortedBars[0].DateTime
            #if(sortedBars[0].Security.Symbol=="SPY"):
            #    print("SPY-{}-final RSI{}:{} -- previous RSI{}:{}".format(self.LastProcessedDateTime,MINUTES_RSI_LENGTH,self.RSI,MINUTES_RSI_LENGTH,self.PrevRSI))



    def UpdateDaily(self,marketDataArr, DAILY_RSI_LENGTH):

        sortedMDs = sorted(list(filter(lambda x: x is not None, list(marketDataArr.values()))), key=lambda x: x.MDEntryDate, reverse=False)

        if len(sortedMDs)>=DAILY_RSI_LENGTH:

            prevDailyMD = None
            i = 0
            for dailyMD in sortedMDs:


                #If I have more market data in marketDataArr than values needed in DAILY_RSI_LENGTH, I skip the first (len(marketDataArr)- DAILY_RSI_LENGTH)
                if prevDailyMD is not None and ( (len(sortedMDs)-i)<=DAILY_RSI_LENGTH):
                    self.BootstrapUpOpen+= dailyMD.ClosingPrice - prevDailyMD.ClosingPrice  if (dailyMD.ClosingPrice >= prevDailyMD.ClosingPrice) else 0
                    self.BootstrapDownOpen += prevDailyMD.ClosingPrice - dailyMD.ClosingPrice if (dailyMD.ClosingPrice < prevDailyMD.ClosingPrice) else 0

                prevDailyMD=dailyMD
                i+=1


            self.SmoothUp = self.BootstrapUpOpen / DAILY_RSI_LENGTH
            self.SmoothDown = self.BootstrapDownOpen / DAILY_RSI_LENGTH
            self.RSI= (100-(100/(1+(self.SmoothUp/self.SmoothDown)))) if self.SmoothDown>0 else 0

        else:
            raise Exception("Could not calculate daily RSI as market data array length={} and RSI daily length ={}".format(len(sortedMDs),DAILY_RSI_LENGTH))


    def BullishSignal(self,threshold):
        if self.RSI is not None and self.PrevRSI is not None:
            return self.RSI > threshold and self.PrevRSI <= threshold
        else:
            return False


    def BearishSignal(self,threshold):
        if self.RSI is not None and self.PrevRSI is not None:
            return  self.RSI < threshold and self.PrevRSI >= threshold
        else:
            return False
