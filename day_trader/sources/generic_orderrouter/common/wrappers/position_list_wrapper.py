from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.position_list_field import *


class PositionListWrapper(Wrapper):
    def __init__(self, pPositions):
        self.Positions = pPositions

    def GetAction(self):
        """

        Returns:

        """
        return Actions.POSITION_LIST

    def GetField(self, field):
        """

        Args:
            field ():

        Returns:

        """
        if field is None:
            return None

        if field == PositionListField.Positions:
            return self.Positions
        else:
            return None

