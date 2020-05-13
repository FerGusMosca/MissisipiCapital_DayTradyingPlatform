from sources.framework.business_entities.market_data.candle_bar import *
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
    def DAILY_BIAS_FIELD():
        return "DAILY_BIAS"

    @staticmethod
    def TIME_FORMAT():
        return "%H:%M:%S"

    @staticmethod
    def DATE_FORMAT():
        return "%m/%d/%y"

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
            if columns[x]!="":
                modelParamDict[columns[x]]=0

        return modelParamDict

    @staticmethod
    def ExtractModelParametersValues(cls,columns,startIndex,modelParamDict):

        i=startIndex
        for key in modelParamDict:
            modelParamDict[key]=columns[i]
            i+=1

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
    def BuildCandlebar(cls,datetime,date,time,price):
        sec = Security(Symbol="")

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
    def ExtractMarketDataStructure(cls,file):

        candleBarDict = {}

        modelParamDict = {}

        with open(file, newline='') as f:
            reader = csv.reader(f)
            i=0
            timeDict={}
            for row in reader:

                if i==0:
                    timeDict = InputFileConverter.ExtractTimes(cls,row)
                    modelParamDict=InputFileConverter.ExtractModelParametersKeys(cls,row,len(timeDict)+1)

                else:
                    pricesDict = InputFileConverter.ExtractPrices(cls,row, timeDict)
                    date = InputFileConverter.ExtractDate(cls,row)

                    for index in timeDict:
                        dateTime = InputFileConverter.ConcatDateTime(cls,date,timeDict[index])
                        candlebar = InputFileConverter.BuildCandlebar(cls,dateTime,date,time,pricesDict[index])

                        if date not in candleBarDict:
                            candleBarDict[date]=[]
                        candleBarDict[date].append(candlebar)


                    if i==1:
                        InputFileConverter.ExtractModelParametersValues(cls,row,len(timeDict)+1,modelParamDict)
                i+=1

        respDto = StrategyBacktestDto(pSecurity=Security(Symbol=file),pCandleBarDict=candleBarDict,pParamDict=modelParamDict)

        return respDto