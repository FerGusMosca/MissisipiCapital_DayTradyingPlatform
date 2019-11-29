import pymssql
from sources.strategy.strategies.day_trader.business_entities.model_parameter import *

class ModelParametersManager():

    # region Constructors
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

    def BuildModelParameter(self,row):
        modParam = ModelParameter(key=row["key"],
                                  symbol=row["symbol"],
                                  stringValue=row["string_value"],
                                  intValue=int(row["int_value"]) if row["int_value"] is not None else None,
                                  floatValue=float(row['float_value']) if row["float_value"] is not None else None
                                  )
        return modParam

    #endregion

    #region Public Methods

    def PersistModelParameter(self, modelPrameter):
        with self.connection.cursor(as_dict=True) as cursor:
            params = (modelPrameter.Key,modelPrameter.Symbol,modelPrameter.StringValue,modelPrameter.IntValue,
                      modelPrameter.FloatValue)
            cursor.callproc("PersistModelParameter", params)
            self.connection.commit()

    def GetModelParametersManager(self):
        modelParameters=[]
        with self.connection.cursor(as_dict=True) as cursor:
            params = ()
            cursor.callproc("GetModelParameters", params)

            for row in cursor:
                modelParameters.append(self.BuildModelParameter(row))

        return modelParameters

    #endregion