import pyodbc
from sources.strategy.strategies.day_trader.business_entities.model_parameter import *

_id = 0
_key = 1
_symbol =2
_string_value = 3
_int_value =4
_float_value =5

class ModelParametersManager():

    # region Constructors
    def __init__(self, connString):
        self.ConnParams = {}
        self.i = 0
        self.connection = pyodbc.connect(connString)

    #endregion

    #region Private Methods

    def BuildModelParameter(self,row):
        modParam = ModelParameter(key=row[_key],
                                  symbol=row[_symbol],
                                  stringValue=row[_string_value],
                                  intValue=int(row[_int_value]) if row[_int_value] is not None else None,
                                  floatValue=float(row[_float_value]) if row[_float_value] is not None else None
                                  )
        return modParam

    #endregion

    #region Public Methods

    def PersistModelParameter(self, modelPrameter):
        with self.connection.cursor() as cursor:
            params = (modelPrameter.Key,
                      modelPrameter.Symbol if modelPrameter.Symbol is not None and modelPrameter.Symbol !="*" else None,
                      modelPrameter.StringValue,
                      modelPrameter.IntValue,
                      modelPrameter.FloatValue)
            cursor.execute("{CALL PersistModelParameter (?,?,?,?,?)}", params)
            self.connection.commit()

    def GetModelParametersManager(self):
        modelParameters=[]
        with self.connection.cursor() as cursor:
            params = ()

            cursor.execute("{CALL GetModelParameters }", params)

            for row in cursor:
                modelParameters.append(self.BuildModelParameter(row))

        return modelParameters

    #endregion