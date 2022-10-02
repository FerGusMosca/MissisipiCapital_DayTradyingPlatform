from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.server.framework.common.enums.fields.position_field import *
from sources.server.framework.common.enums.SecurityType import *
from sources.server.framework.common.enums.PositionsStatus import *


class CancelAllPositionsWrapper(Wrapper):
    def __init__(self):
        pass

    #region Public Methods

    def GetAction(self):
        return Actions.CANCEL_ALL_POSITIONS

    def GetField(self, field):
        return None

    #endregion

