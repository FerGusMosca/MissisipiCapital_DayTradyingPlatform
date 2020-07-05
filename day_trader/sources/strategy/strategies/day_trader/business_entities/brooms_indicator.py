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
        self.MSArray = []

        self.TPSL = None
        self.BSIMax = None
        self.BSIMin = None
        self.MSIMax = None
        self.MSIMin = None
        self.MSSlope = None

        self.BROOMS = None

        self.LastProcessedDateTime =None


    def CalculateTPSL(self,TP,BROOMS_NN):

        if BROOMS_NN.IntValue is None:
            raise Exception("Missing value for BROOMS_NN parameter")

        self.TPArray.append(TP)

        if(len(self.TPArray)>=BROOMS_NN.IntValue):

            #slope = self.GetSlope(self.TPArray[-1],self.TPArray[-1*BROOMS_NN.IntValue])
            slope=self.GetReggr(BROOMS_NN.IntValue,self.TPArray)

            self.TPSL = (slope * 100)/TP

    def CalculateBSIMaxMin(self,BSI,BROOMS_PP,BROOMS_QQ):

        if BROOMS_PP.IntValue is None:
            raise Exception("Missing value for BROOMS_PP parameter")

        if BROOMS_QQ.IntValue is None:
            raise Exception("Missing value for BROOMS_QQ parameter")

        self.BSIArray.append(BSI)

        if len(self.BSIArray)>=BROOMS_PP.IntValue:
            self.BSIMax = self.GetMaxInArray(self.BSIArray[-1 * BROOMS_PP.IntValue:])

        if len(self.BSIArray)>=BROOMS_QQ.IntValue:
            self.BSIMin = self.GetMinInArray(self.BSIArray[-1 * BROOMS_QQ.IntValue:])

    def CalculateMSIMinMax(self,MSI,BROOMS_RR,BROOMS_SS):

        if BROOMS_RR.IntValue is None:
            raise Exception("Missing value for BROOMS_RR parameter")

        if BROOMS_SS.IntValue is None:
            raise Exception("Missing value for BROOMS_SS parameter")

        self.MSIArray.append(MSI)

        if len( self.MSIArray)>=BROOMS_RR.IntValue:
            self.MSIMax=self.GetMaxInArray(self.MSIArray[-1*BROOMS_RR.IntValue:])

        if len( self.MSIArray)>=BROOMS_SS.IntValue:
            self.MSIMin=self.GetMinInArray(self.MSIArray[-1*BROOMS_SS.IntValue:])

    def CalculateMSSlope(self,MS,BROOMS_TT):

        if BROOMS_TT.IntValue is None:
            raise Exception("Missing value for BROOMS_TT parameter")

        if MS is None:
            return

        self.MSArray.append(MS)

        if len(self.MSArray)>=BROOMS_TT.IntValue:
            self.MSSlope = self.GetReggr(BROOMS_TT.IntValue,self.MSArray)


    def CalculateBROOMS(self,RSI,BSI,RSI30smSL,BROOMS_R,BROOMS_S,BROOMS_T,BROOMS_U,BROOMS_V,BROOMS_W,BROOMS_X,BROOMS_Y,BROOMS_Z,
                        BROOMS_CC,BROOMS_DD,BROOMS_EE,BROOMS_UU,BROOMS_VV,BROOMS_WW,BROOMS_XX):

        if (self.BSIMax is None or self.BSIMin is None or RSI is None or RSI30smSL is None or self.TPSL is None \
            or self.MSSlope is None or self.MSIMax is None or self.MSIMin is None or BSI is None ):
            return


        if self.BSIMax>BROOMS_DD.FloatValue:
            if (      self.BSIMax>BROOMS_R.FloatValue
                 and  self.MSIMax>BROOMS_T.FloatValue
                 and  RSI < BROOMS_V.FloatValue
                 and  RSI30smSL < BROOMS_X.FloatValue
                 and  self.TPSL < BROOMS_UU.FloatValue
                 and self.MSSlope < BROOMS_WW.FloatValue

                ):
                self.BROOMS = BROOMS_Z.FloatValue
            elif BSI > BROOMS_DD.FloatValue:
                self.BROOMS=BROOMS_DD.FloatValue
            else:
                self.BROOMS=BSI
        elif (self.BSIMin < BROOMS_EE.FloatValue):
            if (        self.BSIMin < BROOMS_S.FloatValue
                    and self.MSIMin < BROOMS_U.FloatValue
                    and RSI > BROOMS_W.FloatValue
                    and RSI30smSL > BROOMS_Y.FloatValue
                    and self.TPSL > BROOMS_VV.FloatValue
                    and self.MSSlope > BROOMS_XX.FloatValue

            ):
                self.BROOMS = BROOMS_CC.FloatValue
            elif BSI < BROOMS_EE.FloatValue:
                self.BROOMS = BROOMS_EE.FloatValue
            else:
                self.BROOMS = BSI
        else:
            self.BROOMS= BSI

    #endregion


    #region Public Methods



    def Update(self, candleBarArr,TP,BSI,MSI,RSI,MS,RSI30smSL,BROOMS_NN,BROOMS_PP,BROOMS_QQ,BROOMS_RR,BROOMS_SS,BROOMS_R,BROOMS_S,
               BROOMS_T,BROOMS_U,BROOMS_V,BROOMS_W,BROOMS_X,BROOMS_Y,BROOMS_Z,BROOMS_CC,BROOMS_DD,BROOMS_EE,BROOMS_TT,
               BROOMS_UU,BROOMS_VV,BROOMS_WW,BROOMS_XX):

        sortedBars = sorted(list(filter(lambda x: x is not None, candleBarArr)), key=lambda x: x.DateTime,
                            reverse=False)

        if (len(sortedBars) == 0):
            return

        candlebar = sortedBars[-1]

        if self.LastProcessedDateTime == candlebar.DateTime:
            return  # Already Processed

        self.CalculateTPSL(TP,BROOMS_NN)

        self.CalculateBSIMaxMin(BSI,BROOMS_PP,BROOMS_QQ)

        self.CalculateMSIMinMax(MSI,BROOMS_RR,BROOMS_SS)

        self.CalculateMSSlope(MS,BROOMS_TT)

        self.CalculateBROOMS(RSI,BSI,RSI30smSL,BROOMS_R,BROOMS_S,BROOMS_T,BROOMS_U,BROOMS_V,BROOMS_W,BROOMS_X,BROOMS_Y,
                             BROOMS_Z,BROOMS_CC,BROOMS_DD,BROOMS_EE,BROOMS_UU,BROOMS_VV,BROOMS_WW,BROOMS_XX)

        self.LastProcessedDateTime = candlebar.DateTime


    #endregion