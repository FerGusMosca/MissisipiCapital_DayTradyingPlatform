from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.position_list_field import *


class PositionListWrapper(Wrapper):
    def __init__(self, pPositions, pException=None):
        self.Positions = pPositions
        self.Exception=pException

    def GetAction(self):
        return Actions.POSITION_LIST

    def GetField(self, field):

        if field is None:
            return None

        if field == PositionListField.Positions:
            return self.Positions
        elif field == PositionListField.Status:
            return self.Exception is None
        elif field == PositionListField.Error:
            return self.Exception
        else:
            return None

