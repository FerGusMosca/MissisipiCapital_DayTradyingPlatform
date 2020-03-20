from sources.framework.business_entities.market_data.candle_bar import *

class RSIIndicator():


    def __init__(self,smoothed=False):
        self.Reset()
        self.Smoothed = smoothed


    def Reset(self):
        self.UpOpen = []
        self.DownOpen = []
        self.SmoothUp = []
        self.SmoothDown = []
        self.LastProcessedDateTime = None
        self.RSIArray = []
        self.RSI = None
        self.PrevRSI = None


    def CalculateAverage(self,array,length):
        sum=0
        # Just the average
        for value in array:
            sum += value
        return sum / length

    def CalculatedUpDown(self,MINUTES_RSI_LENGTH,xOpenArr,xSmoothOpenArr,smoothed,direction):
        
        lastNElems = xOpenArr[(-1)*MINUTES_RSI_LENGTH:]
        sum=0

        if len(xOpenArr)>=MINUTES_RSI_LENGTH:
           prevSmoothOpen = xSmoothOpenArr[-1]
           lastxOpen = xOpenArr[-1]


           if not smoothed:
               return self.CalculateAverage(lastNElems,MINUTES_RSI_LENGTH)

           else:
               if(len(xOpenArr)==MINUTES_RSI_LENGTH):
                   return  self.CalculateAverage(lastNElems,MINUTES_RSI_LENGTH)
               elif (len(xOpenArr) > MINUTES_RSI_LENGTH):
                   return ( (prevSmoothOpen*(MINUTES_RSI_LENGTH-1))  + lastxOpen)/((MINUTES_RSI_LENGTH))
        else:
            return 0


    def Update(self,candleBarArr,MINUTES_RSI_LENGTH):

        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)), key=lambda x: x.DateTime, reverse=True)

        if len(sortedBars)>=2:

            if sortedBars[0].Close is None or sortedBars[1].Close is None:
                return

            if self.LastProcessedDateTime==sortedBars[0].DateTime:
                return #Already Processed

            self.UpOpen.append(sortedBars[0].Close - sortedBars[1].Close  if (sortedBars[0].Close >= sortedBars[1].Close) else 0)
            self.DownOpen.append( sortedBars[1].Close - sortedBars[0].Close if (sortedBars[0].Close < sortedBars[1].Close) else 0)

            #If RSI=14 --> MINUTES_RSI_LENGTH=15 --> So we have to send n-1
            self.SmoothUp.append(self.CalculatedUpDown(MINUTES_RSI_LENGTH-1,self.UpOpen,self.SmoothUp,self.Smoothed,"up"))
            self.SmoothDown.append(self.CalculatedUpDown(MINUTES_RSI_LENGTH - 1, self.DownOpen, self.SmoothDown, self.Smoothed, "down"))


            self.PrevRSI = self.RSI if self.RSI !=0 else None
            self.RSI= (100-(100/(1+(self.SmoothUp[-1]/self.SmoothDown[-1])))) if self.SmoothDown[-1]>0 else 0
            self.RSIArray.append(self.RSI)

            self.LastProcessedDateTime=sortedBars[0].DateTime
            #if(sortedBars[0].Security.Symbol=="SPY"):
            #    print("SPY-{}-final RSI{}:{} -- previous RSI{}:{}".format(self.LastProcessedDateTime,MINUTES_RSI_LENGTH,self.RSI,MINUTES_RSI_LENGTH,self.PrevRSI))




