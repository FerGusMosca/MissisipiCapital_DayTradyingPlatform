from sources.strategy.strategies.day_trader.business_entities.bollinger_indicator import *
from sources.strategy.strategies.day_trader.business_entities.MS_strength_indicator import *
from sources.strategy.strategies.day_trader.business_entities.macd_indicator_adjusted import *
from sources.strategy.strategies.day_trader.business_entities.brooms_indicator import *
from sources.strategy.strategies.day_trader.business_entities.rsi_indicator_smoothed import *
from sources.strategy.strategies.day_trader.business_entities.rsi_indicator import *
from sources.framework.business_entities.market_data.candle_bar import *
from sources.strategy.strategies.day_trader.common.util.model_parameters_handler import *
from datetime import datetime

class BroomsTester():

    def __init__(self,pModelParametersHandler):
        self.ModelParametersHandler=pModelParametersHandler

    def GetPrices(self):
        # Original Example @Bollinger
        # return [314.59,314.42,314.32,314.25,314.19,314.18,314.12,314.08,314.045,313.83,313.54,313.41,313.52,313.617,313.59,313.57,313.67,313.58,313.49,313.57,313.47,313.37,313.48,313.559,313.43,313.43,313.39,313.28,313.25,313.189,312.73,312.68,312.54,312.26,312.395,312.16,311.92,312.09,312.15,312.25,312.25,312.64,312.68,312.7,312.755,312.77,312.75,312.705,312.66,312.43,312.28,312.26,312.2,312.22,312.24,312,312.14,312.07,311.98,312.09,312.22,311.925,311.9,311.87,311.81,312.04,311.6,311.65,311.87,311.825,311.805,311.79,312.005,312.26,312.18,312.26,312.12,312.06,311.819,311.79,311.74,311.775,311.62,311.48,311.71,311.57,311.65,311.515,311.635,311.56,311.55,311.623,311.54,311.56,311.415,311.405,311.425,311.48,311.36,311.33]

        # 23.03.20 example
        return [228.19, 226.1, 225.28, 227.17, 227.655, 227.04, 226.15, 225.76, 224.35, 223.13, 222.385, 223.44, 222.65,
                222.87, 224.047, 223.41, 223.45, 222.81, 224.085, 224.69, 224.54, 224.04, 225.608, 226.02, 225.565,
                225.55, 226.857, 226.96, 227.29, 227.269, 227.42, 227.3, 225.97, 225.7, 225.23, 225.8, 226.53, 226.39,
                227, 226.5, 226.77, 226.81, 227.47, 228.715, 228.22, 228.26, 227.93, 227.83, 227.32, 226.27, 225.605,
                225.529, 225.15, 225.83, 226.49, 226.72, 227.1, 225.97, 226.34, 226.96, 226.574, 226.04, 226.78, 226.53,
                226.38, 226.38, 226.41, 225.65, 224.78, 225.5, 225.98, 226.21, 226.17, 227.31, 227.158, 227, 226.03,
                225.86, 225.88, 225.76, 225.81, 225.64, 225.46, 225.521, 225.2, 224.59, 224.29, 224.12, 223.67, 223.83,
                223.52, 224.11, 223.49, 223.24, 223.31, 224.37, 224.09, 223.87, 223.59, 223.57]

    def UpdateMACD(self,macdAdjInd,candleBarArr,slow,fast,signal):

        macdAdjInd.Update(CandleBarArr=candleBarArr, slow=slow, fast=fast, signal=signal)

    def UpdateBollinger(self,bollingerInd,candleBarArr):
        bollingerInd.Update(candleBarArr,
                            self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_TPMA_A()),
                            self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_TPSD_B()),
                            self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BOLLUP_C()),
                            self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BOLLDN_D()),
                            self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BOLLINGER_K()),
                            self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BOLLINGER_L())
                            )

        print("DateTime={} Bollinger--> TP ={}  TPMA={}  TPSD={}  BollUp={}  BollDn={}  BSI={}".format(
            candleBarArr[-1].DateTime, bollingerInd.TP, bollingerInd.TPMA, bollingerInd.TPSD, bollingerInd.BollUp
            , bollingerInd.BollDn, bollingerInd.BSI))

    def UpdateMSStrength(self,msStrengthInd,macdAdjInd,candleBarArr):
        msStrengthInd.Update(candleBarArr,
                             macdAdjInd.MS,
                             self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_TPSD_B()),
                             self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_MS_STRENGTH_M()),
                             self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_MS_STRENGTH_N()),
                             self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_MS_STRENGTH_P()),
                             self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_MS_STRENGTH_Q())
                             )

        print("DateTime={} MS-Strength--> TPSD={}  MSI={}".format(
            candleBarArr[-1].DateTime, msStrengthInd.TPSD, msStrengthInd.MSI))

    def UpdateRSI(self,rsiSmoothed,rsiNonSmoothed,candleBarArr):

        candlebar= candleBarArr[-1]

        rsiSmoothed.Update(candleBarArr, 30)
        rsiNonSmoothed.Update(candleBarArr,14)
        print("DateTime={} - RSI={} - RSI Smoothed 30 SL={}".format(candlebar.DateTime,rsiSmoothed.RSI,rsiSmoothed.GetRSISlope(30)))

    def UpdateBrooms(self,broomsInd,macdAdjInd,rsiSmoothed,rsiNonSmoothed,bollingerInd,msStrengthInd,candleBarArr):

        broomsInd.Update(candleBarArr,
                         bollingerInd.TP,
                         bollingerInd.BSI,
                         msStrengthInd.MSI,
                         rsiNonSmoothed.RSI,
                         macdAdjInd.MS,
                         rsiSmoothed.GetRSIReggr(30),  # RSI30smSL
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_NN()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_PP()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_QQ()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_RR()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_SS()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_R()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_S()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_T()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_U()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_V()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_W()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_X()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_Y()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_Z()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_CC()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_DD()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_EE()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_TT()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_UU()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_VV()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_WW()),
                         self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_XX()))

        print("DateTime={} Brooms--> TPSL ={}  BSIMax={}  BSIMin={}  MSIMax={}  MSIMin={}  MSSlope={}  BROOMS={}".format(
            candleBarArr[-1].DateTime, broomsInd.TPSL, broomsInd.BSIMax, broomsInd.BSIMin, broomsInd.MSIMax
            , broomsInd.MSIMin,broomsInd.MSSlope, broomsInd.BROOMS))



    def RunBroomsTests(self):

        fast = 10
        slow = 50
        signal = 50

        print("Starting to process Brooms tests".format())

        prices=self.GetPrices()

        candleBarArr = []
        macdAdjInd = MACDIndicatorAdjusted(slow=slow,fast=fast,signal=signal)
        rsiSmoothed = RSIIndicatorSmoothed()
        rsiNonSmoothed = RSIIndicator(False)
        bollingerInd = BollingerIndicator()
        msStrengthInd = MSStrengthIndicator()
        broomsInd = BroomsIndicator()

        date = datetime.strptime('23 Mar 2020', '%d %b %Y')

        hour=8
        minute=30

        for price in prices:
            candlebar = CandleBar(None)
            candlebar.DateTime =  date.replace(hour=hour, minute=minute)
            candlebar.Close=price
            candlebar.Low=price
            candlebar.High=price
            candlebar.Open=price

            candleBarArr.append(candlebar)

            self.UpdateMACD(macdAdjInd,candleBarArr,slow,fast,signal)
            self.UpdateRSI(rsiSmoothed,rsiNonSmoothed,candleBarArr)

            self.UpdateBollinger(bollingerInd,candleBarArr)

            self.UpdateMSStrength(msStrengthInd,macdAdjInd,candleBarArr)

            self.UpdateBrooms(broomsInd,macdAdjInd,rsiSmoothed,rsiNonSmoothed,bollingerInd,msStrengthInd,candleBarArr)


            if minute==59:
                minute=0
                hour+=1
            else:
                minute+=1


    def DoTest(self):

        #self.RunRSITests(14,smoothed=False)

        self.RunBroomsTests()