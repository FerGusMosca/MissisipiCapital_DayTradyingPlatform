from sources.strategy.strategies.day_trader.business_entities.macd_indicator_adjusted import *
from sources.framework.business_entities.market_data.candle_bar import *
from datetime import datetime

class MACDIndicatorAdjustedTester():

    def __init__(self):
        pass


    def GetPrices(self):

        # Original Example
        #return [314.59,314.42,314.32,314.25,314.19,314.18,314.12,314.08,314.045,313.83,313.54,313.41,313.52,313.617,313.59,313.57,313.67,313.58,313.49,313.57,313.47,313.37,313.48,313.559,313.43,313.43,313.39,313.28,313.25,313.189,312.73,312.68,312.54,312.26,312.395,312.16,311.92,312.09,312.15,312.25,312.25,312.64,312.68,312.7,312.755,312.77,312.75,312.705,312.66,312.43,312.28,312.26,312.2,312.22,312.24,312,312.14,312.07,311.98,312.09,312.22,311.925,311.9,311.87,311.81,312.04,311.6,311.65,311.87,311.825,311.805,311.79,312.005,312.26,312.18,312.26,312.12,312.06,311.819,311.79,311.74,311.775,311.62,311.48,311.71,311.57,311.65,311.515,311.635,311.56,311.55,311.623,311.54,311.56,311.415,311.405,311.425,311.48,311.36,311.33]

        # 23.03.20 example
        return [228.19, 226.1, 225.28, 227.17, 227.655, 227.04, 226.15, 225.76, 224.35, 223.13, 222.385, 223.44, 222.65,
                222.87, 224.047, 223.41, 223.45, 222.81, 224.085, 224.69, 224.54, 224.04, 225.608, 226.02, 225.565,
                225.55, 226.857, 226.96, 227.29, 227.269, 227.42, 227.3, 225.97, 225.7, 225.23, 225.8, 226.53, 226.39,
                227, 226.5, 226.77, 226.81, 227.47, 228.715, 228.22, 228.26, 227.93, 227.83, 227.32, 226.27, 225.605,
                225.529, 225.15, 225.83, 226.49, 226.72, 227.1, 225.97, 226.34, 226.96, 226.574, 226.04, 226.78, 226.53,
                226.38, 226.38, 226.41, 225.65, 224.78, 225.5, 225.98, 226.21, 226.17, 227.31, 227.158, 227, 226.03,
                225.86, 225.88, 225.76, 225.81, 225.64, 225.46, 225.521, 225.2, 224.59, 224.29, 224.12, 223.67, 223.83,
                223.52, 224.11, 223.49, 223.24, 223.31, 224.37, 224.09, 223.87, 223.59, 223.57]

    def RunMACDAdjustedTests(self):

        print("Starting to process MACDAdjusted tests ")

        prices=self.GetPrices()

        candleBarArr = []
        macdAdjInd = MACDIndicatorAdjusted(slow=26,fast=12,signal=9)
        date = datetime.strptime('10 Mar 2020', '%d %b %Y')

        hour=8
        minute=30

        for price in prices:
            candlebar = CandleBar(None)
            candlebar.DateTime =  date.replace(hour=hour, minute=minute)
            candlebar.Close=price

            candleBarArr.append(candlebar)

            macdAdjInd.Update(CandleBarArr= candleBarArr)

            print("MACDAdj  DateTime={} MACD={} Signal={} MS={} MSPrev={}".format(
                                                            candlebar.DateTime,
                                                            macdAdjInd.MACD,macdAdjInd.Signal,
                                                            macdAdjInd.MS,macdAdjInd.MSPrev))

            if minute==59:
                minute=0
                hour+=1
            else:
                minute+=1


    def DoTest(self):

        self.RunMACDAdjustedTests()

