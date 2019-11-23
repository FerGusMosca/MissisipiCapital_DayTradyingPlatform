import pymssql
from sources.framework.business_entities.securities.security import *
from sources.strategy.strategies.day_trader.business_entities.day_trading_position import *


_CS_SEC_TYPE = "Equity"

class DayTradingPositionManager():

    #region Constructors

    def __init__(self, host, port, database, user, password):
        self.ConnParams = {}

        self.ConnParams["host"] = host
        self.ConnParams["port"] = port
        self.ConnParams["database"] = database
        self.ConnParams["user"] = user
        self.ConnParams["password"] = password
        self.i = 0
        self.connection = pymssql.connect(server=host, user=user, password=password, database=database)
    #endregion

    #region Private Methods

    def GetSecurityTypeFromStrSecType(self,strSecType):

        if strSecType==_CS_SEC_TYPE:
            return SecurityType.CS
        else:
            raise Exception("Unknown security type {0}".format(strSecType))

    def BuildSecurity(self,row):
        return Security(Symbol=row['symbol'],
                        Exchange=row['exchange'],
                        SecType=self.GetSecurityTypeFromStrSecType(row['security_type'])
                       )

    def BuildSecurityToTrade(self, row,security):
        return DayTradingPosition(
            id=int(row['id']),
            security=security,
            shares=int(row['shares_quantity']),
            active=bool(row['active']),
            open=bool(row['open']),
            routing=bool(row['routing']),
            longSignal=bool(row['long_signal']),
            shortSignal=bool(row['short_signal']),
            signalType=str(row['signal_type'])  if row['signal_type'] is not None else None ,
            signalDesc=str(row['signal_desc']) if row['signal_desc'] is not None else None,

        )

    #endregion

    #region Public Methods

    def PersistDayTradingPosition(self, dayTradingPosition):

        with self.connection.cursor(as_dict=True) as cursor:
            params = (dayTradingPosition.Id, dayTradingPosition.Security.Symbol,
                      int(dayTradingPosition.SharesQuantity),
                      bool(dayTradingPosition.Active),
                      bool(dayTradingPosition.Routing),
                      bool(dayTradingPosition.Open),
                      bool(dayTradingPosition.LongSignal),
                      bool(dayTradingPosition.ShortSignal),
                      dayTradingPosition.SignalType if not None else None,
                      dayTradingPosition.SignalDesc if not None else None)
            cursor.callproc("PersistDayTradingPosition", params)
            self.connection.commit()

    def GetDayTradingPositions(self):
        datTradingPositions=[]
        with self.connection.cursor(as_dict=True) as cursor:
            params = (True,)
            cursor.callproc("GetDayTradingPositions", params)

            for row in cursor:
                sec = self.BuildSecurity(row)
                dayTradingPos = self.BuildSecurityToTrade(row,sec)
                datTradingPositions.append(dayTradingPos)

        return datTradingPositions

    #endregion


