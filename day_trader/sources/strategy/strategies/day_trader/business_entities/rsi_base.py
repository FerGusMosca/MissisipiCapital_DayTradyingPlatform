from scipy import stats
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


    def GetMaxInArray(self,array):

        max=None
        for val in array:
            if max is None or val > max:
                max = val

        return max

    def GetMinInArray(self, array):

        min=None
        for val in array:
            if min is None or val < min:
                min = val

        return min

    def GetReggr(self,index,array):
        arrayIndex = []
        arrayToUse= []

        if len(array)<index:
            return None

        i = index
        for val in array[-1 * index:]:
            arrayToUse.append(val)
            arrayIndex.append(len(array) - i)
            i -= 1

        reggr = stats.linregress(arrayIndex, arrayToUse)
        return reggr.slope


    #endregion
