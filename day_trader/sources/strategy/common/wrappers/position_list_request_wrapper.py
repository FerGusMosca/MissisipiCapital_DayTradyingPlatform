from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.position_field import *


class PositionListRequestWrapper(Wrapper):
    def __init__(self):
        pass


    def GetAction(self):
        """ See Wrapper class.

        Returns:

        """
        return Actions.POSITION_LIST_REQUEST

    def GetField(self, field):
        """ See Wrapper class.

        Args:
            field ():
        """
        pass