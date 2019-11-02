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
        self.OrderPositions = {}
        self.MemOrderPositions = {}  # different dictionary that works with the previously existing orders
        self.PreviouslyFinishedPositions = {}

    def LoadConfig(self):
        """ Load current configuration from module configuration file.

        Returns:
            bool. True if finished.
        """
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True

    def InitializeOrderRouter(self):
        """ Initialize Generic Order Router with specific module name from configuration file

        """
        module_name, class_name = self.Configuration.OutgoingModule.rsplit(".", 1)
        outgoing_module_class = getattr(importlib.import_module(module_name), class_name)

        if outgoing_module_class is not None:
            self.OutgoingModule = outgoing_module_class()
            state = self.OutgoingModule.Initialize(self, self.Configuration.OutgoingConfigFile)

            if not state.Success:
                raise state.Exception
        else:
            raise Exception("Could not instantiate module {}".format(self.Configuration.OutgoingModule))

    def ProcessExecutionReportList(self, wrapper):
        """

        Args:
            wrapper ():

        Returns:

        """
        positions = ExecutionReportListConverter.GetPositionsFromExecutionReportList(self, wrapper)
        for pos in positions:
            if not pos.IsFinishedPosition():

                if pos.GetLastOrder() is not None:
                    pos.GetLastOrder().ClOrdId = pos.PosId
                    self.MemOrderPositions[pos.GetLastOrder().OrderId] = pos
                else:
                    self.DoLog(
                        "Could not find order for pre existing position on execution report initial load. PosId = {}".format(pos.PosId), MessageType.ERROR)
            else:
                if pos.GetLastOrder() is not None:
                    pos.GetLastOrder().ClOrdId = pos.PosId
                    self.PreviouslyFinishedPositions[pos.GetLastOrder().OrderId] = pos
                else:
                    self.DoLog(
                        "Could not find order for finished previous position on execution report initial load. PostId "
                        "= {}".format(
                            pos.PosId), MessageType.ERROR)

        pos_list_wrapper = PositionListWrapper(positions)
        self.InvokingModule.ProcessOutgoing(pos_list_wrapper)
        return CMState.BuildSuccess(self)

    def ProcessPreviouslyExistingOrders(self, orderId, wrapper):
        """

        Returns:
            object:
        """
        mem_pos = self.MemOrderPositions[orderId]
        processed_exec_report = GenericERWrapper(mem_pos.PosId, wrapper)
        self.InvokingModule.ProcessOutgoing(processed_exec_report)

    def ProcessExecutionReport(self, wrapper):
        """ Process execution report received from module that is invoked.

        Args:
            wrapper (:obj:`Wrapper`): Generic wrapper to communicate strategy with other modules.

        Returns:
            CMState object. The return value. BuildSuccess for success.
        """

        try:
            cl_ord_id = wrapper.GetField(ExecutionReportField.ClOrdID)
            order_id = wrapper.GetField(ExecutionReportField.OrderID)

            if cl_ord_id in self.OrderPositions:
                pos = self.OrderPositions[cl_ord_id]
                processed_exec_report = GenericERWrapper(pos.PosId, wrapper)
                self.InvokingModule.ProcessOutgoing(processed_exec_report)
            elif order_id in self.MemOrderPositions:
                self.ProcessPreviouslyExistingOrders(order_id, wrapper)
            else:
                time.sleep(10)
                if order_id in self.MemOrderPositions:
                    self.ProcessPreviouslyExistingOrders(order_id, wrapper)
                else:
                    if not order_id in self.PreviouslyFinishedPositions:  # otherwise we just ignore
                        self.DoLog(
                            "Received ExecutionReport for unknown ClOrdId ={} OrderId= {}".format(cl_ord_id, order_id),
                            MessageType.WARNING)
        except Exception as e:
            self.DoLog("Error processing execution report:{}".format(e), MessageType.ERROR)

    def ProcessPositionListRequest(self, wrapper):
        """

        Args:
            wrapper ():

        Returns:

        """
        exec_report_list_req_wrapper = ExecutionReportListRequestWrapper()
        return self.OutgoingModule.ProcessMessage(exec_report_list_req_wrapper)

    def ProcessNewPosition(self, wrapper):
        """ Send a new order wrapper to ProcessMessage method from Order Router module.

        Args:
            wrapper (:obj:`Wrapper`): Generic wrapper to communicate strategy with other modules.
        """
        new_pos = PositionConverter.ConvertPosition(self, wrapper)
        # In this Generic Order Router ClOrdID=PosId
        self.OrderPositions[new_pos.PosId] = new_pos
        order_wrapper = NewOrderWrapper(new_pos.Security.Symbol, new_pos.OrderQty, new_pos.PosId,
                                        new_pos.Security.Currency, new_pos.Side, new_pos.Account, new_pos.Broker,
                                        new_pos.Strategy, new_pos.OrderType, new_pos.OrderPrice)
        self.OutgoingModule.ProcessMessage(order_wrapper)

    def ProcessOutgoing(self, wrapper):
        """ Receives a response from another module that is invoked.

        Args:
            wrapper (:obj:`Wrapper`): Generic wrapper to communicate strategy with other modules.

        Returns:
            CMState object. The return value. BuildSuccess for success.
        """
        try:

            if wrapper.GetAction() == Actions.EXECUTION_REPORT:
                self.ProcessExecutionReport(wrapper)
                #threading.Thread(target=self.ProcessExecutionReport, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.EXECUTION_REPORT_LIST:
                return self.ProcessExecutionReportList(wrapper)
            else:
                raise Exception("ProcessOutgoing: GENERIC Order Router not prepared for outgoing message {}".format(
                    wrapper.GetAction()))

        except Exception as e:
            self.DoLog("Error running ProcessOutgoing @GenericOrderRouter module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessMessage(self, wrapper):
        """ Receives messages from “invoking” modules.

        Args:
            wrapper (:obj:`Wrapper`): Generic wrapper to communicate strategy with other modules.

        Returns:
            CMState object. The return value. BuildSuccess for success, BuildFailure otherwise.
        """
        try:

            if wrapper.GetAction() == Actions.NEW_POSITION:
                self.ProcessNewPosition(wrapper)
            elif wrapper.GetAction() == Actions.POSITION_LIST_REQUEST:
                return self.ProcessPositionListRequest(wrapper)
            elif wrapper.GetAction() == Actions.CANCEL_POSITION:
                raise Exception("Cancel Position not implemented @Generic Order Router")
            elif wrapper.GetAction() == Actions.CANCEL_ALL_POSITIONS:
                return self.OutgoingModule.ProcessMessage(wrapper)
            else:
                raise Exception("Generic Order Router not prepared for routing message {}".format(wrapper.GetAction()))

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Error running ProcessMessage @OrderRouter.IB module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def Initialize(self, pInvokingModule, pConfigFile):
        """  initialize everything

        Args:
            pInvokingModule (ProcessOutgoing method): Invoking module.
            pConfigFile (Ini file): Configuration file path.

        Returns:
            CMState object. The return value. BuildSuccess for success, BuildFailure otherwise.
        """
        self.InvokingModule = pInvokingModule
        self.ModuleConfigFile = pConfigFile

        try:
            self.DoLog("Initializing Generic Market Order Router", MessageType.INFO)
            if self.LoadConfig():
                self.InitializeOrderRouter()
                self.DoLog("Generic Market Order Router Initialized", MessageType.INFO)
                return CMState.BuildSuccess(self)
            else:
                raise Exception("Unknown error initializing config file for Generic Market Order Router")

        except Exception as e:

            self.DoLog("Error Loading Generic Market Order Router module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

