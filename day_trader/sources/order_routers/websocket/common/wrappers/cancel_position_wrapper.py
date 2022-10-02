from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.position_field import *


class CancelPositionWrapper(Wrapper):
    def __init__(self,posId):
        self.PosId = posId

    #region Public Methods

    def GetAction(self):
        return Actions.CANCEL_POSITION

    def GetField(self, field):
        if field == PositionField.PosId:
            return self.PosId
        else:
            return None

    #endregion

