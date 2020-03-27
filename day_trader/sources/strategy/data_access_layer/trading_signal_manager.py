import pyodbc
import datetime
from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *
from sources.strategy.strategies.day_trader.business_entities.model_parameter import *

_id = 0
_key = 1
_symbol =2
_string_value = 3
_int_value =4
_float_value =5

class TradingSignalManager():

    # region Constructors
    def __init__(self, connString):
        self.ConnParams = {}
        self.i = 0
        self.connection = pyodbc.connect(connString, autocommit=False)

    #endregion


    #region Public Methods


    def GetTradingSignal(self,datetime,symbol):
        tradingSignalId=None
        with self.connection.cursor() as cursor:
            params = (datetime,symbol)
            cursor.execute("{CALL GetTradingSignal (?,?)}", params)

            for row in cursor:
                tradingSignalId=row[0]

        return tradingSignalId

    def PersistTradingSignal(self, dayTradingPos,datetime,action,side,candlebar):
        with self.connection.cursor() as cursor:
            params = (datetime,dayTradingPos.Security.Symbol,action,side,dayTradingPos.Id,
                      dayTradingPos.GetNetOpenShares(),dayTradingPos.Routing,dayTradingPos.CurrentProfit,
                      dayTradingPos.CurrentProfitLastTrade,dayTradingPos.CurrentProfitMonetary,
                      dayTradingPos.CurrentProfitMonetaryLastTrade,dayTradingPos.IncreaseDecrease,
                      dayTradingPos.MaxProfit,dayTradingPos.MaxLoss,dayTradingPos.LastNDaysStdDev,
                      dayTradingPos.MinuteNonSmoothedRSIIndicator.RSI,candlebar.Close)
            cursor.execute("{CALL PersistTradingSignal (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)}", params)
            #self.connection.commit()

    def PersistSignalModelParameter(self, tradingSignalId ,modelParam):
        with self.connection.cursor() as cursor:
            params = (tradingSignalId,modelParam.Key,modelParam.Symbol,modelParam.StringValue,
                      modelParam.IntValue,modelParam.FloatValue)
            cursor.execute("{CALL PersistSignalModelParameter (?,?,?,?,?,?)}", params)
            #self.connection.commit()

    def PersistSignalStatisticalParameter(self, tradingSignalId ,param,value):
        with self.connection.cursor() as cursor:
            params = (tradingSignalId,param,value)
            cursor.execute("{CALL PersistSignalStatisticalParameter (?,?,?)}", params)
            #self.connection.commit()

    def PersistSignalOtherParameter(self, tradingSignalId ,param,value):
        with self.connection.cursor() as cursor:
            params = (tradingSignalId,param,value)
            cursor.execute("{CALL PersistSignalOtherParameter (?,?,?)}", params)
            #self.connection.commit()

    def Commit(self):
        self.connection.commit()



    #endregion