from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.strategy.strategies.day_trader.common.enums.fields.model_param_field import *

from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.PositionsStatus import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


class ModelParamReqWrapper(Wrapper):
    def __init__(self,modelParamReq):
        self.ModelParamReq=modelParamReq

    #region Public Methods

    def GetAction(self):
        return Actions.MODEL_PARAM_REQUEST

    def GetField(self, field):
        if field == ModelParamField.Symbol:
            return self.ModelParamReq.Symbol
        elif field == ModelParamField.Key:
            return self.ModelParamReq.Key
        else:
            return None

    #endregion
