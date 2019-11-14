from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.portfolio_positions_list_field import *


class PortfolioPositionListWrapper(Wrapper):
    def __init__(self, pPortfolioPositions,pSuccess=True,pError=None):
        self.PortfolioPositions = pPortfolioPositions
        self.Success=pSuccess
        self.Error=pError

    def GetAction(self):
        return Actions.PORTFOLIO_POSITIONS

    def GetField(self, field):
        if field is None:
            return None

        if field == PortfolioPositionListFields.PortfolioPositions:
            return self.PortfolioPositions
        elif field == PortfolioPositionListFields.Status:
            return self.Success
        elif field == PortfolioPositionListFields.Error:
            return self.Error
        else:
            return None

