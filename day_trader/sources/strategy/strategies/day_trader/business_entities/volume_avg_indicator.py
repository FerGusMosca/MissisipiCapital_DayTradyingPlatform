import statistics

_L20_MINUTES=20
_L5_MINUTES=5

class VolumeAvgIndicator():


    def __init__(self):
        self.Reset()

    # region Private Methods

    def Reset(self):

        self.T1 = None
        self.T2 = None
        self.T3 = None

        self.L5V=None
        self.L20V=None
        self.CV=None

        self.VR1=None
        self.VR2= None
        self.VR3 = None

        self.RuleBroomsEnabled=None
        self.Rule4Enabled=None

        self.LastProcessedDateTime=None

    def CalculateNAverage(self,candleBarArr,count):
        candlesToConsider = candleBarArr[-1*count:]


        volumeArr= []
        if len(candlesToConsider)>=count:

            for candlebar in candlesToConsider:
                if (candlebar.Volume is not None):
                    volumeArr.append(candlebar.Volume)
                else:
                    return None

            return statistics.mean(volumeArr)

        else:
            return None

    def UpdateConfigParamters(self,VOLUME_INDICATOR_T1,VOLUME_INDICATOR_T2,VOLUME_INDICATOR_T3,VOLUME_INDICATOR_RULE_4,
               VOLUME_INDICATOR_RULE_BROOMS):
        self.Rule4Enabled = VOLUME_INDICATOR_RULE_4.IntValue
        self.RuleBroomsEnabled = VOLUME_INDICATOR_RULE_BROOMS.IntValue

        self.T1= VOLUME_INDICATOR_T1.FloatValue
        self.T2 = VOLUME_INDICATOR_T2.FloatValue
        self.T3 = VOLUME_INDICATOR_T3.FloatValue


    def CalculateIndicators(self,sortedBars):

        candlebar = sortedBars[-1]

        if candlebar.Volume == 0 or candlebar.Volume is None:
            return

        self.L5V = self.CalculateNAverage(sortedBars, _L5_MINUTES)
        self.L20V = self.CalculateNAverage(sortedBars, _L20_MINUTES)
        self.CV = candlebar.Volume

        self.VR1 = (self.CV / self.L5V) if (self.L5V is not None and self.CV is not None and self.L5V != 0) else None
        self.VR2 = (self.CV / self.L20V) if (self.L20V is not None and self.CV is not None and self.L20V !=0) else None
        self.VR3 = (self.L5V / self.L20V) if (self.L5V is not None and self.L20V is not None and self.L20V !=0) else None

    def EnoughData(self):
        return (self.VR1 is not None and self.VR2 is not None and self.VR3 is not None and self.T1 is not None
                and self.T2 is not None and self.T3 is not None)

    def ConditionActivated(self):

        if self.EnoughData():
            return self.VR1>=self.T1 and self.VR2 >=self.T2 and self.VR3 >= self.T3
        else:
            return True


    #endregion

    #region Public Methods
    def Update(self, candleBarArr,VOLUME_INDICATOR_T1,VOLUME_INDICATOR_T2,VOLUME_INDICATOR_T3,VOLUME_INDICATOR_RULE_4,
               VOLUME_INDICATOR_RULE_BROOMS):

        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)), key=lambda x: x.DateTime,
                            reverse=False)

        if (len(sortedBars) == 0):
            return

        candlebar = sortedBars[-1]

        if self.LastProcessedDateTime == candlebar.DateTime:
            return  # Already Processed

        self.UpdateConfigParamters(VOLUME_INDICATOR_T1,VOLUME_INDICATOR_T2,VOLUME_INDICATOR_T3,VOLUME_INDICATOR_RULE_4,
                                   VOLUME_INDICATOR_RULE_BROOMS)

        self.CalculateIndicators(sortedBars)


        self.LastProcessedDateTime = candlebar.DateTime


    def ValidateBroomsRule(self):

           if self.RuleBroomsEnabled>=1:
                if self.EnoughData():
                    return self.ConditionActivated()
                else:
                    return True

    def ValidateRule4(self):

           if self.Rule4Enabled>=1:
                if self.EnoughData():
                    return self.ConditionActivated()
                else:
                    return True


    def ValidateIfEnoughData(self):

        if self.EnoughData():
            return self.ConditionActivated()
        else:
            return True #if we don't have enough data, we just validate everything



    #endregion
