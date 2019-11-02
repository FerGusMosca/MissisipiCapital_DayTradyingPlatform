from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.execution_report_field import *
from sources.generic_orderrouter.market_order_router.common.wrappers.order_wrapper import *


class ExecutionReportWrapper():
    def __init__(self, pPosId, pWrapper):
        self.PosId = pPosId
        self.Wrapper = pWrapper

    def GetAction(self):
        """

        Returns:

        """
        return Actions.EXECUTION_REPORT

    def GetField(self, field):
        """

        Args:
            field ():

        Returns:

        """
        if field is None:
            return None

        if field == ExecutionReportField.PosId:
            return self.PosId
        else:
            return self.Wrapper.GetField(field)
