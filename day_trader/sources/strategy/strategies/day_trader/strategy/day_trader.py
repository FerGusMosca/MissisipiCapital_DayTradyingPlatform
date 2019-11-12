from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.enums.fields.order_cancel_reject_field import *
from sources.framework.common.wrappers.error_wrapper import *
from sources.strategy.strategies.day_trader.common.configuration.configuration import Configuration
from sources.framework.common.converters.execution_report_converter import *
from sources.framework.common.enums.fields.execution_report_field import *
from sources.framework.common.enums.fields.position_list_field import *
from sources.framework.common.abstract.base_communication_module import *
from sources.framework.business_entities.positions.execution_summary import *
from sources.framework.business_entities.positions.position import *
from sources.framework.common.wrappers.cancel_all_wrapper import *
from sources.framework.common.wrappers.market_data_request_wrapper import *
from sources.framework.common.wrappers.historical_prices_request_wrapper import *
from sources.framework.common.wrappers.candle_bar_request_wrapper import *
from sources.framework.common.enums.SubscriptionRequestType import *
from sources.strategy.strategies.day_trader.common.converters.market_data_converter import *
from sources.framework.common.dto.cm_state import *
from sources.strategy.common.wrappers.position_list_request_wrapper import *
from sources.strategy.data_access_layer.security_to_trade_manager import *
from sources.strategy.data_access_layer.model_parameters_manager import *
from sources.strategy.strategies.day_trader.common.util.log_helper import *
import threading
import time
import datetime
import uuid
import queue

_BAR_FREQUENCY="BAR_FREQUENCY"

class DayTrader(BaseCommunicationModule, ICommunicationModule):

    def __init__(self):
        self.Lock = threading.Lock()
        self.Configuration = None
        self.NextPostId = uuid.uuid4()

        self.ExecutionSummaries = {}

        self.SecurityToTradeManager = None
        self.ModelParametersManager = None

        self.SecuritiesToTrade = []
        self.ModelParameters = {}
        self.MarketData={}
        self.Candlebars={}
        self.HistoricalPrices={}

        self.InvokingModule = None
        self.OutgoingModule = None

        self.FailureException = None
        self.ServiceFailure = False

        self.OrdersQueue = queue.Queue(maxsize=1000000)
        self.SummariesQueue = queue.Queue(maxsize=1000000)

    def FetchParam(self,key):
        if self.ModelParameters is not None:
            if key in self.ModelParameters:
                return self.ModelParameters[key]
            else:
                raise Exception("Unknown key {}",format(key))
        else:
            raise Exception("ModelParameters dictionary not initialized!!!!")

    def ProcessCriticalError(self, exception,msg):
        self.FailureException=exception
        self.ServiceFailure=True
        self.DoLog(msg, MessageType.ERROR)



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
        summary.UpdateStatus(execReport)

        if not recovered:

            if summary.Position.IsFinishedPosition():
                LogHelper.LogPositionUpdate(self,"Position Finished",summary,execReport)
            else:
                LogHelper.LogPositionUpdate(self, "PositionUpdated", summary, execReport)

        if recovered:

            if not summary.Position.IsFinishedPosition():
                LogHelper.LogPositionUpdate(self, "Recovered previously existing position", summary, execReport)
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
                    self.DoLog( "Critical error saving traded position with no fill Id.PosId:{}".format(summary.Position.PosId), MessageType.ERROR)

            except Exception as e:
                self.DoLog("Error Saving to DB: {}".format(e), MessageType.ERROR)

    def ProcessOrderCancelReject(self,wrapper):

        try:

            orderId = wrapper.GetField(OrderCancelRejectField.OrderID)
            msg = wrapper.GetField(OrderCancelRejectField.Text)
            self.DoLog("Publishing cancel reject for orderId {} reason:{}".format(orderId,msg),MessageType.INFO)
            errWrapper = ErrorWrapper (Exception(msg))
            threading.Thread(target=self.ProcessError, args=(errWrapper,)).start()

        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessOrderCancelReject: " + str(e), MessageType.ERROR)

    def ProcessExecutionReport(self, wrapper):
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
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True

    def LoadManagers(self):
        self.SecurityToTradeManager = SecurityToTradeManager(self.Configuration.DBHost, self.Configuration.DBPort,
                                                             self.Configuration.DBCatalog, self.Configuration.DBUser,
                                                             self.Configuration.DBPassword)

        self.SecuritiesToTrade = self.SecurityToTradeManager.GetSecurtitiesToTrade()


        self.ModelParametersManager = ModelParametersManager(self.Configuration.DBHost, self.Configuration.DBPort,
                                                             self.Configuration.DBCatalog, self.Configuration.DBUser,
                                                             self.Configuration.DBPassword)

        modelParams = self.ModelParametersManager.GetModelParametersManager()

        for param in modelParams:
            self.ModelParameters[param.Key]=param




    def CancelAllPositions(self):

        for posId in self.ExecutionSummaries:
            if(self.ExecutionSummaries[posId].Position.IsOpenPosition()):
                pos = self.ExecutionSummaries[posId]
                pos.PosStatus = PositionStatus.PendingCancel


        cancelWrapper = CancelAllWrapper()
        self.OutgoingModule.ProcessMessage(cancelWrapper)

    def ProcessPositionList(self, wrapper):
        try:
            success = wrapper.GetField(PositionListField.Status)
            if success:
                positions = wrapper.GetField(PositionListField.Positions)
                self.DoLog("Received list of Open Positions: {} positions".format(Position.CountOpenPositions(self, positions)),
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

                self.DoLog("Process ready to receive commands and trade", MessageType.INFO)
            else:
                exception= wrapper.GetField(PositionListField.Error)
                raise exception

        except Exception as e:
            self.ProcessCriticalError(e,"Critical error @DayTrader.ProcessPositionList:{}".format(e))

    def ProcessMarketData(self,wrapper):
        try:
            md = MarketDataConverter.ConvertMarketData(wrapper)
            self.MarketData[md.Security.Symbol]=md
            self.DoLog("Marktet Data successfully loaded for symbol {} ".format(md.Security.Symbol),MessageType.DEBUG)

        except Exception as e:
            self.ProcessError("@DayTrader.ProcessMarketData", e)

    def ProcessError(self,method,e):
        msg = "Critical error @{}:{} ".format(method,str(e))
        error = ErrorWrapper(Exception(msg))
        self.ProcessError(error)
        self.DoLog(msg, MessageType.ERROR)

    def ProcessError(self,wrapper):
        try:
           self.InvokingModule.ProcessMessage(wrapper)
        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessError: " + str(e), MessageType.ERROR)

    def ProcessHistoricalPrices(self,wrapper):
        try:
            security = MarketDataConverter.ConvertHistoricalPrices(wrapper)
            self.HistoricalPrices[security.Symbol]=security.MarketDataArr
            self.DoLog("Historical prices successfully loaded for symbol {} ".format(security.Symbol), MessageType.INFO)
        except Exception as e:
            self.ProcessError("@DayTrader.ProcessHistoricalPrices",e)

    def ProcessCandleBar(self,wrapper):
        try:
            candlebar = MarketDataConverter.ConvertCandlebar(wrapper)

            if candlebar is not None:
                cbDict = self.Candlebars[candlebar.Security.Symbol]
                if cbDict is  None:
                    cbDict = {}

                cbDict[candlebar.DateTime] = candlebar
                self.Candlebars[candlebar.Security.Symbol]=cbDict

                self.DoLog("Candlebars successfully loaded for symbol {} ".format(candlebar.Security.Symbol),MessageType.DEBUG)
            else:
                self.DoLog("Received unknown null candlebar",MessageType.DEBUG)

        except Exception as e:
            self.ProcessError("@DayTrader.ProcessCandleBar", e)

    def RequestPositionList(self):
        time.sleep(int(self.Configuration.PauseBeforeExecutionInSeconds))
        self.DoLog("Requesting for open orders...", MessageType.INFO)
        wrapper = PositionListRequestWrapper()
        self.OrderRoutingModule.ProcessMessage(wrapper)

    def RequestMarketData(self):
        for secIn in self.SecuritiesToTrade:
            self.MarketData[secIn.Security.Symbol]=secIn.Security
            mdReqWrapper = MarketDataRequestWrapper(secIn.Security,SubscriptionRequestType.SnapshotAndUpdates)
            self.MarketDataModule.ProcessMessage(mdReqWrapper)

    def RequestBars(self):
        for secIn in self.SecuritiesToTrade:
            sec = self.MarketData[secIn.Security.Symbol]
            time = int( self.FetchParam(_BAR_FREQUENCY).IntValue)
            if sec is not None:
                self.Candlebars[secIn.Security.Symbol]=None
                mdReqWrapper = CandleBarRequestWrapper(secIn.Security,time,TimeUnit.Minute,
                                                       SubscriptionRequestType.SnapshotAndUpdates)
                self.MarketDataModule.ProcessMessage(mdReqWrapper)
            else:
                raise Exception("Could not find security for symbol {}".format(secIn.Security.Symbol))

    def RequestHistoricalPrices(self):
        for secIn in self.SecuritiesToTrade:
            sec = self.MarketData[secIn.Security.Symbol]

            if sec is not None:
                self.HistoricalPrices[secIn.Security.Symbol]=None
                hpReqWrapper = HistoricalPricesRequestWrapper(secIn.Security,self.Configuration.HistoricalPricesPastDays,
                                                              TimeUnit.Day, SubscriptionRequestType.Snapshot)
                self.MarketDataModule.ProcessMessage(hpReqWrapper)
            else:
                raise Exception("Could not find security for symbol {}".format(secIn.Security.Symbol))

    def ProcessMessage(self, wrapper):
        pass

    def ProcessIncoming(self, wrapper):
        try:
            if wrapper.GetAction() == Actions.MARKET_DATA:
                threading.Thread(target=self.ProcessMarketData, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.CANDLE_BAR_DATA:
                threading.Thread(target=self.ProcessCandleBar, args=(wrapper,)).start()
            elif wrapper.GetAction() == Actions.HISTORICAL_PRICES:
                threading.Thread(target=self.ProcessHistoricalPrices, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.ERROR:
                threading.Thread(target=self.ProcessError, args=(wrapper,)).start()
            else:
                raise Exception("ProcessIncoming: Not prepared for routing message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessIncoming: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def ProcessOutgoing(self, wrapper):
        try:
            if wrapper.GetAction() == Actions.EXECUTION_REPORT:
                threading.Thread(target=self.ProcessExecutionReport, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.POSITION_LIST:
                threading.Thread(target=self.ProcessPositionList, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.ORDER_CANCEL_REJECT:
                threading.Thread(target=self.ProcessOrderCancelReject, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.ERROR:
                threading.Thread(target=self.ProcessError, args=(wrapper,)).start()
                return CMState.BuildSuccess(self)
            else:
                raise Exception("ProcessOutgoing: Not prepared for routing message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessOutgoing: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def Initialize(self, pInvokingModule, pConfigFile):
        self.ModuleConfigFile = pConfigFile
        self.InvokingModule = pInvokingModule
        self.DoLog("DayTrader  Initializing", MessageType.INFO)

        if self.LoadConfig():

            threading.Thread(target=self.OrdersPersistanceThread, args=()).start()

            threading.Thread(target=self.TradesPersistanceThread, args=()).start()

            self.LoadManagers()

            self.MarketDataModule =  self.InitializeModule(self.Configuration.IncomingModule,self.Configuration.IncomingConfigFile)

            self.OrderRoutingModule = self.InitializeModule(self.Configuration.OutgoingModule,self.Configuration.OutgoingConfigFile)

            self.WebsocketModule = self.InitializeModule(self.Configuration.WebsocketModule,self.Configuration.WebsocketConfigFile)

            time.sleep(self.Configuration.PauseBeforeExecutionInSeconds)

            self.RequestMarketData()

            self.RequestPositionList()

            self.RequestBars()

            self.RequestHistoricalPrices()

            self.DoLog("DayTrader Successfully initialized", MessageType.INFO)

            return CMState.BuildSuccess(self)


        else:
            msg = "Error initializing config file for SimpleCSVProcessor"
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self,errorMsg=msg)
