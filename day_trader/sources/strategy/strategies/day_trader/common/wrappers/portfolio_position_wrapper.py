from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.portfolio_position_field import *


class PortfolioPositionWrapper(Wrapper):
    def __init__(self, pDayTradingPosition):
        self.DayTradingPositionsition = pDayTradingPosition

    def GetAction(self):
        return Actions.PORTFOLIO_POSITION

    def GetField(self, field):
        if field is None:
            return None

        if field == PortfolioPositionFields.PortfolioPosition:
            return self.DayTradingPositionsition
        else:
            return None

