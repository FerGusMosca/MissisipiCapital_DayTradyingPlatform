from sources.strategy.strategies.day_trader.business_entities.rsi_indicator import *
from sources.framework.business_entities.market_data.candle_bar import *
from datetime import datetime

class RSIIndicatorTester():

    def __init__(self):
        pass


    def GetPrices(self):

        return [314.59,314.42,314.32,314.25,314.19,314.18,314.12,314.08,314.045,313.83,313.54,313.41,313.52,313.617,313.59,313.57,313.67,313.58,313.49,313.57,313.47,313.37,313.48,313.559,313.43,313.43,313.39,313.28,313.25,313.189,312.73,312.68,312.54,312.26,312.395,312.16,311.92,312.09,312.15,312.25,312.25,312.64,312.68,312.7,312.755,312.77,312.75,312.705,312.66,312.43,312.28,312.26,312.2,312.22,312.24,312,312.14,312.07,311.98,312.09,312.22,311.925,311.9,311.87,311.81,312.04,311.6,311.65,311.87,311.825,311.805,311.79,312.005,312.26,312.18,312.26,312.12,312.06,311.819,311.79,311.74,311.775,311.62,311.48,311.71,311.57,311.65,311.515,311.635,311.56,311.55,311.623,311.54,311.56,311.415,311.405,311.425,311.48,311.36,311.33]


    def RunRSITests(self, minSpan, smoothed):

        print("Starting to process RSI tests for span {} {}".format(minSpan,"Smoothed" if smoothed else "Non Smoothed",))

        prices=self.GetPrices()

        candleBarArr = []
        rsiSmoothed = RSIIndicator(smoothed=smoothed)
        date = datetime.strptime('10 Mar 2020', '%d %b %Y')

        hour=11
        minute=0

        for price in prices:
            candlebar = CandleBar(None)
            candlebar.DateTime =  date.replace(hour=hour, minute=minute)
            candlebar.Close=price

            candleBarArr.append(candlebar)

            rsiSmoothed.Update(candleBarArr,minSpan+1)

            print("RSI {} {}- DateTime={} Value={}".format(minSpan,
                                                           "Smoothed" if smoothed else "Non Smoothed",
                                                            candlebar.DateTime,
                                                            rsiSmoothed.RSI))

            if minute==59:
                minute=0
                hour+=1
            else:
                minute+=1


    def DoTest(self):

        self.RunRSITests(14,smoothed=False)

        self.RunRSITests(14,smoothed=True)
