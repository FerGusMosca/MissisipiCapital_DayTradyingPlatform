from sources.framework.common.enums.Actions import *
from sources.framework.common.wrappers.wrapper import *
from sources.framework.common.converters.execution_report_converter import *
from sources.framework.common.enums.fields.execution_report_list_field import *
from sources.framework.business_entities.positions.position import *
from sources.framework.business_entities.securities.security import *
from sources.framework.business_entities.orders.order import *
import uuid


class ExecutionReportListConverter:

    @staticmethod
    def ValidateExecutionReportList(self, wrapper):
        if wrapper.GetField(ExecutionReportListField.ExecutionReports) is None:
            raise Exception(
                "Missing parameter {} for execution report list".format(ExecutionReportListField.ExecutionReports))

    @staticmethod
    def ValidateExecutionReport(self, execReport):
        if execReport.Order is None:
            raise Exception("Missing parameter {} for execution report ".format("Order"))

        if execReport.Order.Security is None:
            raise Exception("Missing parameter {} for execution report ".format("Order.Security"))

    @staticmethod
    def CreatePositionFromExecutionReport(self,execReportWrapper):

        exec_report = ExecutionReportConverter.ConvertExecutionReport(execReportWrapper)

        ExecutionReportListConverter.ValidateExecutionReport(self, exec_report)

        pos = Position(
            PosId=uuid.uuid4(),
            Security=Security(Symbol=exec_report.Order.Security.Symbol,
                              Currency=exec_report.Order.Security.Currency),
            Side=exec_report.Order.Side,
            PriceType=PriceType.FixedAmount,
            Qty=exec_report.Order.OrderQty,
            QuantityType=QuantityType.SHARES,
            Account=exec_report.Order.Account,
            Broker=exec_report.Order.Broker,
            Strategy=exec_report.Order.Strategy,
            OrderType=exec_report.Order.OrdType,
            OrderPrice=exec_report.Order.Price,
            CumQty=exec_report.CumQty,
            LeavesQty=exec_report.LeavesQty,
            AvgPx=exec_report.AvgPx,
            LastQty=exec_report.LastQty,
            LastPx=exec_report.LastPx,
            LastMkt=exec_report.LastMkt
        )

        pos.SetPositionStatusFromExecution(exec_report)
        pos.ExecutionReports.append(exec_report)
        pos.AppendOrder(exec_report.Order)
        return pos

    @staticmethod
    def GetPositionsFromExecutionReportList(self, wrapper):

        ExecutionReportListConverter.ValidateExecutionReportList(self, wrapper)

        exec_reports_wrappers = wrapper.GetField(ExecutionReportListField.ExecutionReports)

        # Now we convert every execReport into a position

        positions = []
        for execReportWrapper in exec_reports_wrappers:
            pos= ExecutionReportListConverter.CreatePositionFromExecutionReport(self,execReportWrapper)
            positions.append(pos)

        return positions
