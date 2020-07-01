from sources.framework.business_entities.market_data.candle_bar import *
import statistics

class MSStrengthIndicator():
    def __init__(self):
        self.Reset()

    # region Private Methods

    def Reset(self):
        self.TPSD=None
        self.MSI=None

        self.LastProcessedDateTime = None


    def CalculateTPSD(self,candleBarArr,BROOMS_TPSD_B):

        if BROOMS_TPSD_B.IntValue is None:
            raise Exception("Missing value for BROOMS_TPSD_B parameter")

        if len(candleBarArr)<BROOMS_TPSD_B.IntValue:
            return

        candlesToConsider = candleBarArr[-1*BROOMS_TPSD_B.IntValue:]

        prices = []

        for candle in candlesToConsider:
            prices.append(candle.Close)

        self.TPSD = statistics.stdev(prices)


    def CalculateMSI(self,MS,BROOMS_MS_STRENGTH_M,BROOMS_MS_STRENGTH_N,BROOMS_MS_STRENGTH_P,BROOMS_MS_STRENGTH_Q):

        if BROOMS_MS_STRENGTH_M.FloatValue is None:
            raise Exception("Missing value for BROOMS_MS_STRENGTH_M parameter")

        if BROOMS_MS_STRENGTH_N.FloatValue is None:
            raise Exception("Missing value for BROOMS_MS_STRENGTH_N parameter")

        if BROOMS_MS_STRENGTH_P.FloatValue is None:
            raise Exception("Missing value for BROOMS_MS_STRENGTH_P parameter")

        if BROOMS_MS_STRENGTH_Q.FloatValue is None:
            raise Exception("Missing value for BROOMS_MS_STRENGTH_Q parameter")

        if MS is None or self.TPSD is None:
            return

        M=BROOMS_MS_STRENGTH_M.FloatValue
        N=BROOMS_MS_STRENGTH_N.FloatValue
        P=BROOMS_MS_STRENGTH_P.FloatValue
        Q=BROOMS_MS_STRENGTH_Q.FloatValue

        self.MSI=((M - N ) /(self.TPSD * (P + Q)) )* (MS - (self.TPSD * P )) + M


    #endregion


    #region Public Methods

    def Update(self, candleBarArr,MS,BROOMS_TPSD_B,BROOMS_MS_STRENGTH_M,BROOMS_MS_STRENGTH_N,BROOMS_MS_STRENGTH_P,BROOMS_MS_STRENGTH_Q):

        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)), key=lambda x: x.DateTime,
                            reverse=False)

        if (len(sortedBars) == 0):
            return

        candlebar = sortedBars[-1]

        if self.LastProcessedDateTime == candlebar.DateTime:
            return  # Already Processed

        self.CalculateTPSD(sortedBars,BROOMS_TPSD_B)
        self.CalculateMSI(MS,BROOMS_MS_STRENGTH_M,BROOMS_MS_STRENGTH_N,BROOMS_MS_STRENGTH_P,BROOMS_MS_STRENGTH_Q)

        self.LastProcessedDateTime = candlebar.DateTime


    #endregion
