from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.summary_list_fields import *


class ExecutionSummaryListWrapper(Wrapper):
    def __init__(self, pDayTradingPosition,pError=None):
        self.DatyTradingPosition = pDayTradingPosition
        self.Status= pError is None
        self.Error=pError

    def GetAction(self):
        return Actions.EXECUTION_SUMMARIES_LIST

    def GetField(self, field):
        if field is None:
            return None

        if field == SummaryListFields.Status:
            return self.Status
        elif field == SummaryListFields.PositionId:
            return self.DatyTradingPosition.Id
        elif field == SummaryListFields.Summaries:
            #return self.DatyTradingPosition.ExecutionSummaries.values()
            return self.DatyTradingPosition.GetAceptedSummaries()
        elif field == SummaryListFields.Error:
            return self.Error
        else:
            return None

