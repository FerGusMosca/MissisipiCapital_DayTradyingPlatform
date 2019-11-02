from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.strategy.strategies.day_trader.common.configuration.configuration import Configuration
from sources.strategy.strategies.day_trader.common.converters.csv_converter import *
from sources.strategy.strategies.day_trader.common.util.csv_constants import *
from sources.strategy.strategies.day_trader.data_access_layer.execution_report_data_access_layer import *
from sources.framework.common.converters.execution_report_converter import *
from sources.framework.common.enums.fields.execution_report_field import *
from sources.framework.common.enums.fields.position_list_field import *
from sources.framework.common.abstract.base_communication_module import *
from sources.framework.business_entities.positions.execution_summary import *
from sources.framework.business_entities.positions.position import *
from sources.framework.business_entities.securities.security import *
from sources.strategy.common.wrappers.position_wrapper import *
from sources.framework.common.wrappers.cancel_all_wrapper import *
from sources.framework.common.enums.Side import *
from sources.framework.common.dto.cm_state import *
from sources.strategy.strategies.day_trader.common.util.local_folder_file_handler import *
from sources.strategy.common.wrappers.position_list_request_wrapper import *
import csv
import importlib
import threading
import time
import datetime
import uuid
import schedule
import queue

class DayTrader(BaseCommunicationModule, ICommunicationModule):

    def __init__(self):
        self.Lock = threading.Lock()
        self.Configuration = None
        self.NextPostId = uuid.uuid4()
        self.ExecutionSummaries = {}
        self.ExecutionReportManager = None
        self.InvokingModule = None
        self.OutgoingModule = None
        self.OrdersQueue = queue.Queue(maxsize=1000000)
        self.SummariesQueue = queue.Queue(maxsize=1000000)

    def OrdersPersistanceThread(self):

        while True:

            while not self.OrdersQueue.empty():

                try:

                    order = self.OrdersQueue.get()
                    #print("order {} get".format(order.OrderId))
                    if self.ExecutionReportManager is not None:
                        self.DoLog("Persisting order {}".format(order.OrderId),MessageType.DEBUG)
                        self.ExecutionReportManager.PersistOrder(order)
                    else:
                        self.DoLog("Not persisiting order with order id {} because not established connection to DB".format(order.OrderId),MessageType.INFO)
                    #print("order {} persisted".format(order.OrderId))
                except Exception as e:
                    self.DoLog("Error Saving Orders to DB: {}".format(e), MessageType.ERROR)
            time.sleep(int(1))

    def TradesPersistanceThread(self):

        while True:

            while not self.SummariesQueue.empty():

                try:
                    summary = self.SummariesQueue.get()
                    if self.ExecutionReportManager is not None:
                        first_trade_exec_rep = summary.Position.GetFirstTradeExecutionReport()
                        if first_trade_exec_rep is not None:
                            self.DoLog("Persisting trade {} ".format(first_trade_exec_rep.ExecId),MessageType.DEBUG)
                            self.ExecutionReportManager.PersistExecutionSummary(first_trade_exec_rep.ExecId,summary)
                    else:
                        self.DoLog("Not persisiting trade for PosId {} because not established connection to DB".format(summary.Position.PosId),MessageType.INFO)

                except Exception as e:
                    self.DoLog("Error Saving Trades to DB: {}".format(e), MessageType.ERROR)
            time.sleep(int(1))

    def ProcessOrder(self,summary, isRecovery):
        """ Persist an order in the database

        Args:
            summary (:obj:`ExecutionSummary`): Execution summary to be updated.
        """

        order = summary.Position.GetLastOrder()

        if order is not None:
            if  summary.Position.IsFinishedPosition() or self.Configuration.PersistFullOrders:
                if isRecovery and self.Configuration.PersistRecovery:
                    self.OrdersQueue.put(order)
                elif not isRecovery:
                    self.OrdersQueue.put(order)
        else:
            self.DoLog("Order not found for position {}".format(summary.Position.PosId), MessageType.DEBUG)

    def UpdateExecutionSummary(self, summary, execReport, recovered=False):
        """ Update Summary information with Execution Report received

        Args:
            recovered ():
            summary (:obj:`ExecutionSummary`): Execution summary to be updated.
            execReport (:obj:`ExecutionReport`): Execution report data as input.
        """
        summary.UpdateStatus(execReport)

        if not recovered:

            if summary.Position.IsFinishedPosition():
                self.DoLog(
                    "Position Finished: PosId={} Symbol={} Side={} Final Status={} OrdQty={} CumQty={} LvsQty={} "
                    "AvgPx={} Text={} "
                        .format(summary.Position.PosId,
                                summary.Position.Security.Symbol,
                                summary.Position.Side,
                                summary.Position.PosStatus,
                                summary.Position.Qty if summary.Position.Qty is not None else summary.Position.CashQty,
                                summary.CumQty,
                                summary.LeavesQty,
                                summary.AvgPx,
                                execReport.Text), MessageType.INFO)
            else:
                self.DoLog(
                    "Position Updated: PosId={} Symbol={}  Side={} Final Status={} OrdQty={} CumQty={} LvsQty={} "
                    "AvgPx={} Text={} "
                        .format(summary.Position.PosId,
                                summary.Position.Security.Symbol,
                                summary.Position.Side,
                                summary.Position.PosStatus,
                                summary.Position.Qty if summary.Position.Qty is not None else summary.Position.CashQty,
                                summary.CumQty,
                                summary.LeavesQty,
                                summary.AvgPx,
                                execReport.Text), MessageType.INFO)

        if recovered:

            if not summary.Position.IsFinishedPosition():
                self.DoLog(
                    "Recovered previously existing position: PosId={} Symbol={} Side={}  Final Status={} OrdQty={} "
                    "CumQty={} LvsQty={} AvgPx={} Text={} "
                        .format(summary.Position.PosId,
                                summary.Position.Security.Symbol,
                                summary.Position.Side,
                                summary.Position.PosStatus,
                                summary.Position.Qty if summary.Position.Qty is not None else summary.Position.CashQty,
                                summary.CumQty,
                                summary.LeavesQty,
                                summary.AvgPx,
                                execReport.Text if execReport is not None else ""), MessageType.INFO)
                self.ExecutionSummaries[summary.Position.PosId] = summary

        # Recovered or not. If it's a traded position, we fill the DB
        if summary.Position.IsTradedPosition():
            try:
                first_trade_exec_rep = summary.Position.GetFirstTradeExecutionReport()
                # if recovered ==  False:
                if first_trade_exec_rep is not None:
                    if(recovered == False or self.Configuration.PersistRecovery):
                        self.SummariesQueue.put(summary)
                else:
                    self.DoLog(
                        "Critical error saving traded position with no fill Id.PosId:{}".format(summary.Position.PosId),
                        MessageType.ERROR)

            except Exception as e:
                self.DoLog("Error Saving to DB: {}".format(e), MessageType.ERROR)

    def ProcessExecutionReport(self, wrapper):
        """ Process execution report received from module that is invoked.

        Args:
            wrapper (:obj:`Wrapper`): Generic wrapper to communicate strategy with other modules.

        Returns:
            CMState object: The return value. BuildSuccess for success.

        """
        try:

            try:
                exec_report = ExecutionReportConverter.ConvertExecutionReport(wrapper)
            except Exception as e:
                self.DoLog("Discarding execution reprot with bad data: " + str(e), MessageType.INFO)
                #exec_report = ExecutionReportConverter.ConvertExecutionReport(wrapper)
                return

            pos_id = wrapper.GetField(ExecutionReportField.PosId)

            if pos_id is not None:
                if pos_id in self.ExecutionSummaries:
                    summary = self.ExecutionSummaries[pos_id]
                    self.UpdateExecutionSummary(summary, exec_report)
                    self.ProcessOrder(summary,False)
                    return CMState.BuildSuccess(self)
                else:
                    raise Exception("Received execution report for unknown PosId {}".format(pos_id))
            else:
                raise Exception("Received execution report without PosId")
        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessExecutionReport: " + str(e), MessageType.ERROR)

    def LoadConfig(self):
        """ Load current configuration from module configuration file.

        Returns:
            bool: True if finished.

        """
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True

    def InitializeGenericOrderRouter(self):
        """ Initialize Generic Order Router with specific module name from configuration file.

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

    def CancelAllPositions(self):

        for posId in self.ExecutionSummaries:
            if(self.ExecutionSummaries[posId].Position.IsOpenPosition()):
                pos = self.ExecutionSummaries[posId]
                pos.PosStatus = PositionStatus.PendingCancel


        cancelWrapper = CancelAllWrapper()
        self.OutgoingModule.ProcessMessage(cancelWrapper)

    def ProcessPositionList(self, wrapper):
        try:
            positions = wrapper.GetField(PositionListField.Positions)
            self.DoLog(
                "Received list of Open Positions: {} positions".format(Position.CountOpenPositions(self, positions)),
                MessageType.INFO)
            i=0
            for pos in positions:

                summary = ExecutionSummary(datetime.datetime.now(), pos)
                last_exec_report = None
                if pos.GetLastExecutionReport() is not None:
                    last_exec_report = pos.GetLastExecutionReport()
                    self.UpdateExecutionSummary(summary, last_exec_report,recovered=True)  # we will persist only if we have an existing position
                    self.ProcessOrder(summary,True)
                else:
                    self.DoLog("Could not find execution report for position id {}".format(pos.PosId),
                               MessageType.ERROR)

            self.DoLog("Starting process to fetch files", MessageType.INFO)
            threading.Thread(target=self.FileHandler.FetchFile, args=()).start()
        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessPositionList: " + str(e), MessageType.ERROR)

    def RequestPositionList(self):
        time.sleep(int(self.Configuration.PauseBeforeExecutionInSeconds))
        self.DoLog("Requesting for open orders...", MessageType.INFO)
        wrapper = PositionListRequestWrapper()
        self.OutgoingModule.ProcessMessage(wrapper)

    def ProcessMessage(self, wrapper):
        pass

    def ProcessOutgoing(self, wrapper):
        """ Receives a response from another module that is invoked.

        Args:
            wrapper (:obj:`Wrapper`): Generic wrapper to communicate strategy with other modules.

        Returns:
            CMState object: The return value. BuildSuccess for success, BuildFailure otherwise.

        """
        try:
            if wrapper.GetAction() == Actions.EXECUTION_REPORT:
                threading.Thread(target=self.ProcessExecutionReport, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.POSITION_LIST:
                threading.Thread(target=self.ProcessPositionList, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            else:
                raise Exception("MainApp: Not prepared for routing message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessOutgoing: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def Initialize(self, pInvokingModule, pConfigFile):
        """  Initialize everything.

        Args:
            pInvokingModule (ProcessOutgoing method): Invoking module.
            pConfigFile (Ini file): Configuration file path.
        """
        self.ModuleConfigFile = pConfigFile
        self.InvokingModule = pInvokingModule
        self.DoLog("DayTrader  Initializing", MessageType.INFO)

        if self.LoadConfig():

            threading.Thread(target=self.OrdersPersistanceThread, args=()).start()

            threading.Thread(target=self.TradesPersistanceThread, args=()).start()

            self.InitializeGenericOrderRouter()

            self.DoLog("DayTrader Successfully initializer", MessageType.INFO)


        else:
            self.DoLog("Error initializing config file for SimpleCSVProcessor", MessageType.ERROR)
