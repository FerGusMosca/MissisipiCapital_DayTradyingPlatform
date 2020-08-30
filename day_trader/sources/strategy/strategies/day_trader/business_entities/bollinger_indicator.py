from sources.framework.business_entities.market_data.candle_bar import *
import statistics

class BollingerIndicator():


    def __init__(self):
        self.Reset()

    # region Private Methods

    def Reset(self):
        self.TP=None
        self.TPMA= None
        self.TPSD = None
        self.BollUp=None
        self.BollDn=None
        self.BSI= None

        self.HalfBollUp = None #for MACD
        self.HalfBollDn = None #for MACD


        self.TPSDStartOfTrade = None

        self.LastProcessedDateTime =None

    def CalculateTP(self,candlebar):

        if (candlebar.Low is  None or candlebar.High is  None or candlebar.Close is  None):
            return

        self.TP = (candlebar.Low + candlebar.High + candlebar.Close) / 3

    def CalculateTPMA(self,candleBarArr,BROOMS_TPMA_A):

        if BROOMS_TPMA_A.IntValue is None:
            raise Exception("Missing value for BROOMS_TPMA_A parameter")

        if len(candleBarArr)<BROOMS_TPMA_A.IntValue:
            return

        candlesToConsider = candleBarArr[-1*BROOMS_TPMA_A.IntValue:]

        sum=0
        for candlebar in candlesToConsider:
            sum+=candlebar.Close

        self.TPMA = sum/BROOMS_TPMA_A.IntValue


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

    def CalculateBollUp(self,BROOMS_BOLLUP_C):

        if BROOMS_BOLLUP_C.FloatValue is None:
            raise Exception("Missing value for BROOMS_BOLLUP_C parameter")

        if self.TPMA is None or self.TPSD is None:
            return

        self.BollUp= self.TPMA + (BROOMS_BOLLUP_C.FloatValue*self.TPSD)

    def CalculateBollDn(self,BROOMS_BOLLDN_D):

        if BROOMS_BOLLDN_D.FloatValue is None:
            raise Exception("Missing value for BROOMS_BOLLDN_D parameter")

        if self.TPMA is None or self.TPSD is None:
            return

        self.BollDn= self.TPMA - (BROOMS_BOLLDN_D.FloatValue*self.TPSD)


    def CalculateDeltas(self,BROOMS_BOLLUP_CvHALF,BROOMS_BOLLDN_DvHALF):

        if BROOMS_BOLLUP_CvHALF.FloatValue is None:
            raise Exception("Missing value for BROOMS_BOLLUP_CvHALF parameter")

        if BROOMS_BOLLDN_DvHALF.FloatValue is None:
            raise Exception("Missing value for BROOMS_BOLLDN_DvHALF parameter")

        if self.TPMA is None or self.TPSD is None:
            return

        self.HalfBollUp= self.TPMA + (BROOMS_BOLLUP_CvHALF.FloatValue*self.TPSD)
        self.HalfBollDn=self.TPMA - (BROOMS_BOLLDN_DvHALF.FloatValue*self.TPSD)

    def CalculateBSI(self,BROOMS_BOLLINGER_K,BROOMS_BOLLINGER_L):

        if BROOMS_BOLLINGER_K.FloatValue is None:
            raise Exception("Missing value for BROOMS_BOLLINGER_K parameter")

        if BROOMS_BOLLINGER_L.FloatValue is None:
            raise Exception("Missing value for BROOMS_BOLLINGER_L parameter")

        if self.BollUp is None or self.BollDn is None  or self.TP is None:
            return

        if self.BollUp == self.BollDn :
            return

        K=float( BROOMS_BOLLINGER_K.FloatValue)
        L=float( BROOMS_BOLLINGER_L.FloatValue)


        self.BSI = ((K - L ) / (self.BollUp - self.BollDn) * (self.TP-self.BollUp) ) + K

    #endregion

    #region Public Methods

    def Update(self, candleBarArr, BROOMS_TPMA_A,BROOMS_TPSD_B,BROOMS_BOLLUP_C,BROOMS_BOLLDN_D,BROOMS_BOLLINGER_K,
               BROOMS_BOLLINGER_L,BROOMS_BOLLUP_CvHALF,BROOMS_BOLLDN_DvHALF):

        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)), key=lambda x: x.DateTime,
                            reverse=False)

        if(len(sortedBars)==0):
            return

        candlebar = sortedBars[-1]

        if self.LastProcessedDateTime == candlebar.DateTime:
            return  # Already Processed

        self.CalculateTP(candlebar)
        self.CalculateTPMA(sortedBars,BROOMS_TPMA_A)
        self.CalculateTPSD(sortedBars,BROOMS_TPSD_B)
        self.CalculateBollUp(BROOMS_BOLLUP_C)
        self.CalculateBollDn(BROOMS_BOLLDN_D)
        self.CalculateBSI(BROOMS_BOLLINGER_K,BROOMS_BOLLINGER_L)

        self.CalculateDeltas(BROOMS_BOLLUP_CvHALF,BROOMS_BOLLDN_DvHALF)

        self.LastProcessedDateTime=candlebar.DateTime

    def OnTradeSignal(self):
        self.TPSDStartOfTrade=self.TPSD


    def DeltaDN(self):

        if self.TP is not None and self.HalfBollDn is not None:
            return self.TP - self.HalfBollDn
        else:
            return None

    def DeltaUP(self):

        if self.TP is not None and self.HalfBollUp is not None:
            return self.TP - self.HalfBollUp
        else:
            return None


    #endregion