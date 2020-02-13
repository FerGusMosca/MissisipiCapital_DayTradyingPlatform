from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.strategy.strategies.day_trader.common.enums.fields.model_param_field import *


class CreateModelParamReqWrapper(Wrapper):
    def __init__(self,modelParamCreateReq):
        self.ModelParamCreateReq=modelParamCreateReq

    #region Public Methods

    def GetAction(self):
        return Actions.CREATE_MODEL_PARAM_REQUEST

    def GetField(self, field):
        if field == ModelParamField.Symbol:
            return self.ModelParamCreateReq.Symbol
        elif field == ModelParamField.Key:
            return self.ModelParamCreateReq.Key
        elif field == ModelParamField.FloatValue:
            return self.ModelParamCreateReq.FloatValue
        elif field == ModelParamField.IntValue:
            return self.ModelParamCreateReq.IntValue
        elif field == ModelParamField.StringValue:
            return self.ModelParamCreateReq.StringValue
        else:
            return None

    #endregion
