from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.strategy.strategies.day_trader.common.enums.fields.model_param_field import *

from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.PositionsStatus import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


class UpdateModelParamReqWrapper(Wrapper):
    def __init__(self,modelParamUpdReq):
        self.ModelParamUpdReq=modelParamUpdReq

    #region Public Methods

    def GetAction(self):
        return Actions.UPDATE_MODEL_PARAM_REQUEST

    def GetField(self, field):
        if field == ModelParamField.Symbol:
            return self.ModelParamUpdReq.Symbol
        elif field == ModelParamField.Key:
            return self.ModelParamUpdReq.Key
        elif field == ModelParamField.FloatValue:
            return self.ModelParamUpdReq.FloatValue
        elif field == ModelParamField.IntValue:
            return self.ModelParamUpdReq.IntValue
        elif field == ModelParamField.StringValue:
            return self.ModelParamUpdReq.StringValue
        else:
            return None

    #endregion
