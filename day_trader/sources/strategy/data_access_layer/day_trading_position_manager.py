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
        return DayTradingPosition(id=row['id'],security=security,shares=row['shares_quantity'],active=True)

    #endregion

    #region Public Methods

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


