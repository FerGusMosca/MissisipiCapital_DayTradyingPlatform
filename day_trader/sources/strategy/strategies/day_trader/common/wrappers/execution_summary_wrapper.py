from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.summary_field import *


class ExecutionSummaryWrapper(Wrapper):
    def __init__(self, pExecutionSummary, pDayTradingPositionId):
        self.ExecutionSummary = pExecutionSummary
        self.DatyTradingPositionId = pDayTradingPositionId

    def GetAction(self):
        return Actions.EXECUTION_SUMMARY

    def GetField(self, field):
        if field is None:
            return None

        if field == SummaryFields.Summary:
            return self.ExecutionSummary
        elif field == SummaryFields.PositionId:
            return self.DatyTradingPositionId
        elif field == SummaryFields.Status:
            return True
        elif field == SummaryFields.Error:
            return None
        else:
            return None

