from sources.framework.business_entities.market_data.candle_bar import *
import statistics

class LastSDDDaysOpenStdDevIndicator():


    def __init__(self):
        self.Reset()

    # region Private Methods

    def Reset(self):
        self.LastSDDDaysOpenStdDev=None


    #endregion



    #region Public Methods

    def UpdateOnHistoricalData(self,marketDataArr,sddDaysModelParam):

        if sddDaysModelParam is not None:

            sortedMDArr = sorted(list(filter(lambda x: x.OpeningPrice is not None, marketDataArr.values())),
                                 key=lambda x: x.MDEntryDate,
                                 reverse=True)[:sddDaysModelParam.IntValue]

            openingPrices = []

            for md in sortedMDArr:
                openingPrices.append(md.OpeningPrice)

            self.LastSDDDaysOpenStdDev = statistics.stdev(openingPrices)

        else:
            self.LastSDDDaysOpenStdDev = None


    def PreloadForBacktest(self,preloadedParamDict,histPricesSDDOpenStdDevParam,candelBarDict,date,index):


        if histPricesSDDOpenStdDevParam.IntValue is None:
            raise Exception("Missing HISTORICAL_PRICES_SDD_OPEN_STD_DEV loaded to process LastSDDDaysOpenStdDevIndicator indicator")

        histPricesSDDOpenStdDevCount = histPricesSDDOpenStdDevParam.IntValue

        #A- <Preload> - The first <DDOpenStdDevCount> we have to load the parameters from the preloadedParamDict
        if index<=histPricesSDDOpenStdDevCount:
            if index in preloadedParamDict:
                self.LastSDDDaysOpenStdDev=preloadedParamDict[index]
            else:
                self.LastSDDDaysOpenStdDev=0
        else:
            #B - <Calculation> - We calculate the standard deveiation from the last <SDDOpenStdDevCount> opening candles
            #we have to calculate this from the previous opening prices

            canldeBarArraArr =list(filter(lambda x: x is not None,candelBarDict.values()))

            openingPrices = []

            #we consider prices up to this day
            candlesToConsiderArrArr = canldeBarArraArr[0:index]

            #then we take the last 21 <HISTORICAL_PRICES_SDD_OPEN_STD_DEV> last days
            candlesToEvaluateArrArr=candlesToConsiderArrArr[-1*histPricesSDDOpenStdDevCount:]

            for candlebarArr in candlesToEvaluateArrArr:
                if len (candlebarArr)>0:
                    openingPrices.append(candlebarArr[0].Open)
                else:
                     raise Exception("Received empty candle bar array for date {}".format(date))


            self.LastSDDDaysOpenStdDev = statistics.stdev(openingPrices)


    #endregion