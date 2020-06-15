
class RSIBase():


    def __init__(self):
        pass

    #region Protected Methods

    def Reset(self):
        self.RSI = 0
        self.PrevRSI = None
        self.RSIArray = []
        self.LastProcessedDateTime = None

    def GetSlope(self, currValue, prevValue):

        if currValue is not None and prevValue is not None and prevValue != 0:
            return (currValue - prevValue) / prevValue
        else:
            return None

    def CalculateAverage(self,array,length):
        sum=0
        # Just the average
        for value in array:
            sum += value
        return sum / length


    def GetRSISlope (self,index):

        if len(self.RSIArray)>=index:
            lastRSIIndex = self.RSIArray[-1*index]
            return self.GetSlope(self.RSI,lastRSIIndex)
        else:
            return None


    #endregion
