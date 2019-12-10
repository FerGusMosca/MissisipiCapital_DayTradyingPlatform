from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.strategy.strategies.day_trader.common.enums.fields.model_param_field import *

from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.PositionsStatus import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


class ModelParameterWrapper(Wrapper):
    def __init__(self,modelParam):
        self.ModelParam=modelParam

    #region Public Methods

    def GetAction(self):
        return Actions.MODEL_PARAM

    def GetField(self, field):
        if field == ModelParamField.Symbol:
            return self.ModelParam.Symbol
        elif field == ModelParamField.Key:
            return self.ModelParam.Key
        elif field == ModelParamField.IntValue:
            return self.ModelParam.IntValue
        elif field == ModelParamField.StringValue:
            return self.ModelParam.StringValue
        elif field == ModelParamField.FloatValue:
            return self.ModelParam.FloatValue
        else:
            return None

    #endregion
