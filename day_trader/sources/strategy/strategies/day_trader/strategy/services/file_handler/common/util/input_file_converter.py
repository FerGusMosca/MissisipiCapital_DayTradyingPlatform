from sources.framework.business_entities.market_data.candle_bar import *
from sources.framework.business_entities.market_data.market_data import *
from sources.framework.business_entities.securities.security import *
from sources.strategy.strategies.day_trader.strategy.services.file_handler.common.dto.strategy_backtest_dto import *
import csv
import time
import datetime

class InputFileConverter:

    def __init__(self):
        pass

    #region Static Consts

    @staticmethod
    def DATE_FIELD():
        return "Date"

    @staticmethod
    def SYMBOL_FIELD():
        return "Symbol"

    @staticmethod
    def DEFAULT_SYMBOL():
        return "SPY"

    @staticmethod
    def DAILY_BIAS_FIELD():
        return "DAILY_BIAS"

    @staticmethod
    def TIME_FORMAT():
        return "%H:%M:%S"

    @staticmethod
    def DATE_FORMAT():
        return "%m/%d/%y"

    def DAILY_BIAS_FIELD():
        return "DAILY_BIAS"

    #endregion

    @staticmethod
    def ExtractTimes(cls,columns):

        timeDict = {}
        j=0
        for col in columns:
            if col!=InputFileConverter.DATE_FIELD() and col!=InputFileConverter.DAILY_BIAS_FIELD():
                mTime = time.strptime(col, InputFileConverter.TIME_FORMAT())
                timeDict[j]=mTime

            if col==InputFileConverter.DAILY_BIAS_FIELD():
                break

            j+=1

        return timeDict

    @staticmethod
    def ExtractModelParametersKeys(cls,columns,startIndex):
        modelParamDict={}

        for x in range (startIndex,len(columns)):
            if columns[x]!="" :
                modelParamDict[columns[x]]=0

        #No we append custom keys


        return modelParamDict

    @staticmethod
    def ExtractModelParametersValues(cls,columns,startIndex,modelParamDict):

        i=startIndex
        toDel=[]
        for key in modelParamDict:
            if key!=InputFileConverter.SYMBOL_FIELD():
                modelParamDict[key]=columns[i]
            else:
                toDel.append(key)
            i+=1

        for key in toDel:
            del modelParamDict[key]

    @staticmethod
    def ExtractPrices(cls,columns,timeDict):
        j = 0
        pricesDict = {}
        for col in columns:
            if j== 0 :
                pass #we just ignore the date
            else:

                if len(timeDict)>=j and timeDict[j] is not None:
                    pricesDict[j]=float(col)

            j += 1

        return pricesDict

    @staticmethod
    def ExtractDate(cls,columns):
        j = 0

        date=None
        for col in columns:
            if j == 0:
                date=time.strptime(col, InputFileConverter.DATE_FORMAT())
            else:
                break

            j += 1

        return date

    @staticmethod
    def ConcatDateTime(cls,date,time):
        now = datetime.datetime.now()
        return now.replace(year=date.tm_year,month=date.tm_mon,day=date.tm_mday,hour=time.tm_hour, minute=time.tm_min, second=time.tm_sec, microsecond=0)

    @staticmethod
    def GetSymbol(modelParamDict):
        if InputFileConverter.SYMBOL_FIELD() in modelParamDict:
            return modelParamDict[InputFileConverter.SYMBOL_FIELD()]
        else:
            return InputFileConverter.DEFAULT_SYMBOL()

    @staticmethod
    def BuildCandlebar(symbol,datetime,date,time,price):
        sec = Security(Symbol=symbol)

        candlebar = CandleBar(pSecurity=sec)
        candlebar.Time=time
        candlebar.DateTime=datetime
        candlebar.Timestamp=datetime
        candlebar.High=price
        candlebar.Open=price
        candlebar.Low=price
        candlebar.Close=price

        return candlebar

    @staticmethod
    def BuildMarketData(symbol,datetime,date,time,price):
        sec = Security(Symbol=symbol)

        md = MarketData()
        md.Security=sec
        md.OpeningPrice=price
        md.ClosingPrice = price
        md.TradingSessionHighPrice=price
        md.TradingSessionLowPrice=price
        md.Trade=price
        md.MDEntryDate=datetime
        md.MDLocalEntryDate=datetime
        md.Timestamp=datetime
        md.StdDev=0

        return md


    @staticmethod
    def ExtractMarketDataStructure(cls,file):

        candleBarDict = {}
        marketDataDict = {}
        modelParamDict = {}

        symbol = InputFileConverter.DEFAULT_SYMBOL()
        referenceDate = None

        with open(file, newline='') as f:
            reader = csv.reader(f)
            i=0
            timeDict={}
            for row in reader:

                if i==0:
                    timeDict = InputFileConverter.ExtractTimes(cls,row)
                    modelParamDict=InputFileConverter.ExtractModelParametersKeys(cls,row,len(timeDict)+1)

                else:

                    if i==1:
                        InputFileConverter.ExtractModelParametersValues(cls,row,len(timeDict)+1,modelParamDict)
                        symbol=InputFileConverter.GetSymbol(modelParamDict)

                    pricesDict = InputFileConverter.ExtractPrices(cls,row, timeDict)
                    date = InputFileConverter.ExtractDate(cls,row)

                    for index in timeDict:
                        dateTime = InputFileConverter.ConcatDateTime(cls,date,timeDict[index])
                        referenceDate = dateTime if referenceDate is None else referenceDate

                        candlebar = InputFileConverter.BuildCandlebar(symbol,dateTime,date,time,pricesDict[index])
                        md = InputFileConverter.BuildMarketData(symbol, dateTime, date, time, pricesDict[index])

                        if date not in candleBarDict:
                            candleBarDict[date]=[]

                        if date not in marketDataDict:
                            marketDataDict[date]=[]

                        candleBarDict[date].append(candlebar)
                        marketDataDict[date].append(md)



                i+=1

        respDto = StrategyBacktestDto(pReferenceDate=referenceDate,pSecurity=Security(Symbol=symbol),pCandleBarDict=candleBarDict,
                                      pMarketDataDict=marketDataDict,pParamDict=modelParamDict)

        return respDto