from sources.framework.business_entities.market_data.candle_bar import *
from sources.strategy.strategies.day_trader.business_entities.rsi_base import *

class BroomsIndicator(RSIBase):


    def __init__(self):
        self.Reset()

    # region Private Methods

    def Reset(self):

        self.TPArray = []
        self.BSIArray = []
        self.MSIArray = []

        self.TPSL = None
        self.BSIMax = None
        self.BSIMin = None
        self.MSIMax = None
        self.MSIMin = None

        self.BROOMS = None


    def CalculateTPSL(self,TP,BROOMS_NN):

        if BROOMS_NN.IntValue is None:
            raise Exception("Missing value for BROOMS_NN parameter")

        self.TPArray.append(TP)

        if(len(self.TPArray)>=BROOMS_NN.IntValue):

            slope = self.GetSlope(self.TPArray[-1],self.TPArray[-1*BROOMS_NN.IntValue])

            self.TPSL = (slope * 100)/TP

    def CalculateBSIMax(self,BSI,BROOMS_PP):

        if BROOMS_PP.IntValue is None:
            raise Exception("Missing value for BROOMS_PP parameter")

        self.BSIArray.append(BSI)
        self.BSIMax=self.GetMaxInArray(self.BSIArray[-1*BROOMS_PP.IntValue])


    def CalculateBSIMin(self,BSI,BROOMS_QQ):

        if BROOMS_QQ.IntValue is None:
            raise Exception("Missing value for BROOMS_QQ parameter")

        self.BSIArray.append(BSI)
        self.BSIMin=self.GetMinInArray(self.BSIArray[-1*BROOMS_QQ.IntValue])


    def CalculateMSIMax(self,MSI,BROOMS_RR):

        if BROOMS_RR.IntValue is None:
            raise Exception("Missing value for BROOMS_RR parameter")

        self.MSIArray.append(MSI)
        self.MSIMax=self.GetMaxInArray(self.MSIArray[-1*BROOMS_RR.IntValue])

    def CalculateMSIMin(self, MSI, BROOMS_SS):

        if BROOMS_SS.IntValue is None:
            raise Exception("Missing value for BROOMS_SS parameter")

        self.MSIArray.append(MSI)
        self.MSIMin = self.GetMinInArray(self.MSIArray[-1 * BROOMS_SS.IntValue])


    def CalculateBROOMS(self,RSI,RSI30smSL,BROOMS_R,BROOMS_S,BROOMS_T,BROOMS_U,BROOMS_V,BROOMS_W,BROOMS_X,BROOMS_Y,BROOMS_Z,
                        BROOMS_CC,BROOMS_DD,BROOMS_EE,BROOMS_UU,BROOMS_VV,BROOMS_WW,BROOMS_XX):

        if self.BSIMax is None or RSI is None or RSI30smSL is None or self.TPSL is None:
            return


        if self.BSIMax>BROOMS_DD.FloatValue:
            if (      self.BSIMax>BROOMS_R.FloatVaue
                 and  self.MSIMax>BROOMS_T.FloatValue
                 and  RSI < BROOMS_V.FloatValue
                 and  RSI30smSL < BROOMS_X.FloatValue
                 and  self.TPSL < BROOMS_UU.FloatValue

                ):
                pass

    #endregion


    #region Public Methods



    def Update(self, candleBarArr,TP,BSI,MSI,RSI,RSI30smSL,BROOMS_NN,BROOMS_PP,BROOMS_QQ,BROOMS_RR,BROOMS_SS,BROOMS_R,BROOMS_S,
               BROOMS_T,BROOMS_U,BROOMS_V,BROOMS_W,BROOMS_X,BROOMS_Y,BROOMS_Z,BROOMS_CC,BROOMS_DD,BROOMS_EE,
               BROOMS_UU,BROOMS_VV,BROOMS_WW,BROOMS_XX):
        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)), key=lambda x: x.DateTime,
                            reverse=False)

        if (len(sortedBars) == 0):
            return

        candlebar = sortedBars[-1]

        if self.LastProcessedDateTime == candlebar.DateTime:
            return  # Already Processed

        self.CalculateTPSL(TP,BROOMS_NN)

        self.CalculateBSIMax(BSI,BROOMS_PP)

        self.CalculateBSIMin(BSI, BROOMS_QQ)

        self.CalculateMSIMax(MSI,BROOMS_RR)

        self.CalculateMSIMin(MSI,BROOMS_SS)

        self.CalculateBROOMS(RSI,RSI30smSL,BROOMS_R,BROOMS_S,BROOMS_T,BROOMS_U,BROOMS_V,BROOMS_W,BROOMS_X,BROOMS_Y,
                             BROOMS_Z,BROOMS_CC,BROOMS_DD,BROOMS_EE,BROOMS_UU,BROOMS_VV,BROOMS_WW,BROOMS_XX)

        self.LastProcessedDateTime = candlebar.DateTime


    #endregion