import importlib
import time
import threading
from sources.framework.common.abstract.base_communication_module import BaseCommunicationModule
from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.logger.message_type import MessageType
from sources.generic_orderrouter.market_order_router.common.configuration.configuration import *
from sources.framework.common.dto.cm_state import *
from sources.generic_orderrouter.common.converters.position_converter import *
from sources.generic_orderrouter.market_order_router.common.wrappers.new_order_wrapper import *
from sources.generic_orderrouter.market_order_router.common.wrappers.execution_report_list_request_wrapper import *
from sources.generic_orderrouter.common.converters.execution_report_list_converter import *
from sources.generic_orderrouter.common.wrappers.position_list_wrapper import *
from sources.generic_orderrouter.market_order_router.common.wrappers.execution_report_wrapper import \
    ExecutionReportWrapper as GenericERWrapper


class MarketOrderRouter(BaseCommunicationModule, ICommunicationModule):

    def __init__(self):
        self.Name = "Market Order Router"
        self.OutgoingModule = None
        self.Positions = {}

    def LoadConfig(self):
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True

    def ProcessError(self,wrapper):
        self.InvokingModule.ProcessOutgoing(wrapper)
        return CMState.BuildSuccess(self)

    def ProcessOrderCancelReject(self,wrapper):
        self.InvokingModule.ProcessOutgoing(wrapper)
        return CMState.BuildSuccess(self)

    def ProcessExecutionReportList(self, wrapper):
        try:

            positions = ExecutionReportListConverter.GetPositionsFromExecutionReportList(self, wrapper)

            for pos in positions:
                if pos.GetLastOrder() is not None:
                    pos.GetLastOrder().ClOrdId = pos.PosId
                    self.Positions[pos.GetLastOrder().OrderId] = pos
                else:
                    self.DoLog("Could not find order for pre existing position on execution report initial load. PosId = {}".format(pos.PosId), MessageType.ERROR)

            pos_list_wrapper = PositionListWrapper(positions)
            self.InvokingModule.ProcessOutgoing(pos_list_wrapper)
            return CMState.BuildSuccess(self)
        except Exception as e:
            errWrapper = PositionListWrapper([],e)
            self.InvokingModule.ProcessOutgoing(errWrapper)
            self.DoLog("Error processing execution report list:{}".format(e), MessageType.ERROR)
            return CMState.BuildFailure(e)

    def ProcessExecutionReport(self, wrapper):
        try:
            cl_ord_id = wrapper.GetField(ExecutionReportField.ClOrdID)
            order_id = wrapper.GetField(ExecutionReportField.OrderID)
            pos = next(iter(list(filter(lambda x: x.GetLastOrder().ClOrdId == cl_ord_id, self.Positions.values()))), None)

            if pos is not None:
                processed_exec_report = GenericERWrapper(pos.PosId, wrapper)
                self.InvokingModule.ProcessOutgoing(processed_exec_report)
            elif next(iter(list(filter(lambda x: x.GetLastOrder().OrderId == order_id, self.Positions.values()))), None) is not None:
                pos = next(iter(list(filter(lambda x: x.GetLastOrder().OrderId == order_id, self.Positions.values()))), None)
                processed_exec_report = GenericERWrapper(pos.PosId, wrapper)
                self.InvokingModule.ProcessOutgoing(processed_exec_report)
            else:
                self.DoLog( "Received ExecutionReport for unknown ClOrdId ={} OrderId= {}".format(cl_ord_id, order_id),MessageType.WARNING)
        except Exception as e:
            self.DoLog("Error processing execution report:{}".format(e), MessageType.ERROR)

    def ProcessPositionListRequest(self, wrapper):
        exec_report_list_req_wrapper = ExecutionReportListRequestWrapper()
        return self.OutgoingModule.ProcessMessage(exec_report_list_req_wrapper)

    def ProcessNewPosition(self, wrapper):
        new_pos = PositionConverter.ConvertPosition(self, wrapper)
        # In this Generic Order Router ClOrdID=PosId
        self.Positions[new_pos.PosId] = new_pos
        order_wrapper = NewOrderWrapper(new_pos.Security.Symbol, new_pos.OrderQty, new_pos.PosId,
                                        new_pos.Security.Currency, new_pos.Side, new_pos.Account, new_pos.Broker,
                                        new_pos.Strategy, new_pos.OrderType, new_pos.OrderPrice)
        self.OutgoingModule.ProcessMessage(order_wrapper)

    def ProcessCandleBar(self,wrapper):
        self.InvokingModule.ProcessIncoming(wrapper)

    def ProcessMarketData(self, wrapper):
        self.InvokingModule.ProcessIncoming(wrapper)

    def ProcessIncoming(self, wrapper):
        try:

            if wrapper.GetAction() == Actions.CANDLE_BAR_DATA:
                self.ProcessCandleBar(wrapper)
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.MARKET_DATA:
                self.ProcessMarketData(wrapper)
                return CMState.BuildSuccess(self)
            else:
                raise Exception("ProcessOutgoing: GENERIC Order Router not prepared for outgoing message {}".format(
                    wrapper.GetAction()))

        except Exception as e:
            self.DoLog("Error running ProcessOutgoing @GenericOrderRouter module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessOutgoing(self, wrapper):
        try:

            if wrapper.GetAction() == Actions.EXECUTION_REPORT:
                self.ProcessExecutionReport(wrapper)
                #threading.Thread(target=self.ProcessExecutionReport, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.EXECUTION_REPORT_LIST:
                return self.ProcessExecutionReportList(wrapper)
            elif wrapper.GetAction() == Actions.ORDER_CANCEL_REJECT:
                return self.ProcessOrderCancelReject(wrapper)
            elif wrapper.GetAction() == Actions.ERROR:
                return self.ProcessError(wrapper)
            else:
                raise Exception("ProcessOutgoing: GENERIC Order Router not prepared for outgoing message {}".format(
                    wrapper.GetAction()))

        except Exception as e:
            self.DoLog("Error running ProcessOutgoing @GenericOrderRouter module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessMessage(self, wrapper):
        try:

            if wrapper.GetAction() == Actions.NEW_POSITION:
                self.ProcessNewPosition(wrapper)
            elif wrapper.GetAction() == Actions.POSITION_LIST_REQUEST:
                return self.ProcessPositionListRequest(wrapper)
            elif wrapper.GetAction() == Actions.CANCEL_POSITION:
                raise Exception("Cancel Position not implemented @Generic Order Router")
            elif wrapper.GetAction() == Actions.CANCEL_ALL_POSITIONS:
                return self.OutgoingModule.ProcessMessage(wrapper)
            elif wrapper.GetAction() == Actions.CANDLE_BAR_REQUEST:
                return self.OutgoingModule.ProcessMessage(wrapper)
            else:
                raise Exception("Generic Order Router not prepared for routing message {}".format(wrapper.GetAction()))

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Error running ProcessMessage @OrderRouter.IB module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def Initialize(self, pInvokingModule, pConfigFile):
        self.InvokingModule = pInvokingModule
        self.ModuleConfigFile = pConfigFile

        try:
            self.DoLog("Initializing Generic Market Order Router", MessageType.INFO)
            if self.LoadConfig():
                self.OutgoingModule = self.InitializeModule(self.Configuration.OutgoingModule,self.Configuration.OutgoingConfigFile)
                self.DoLog("Generic Market Order Router Initialized", MessageType.INFO)
                return CMState.BuildSuccess(self)
            else:
                raise Exception("Unknown error initializing config file for Generic Market Order Router")

        except Exception as e:

            self.DoLog("Error Loading Generic Market Order Router module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

