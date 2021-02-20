from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.strategy.strategies.day_trader.common.enums.fields.model_param_field import *

from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.PositionsStatus import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


class DeleteModelParamReqWrapper(Wrapper):
    def __init__(self,modelParamDelReq):
        self.ModelParamDelReq=modelParamDelReq

    #region Public Methods

    def GetAction(self):
        return Actions.DELETE_MODEL_PARAM_REQUEST

    def GetField(self, field):
        if field == ModelParamField.Symbol:
            return self.ModelParamDelReq.Symbol
        elif field == ModelParamField.Key:
            return self.ModelParamDelReq.Key
        else:
            return None

    #endregion
