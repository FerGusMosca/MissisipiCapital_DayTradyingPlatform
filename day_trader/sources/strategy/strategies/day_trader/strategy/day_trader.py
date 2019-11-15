from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.enums.fields.order_cancel_reject_field import *
from sources.framework.common.wrappers.error_wrapper import *
from sources.strategy.strategies.day_trader.common.configuration.configuration import Configuration
from sources.framework.common.converters.execution_report_converter import *
from sources.framework.common.enums.fields.execution_report_field import *
from sources.framework.common.enums.fields.position_list_field import *
from sources.framework.common.enums.fields.position_field import *
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
from sources.strategy.common.wrappers.position_wrapper import *
from sources.strategy.data_access_layer.security_to_trade_manager import *
from sources.strategy.data_access_layer.model_parameters_manager import *
from sources.strategy.strategies.day_trader.common.util.log_helper import *
from sources.strategy.strategies.day_trader.common.wrappers.portfolio_position_list_wrapper import *
import threading
import time
import datetime
import uuid
import queue

_BAR_FREQUENCY="BAR_FREQUENCY"

class DayTrader(BaseCommunicationModule, ICommunicationModule):

    def __init__(self):
        self.Lock = threading.Lock()
        self.RoutingLock = threading.Lock()
        self.Configuration = None
        self.NextPostId = uuid.uuid4()

        self.PositionSecurities = {}
        self.SingleExecutionSummaries = {}

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
        self.PositionsSynchronization = True

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
                    #TODO persist orders!
                except Exception as e:
                    self.DoLog("Error Saving Orders to DB: {}".format(e), MessageType.ERROR)
            time.sleep(int(1))

    def TradesPersistanceThread(self):

        while True:

            while not self.SummariesQueue.empty():

                try:
                    summary = self.SummariesQueue.get()
                    #TODO: persist trades/summaries!!

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


    def UpdateManagedPosExecutionSummary(self, summary, execReport):
        summary.UpdateStatus(execReport)
        if summary.Position.IsFinishedPosition():
            LogHelper.LogPositionUpdate(self, "Managed Position Finished", summary, execReport)
        else:
            LogHelper.LogPositionUpdate(self, "Managed Position Updated", summary, execReport)

        if summary.Position.IsTradedPosition():
            try:
                first_trade_exec_rep = summary.Position.GetFirstTradeExecutionReport()
                # if recovered ==  False:
                if first_trade_exec_rep is not None:
                    self.SummariesQueue.put(summary)
                else:
                    self.DoLog( "Critical error saving traded managed position with no fill Id.PosId:{}".format(summary.Position.PosId), MessageType.ERROR)

            except Exception as e:
                self.DoLog("Error Saving to DB: {}".format(e), MessageType.ERROR)

    def UpdateSinglePosExecutionSummary(self, summary, execReport, recovered=False):
        summary.UpdateStatus(execReport)

        if not recovered:

            if summary.Position.IsFinishedPosition():
                LogHelper.LogPositionUpdate(self,"Single Position Finished",summary,execReport)
            else:
                LogHelper.LogPositionUpdate(self, "Single Position Updated", summary, execReport)

        if recovered:

            if not summary.Position.IsFinishedPosition():
                LogHelper.LogPositionUpdate(self, "Recovered previously existing position", summary, execReport)
                self.SingleExecutionSummaries[summary.Position.PosId] = summary

        # Recovered or not. If it's a traded position, we fill the DB
        if summary.Position.IsTradedPosition():
            try:
                first_trade_exec_rep = summary.Position.GetFirstTradeExecutionReport()
                # if recovered ==  False:
                if first_trade_exec_rep is not None:
                    if(recovered == False or self.Configuration.PersistRecovery):
                        self.SummariesQueue.put(summary)
                else:
                    self.DoLog( "Critical error saving traded single position with no fill Id.PosId:{}".format(summary.Position.PosId), MessageType.ERROR)

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

                if pos_id in self.PositionSecurities:
                    secToTrade = self.PositionSecurities[pos_id]
                    if pos_id in secToTrade.ExecutionSummaries:
                        summary = secToTrade.ExecutionSummaries[pos_id]
                        self.UpdateManagedPosExecutionSummary(summary,exec_report)
                        self.ProcessOrder(summary, False)
                        return CMState.BuildSuccess(self)
                    else:
                        self.DoLog("Received execution report for a managed position, but we cannot find its execution summary",MessageType.ERROR)


                elif pos_id in self.SingleExecutionSummaries:
                    #we have a single position
                    summary = self.SingleExecutionSummaries[pos_id]
                    self.UpdateSinglePosExecutionSummary(summary, exec_report)
                    self.ProcessOrder(summary, False)
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

        for posId in self.SingleExecutionSummaries:
            if(self.SingleExecutionSummaries[posId].Position.IsOpenPosition()):
                pos = self.SingleExecutionSummaries[posId]
                pos.PosStatus = PositionStatus.PendingCancel

        for posId in self.PositionSecurities:
            secToTrade = self.PositionSecurities[posId]
            for sPosId in secToTrade.ExecutionSummaries:
                pos = secToTrade.ExecutionSummaries[sPosId]
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
                    if pos.GetLastExecutionReport() is not None:
                        self.UpdateSinglePosExecutionSummary(summary, pos.GetLastExecutionReport(),recovered=True)  # we will persist only if we have an existing position
                        self.ProcessOrder(summary,True)
                    else:
                        self.DoLog("Could not find execution report for position id {}".format(pos.PosId),MessageType.ERROR)
                self.PositionsSynchronization= False
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
        msg = "Error @{}:{} ".format(method,str(e))
        error = ErrorWrapper(Exception(msg))
        self.ProcessError(error)
        self.DoLog(msg, MessageType.ERROR)

    def ProcessError(self,wrapper):
        try:
           self.CommandsModule.ProcessMessage(wrapper)
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


    def ProcessPortfolioPositionsRequestThread(self,wrapper):
        try:
            self.Lock.acquire()

            portfListWrapper = PortfolioPositionListWrapper(self.SecuritiesToTrade)
            self.CommandsModule.ProcessMessage(portfListWrapper)
        except Exception as e:
            msg="Critical error @DayTrader.ProcessPortfolioPositionsRequestThread.:{}".format(str(e))
            self.ProcessCriticalError(e,msg)
            self.CommandsModule(ErrorWrapper(Exception(msg)))
        finally:
            return self.Lock.release()


    #we just route a position and ignore the answers
    def ProcessNewPositionReqSinglePos(self,wrapper):
        try:

            symbol = wrapper.GetField(PositionField.Symbol)
            secType = wrapper.GetField(PositionField.SecurityType)
            side = wrapper.GetField(PositionField.Side)
            qty = wrapper.GetField(PositionField.Qty)
            account = wrapper.GetField(PositionField.Account)

            self.RoutingLock.acquire()

            newPos = Position(PosId=self.NextPostId,
                              Security=Security(Symbol=symbol,Exchange=self.Configuration.DefaultExchange,SecType=secType),
                              Side=side,PriceType=PriceType.FixedAmount,Qty=qty,QuantityType=QuantityType.SHARES,
                              Account=account,Broker=None,Strategy=None,OrderType=OrdType.Market)

            newPos.ValidateNewPosition()

            self.SingleExecutionSummaries[self.NextPostId] = ExecutionSummary(datetime.datetime.now(), newPos)
            self.NextPostId = uuid.uuid4()
            self.RoutingLock.release()

            posWrapper = PositionWrapper(newPos)
            self.OrderRoutingModule.ProcessMessage(posWrapper)

        except Exception as e:
            msg = "Exception @DayTrader.ProcessNewPositionReqSinglePos: {}!".format(str(e))
            self.ProcessCriticalError(e, msg)
            self.CommandsModule.ProcessMessage(ErrorWrapper(Exception(msg)))
        finally:
            self.RoutingLock.release()

    #now we are trading a managed position
    def ProcessNewPositionReqManagedPos(self,wrapper):

        posId = wrapper.GetField(PositionField.PosId)
        try:

            secToTrade = next(iter(list(filter(lambda x: x.Id == posId, self.SecuritiesToTrade.values()))), None)
            if(secToTrade is not None):

                side = wrapper.GetField(PositionField.Side)
                qty = wrapper.GetField(PositionField.Qty)
                account = wrapper.GetField(PositionField.Account)

                self.RoutingLock.acquire()

                newPos = Position(PosId=self.NextPostId,
                                  Security=secToTrade.Security,
                                  Side=side,PriceType=PriceType.FixedAmount,Qty=qty,QuantityType=QuantityType.SHARES,
                                  Account=account,Broker=None,Strategy=None,OrderType=OrdType.Market)

                newPos.ValidateNewPosition()

                secToTrade.ExecutionSummaries[self.NextPostId] = ExecutionSummary(datetime.datetime.now(), newPos)
                secToTrade.PositionSecurities[self.NextPostId] = secToTrade
                self.NextPostId = uuid.uuid4()
                self.RoutingLock.release()

                posWrapper = PositionWrapper(newPos)
                self.OrderRoutingModule.ProcessMessage(posWrapper)

            else:
                raise Exception("Could not find a security to trade (position) for position id {}".format(posId))


        except Exception as e:
            msg = "Exception @DayTrader.ProcessNewPositionReqManagedPos: {}!".format(str(e))
            self.ProcessCriticalError(e, msg)
            self.CommandsModule.ProcessMessage(ErrorWrapper(Exception(msg)))
        finally:
            self.RoutingLock.release()

    def ProcessNewPositionReqThread(self,wrapper):
        try:

            symbol = wrapper.GetField(PositionField.Symbol)
            posId = wrapper.GetField(PositionField.PosId)

            if symbol is not None:
                self.ProcessNewPositionReqSinglePos(wrapper)
            elif posId is not None:
                self.ProcessNewPositionReqManagedPos(wrapper)
            else:
                raise Exception("You need to provide the symbol or positionId for a new position!")

        except Exception as e:
            msg = "Exception @DayTrader.ProcessNewPositionReqThread: {}!".format(str(e))
            self.ProcessCriticalError(e, msg)
            self.CommandsModule.ProcessMessage(ErrorWrapper(Exception(msg)))

    def ProcessCancelAllPositionReqThread(self,wrapper):
        try:
            self.OrderRoutingModule.ProcessMessage(wrapper)
        except Exception as e:
            msg = "Exception @DayTrader.ProcessCancelAllPositionReqThread: {}!".format(str(e))
            #self.ProcessCriticalError(e, msg)
            self.CommandsModule.ProcessMessage(ErrorWrapper(Exception(msg)))

    def ProcessCancelAllPositionReq(self,wrapper):
        try:

            if self.PositionsSynchronization:
                raise Exception("The engine is in the synchronization process. Please try again later!")

            if self.ServiceFailure:
                return CMState.BuildFailure(self.FailureException)

            threading.Thread(target=self.ProcessCancelAllPositionReqThread, args=(wrapper,)).start()

        except Exception as e:
            msg = "Critical Error sending new position to the exchange: {}!".format(str(e))
            self.ProcessCriticalError(e, msg)
            self.CommandsModule.ProcessMessage(ErrorWrapper(Exception(msg)))


    def ProcessNewPositionReq(self,wrapper):

        try:

            if self.PositionsSynchronization:
                raise Exception("The engine is in the synchronization process. Please try again later!")

            if self.ServiceFailure:
                return CMState.BuildFailure(self.FailureException)

            threading.Thread(target=self.ProcessNewPositionReqThread, args=(wrapper,)).start()

        except Exception as e:
            msg = "Critical Error sending new position to the exchange: {}!".format(str(e))
            self.ProcessCriticalError(e, msg)
            self.CommandsModule.ProcessMessage(ErrorWrapper(Exception(msg)))

    def ProcessPortfolioPositionsRequest(self,wrapper):
        
        if self.ServiceFailure:
            return CMState.BuildFailure(self.FailureException)

        threading.Thread(target=self.ProcessPortfolioPositionsRequestThread, args=(wrapper,)).start()

        return CMState.BuildSuccess(self)

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
        try:
            if wrapper.GetAction() == Actions.PORTFOLIO_POSITIONS_REQUEST:
                self.ProcessPortfolioPositionsRequest(wrapper)
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.NEW_POSITION:
                self.ProcessNewPositionReq(wrapper)
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.CANCEL_ALL_POSITIONS:
                self.ProcessCancelAllPositionReq(wrapper)
                return CMState.BuildSuccess(self)
            else:
                raise Exception("DayTrader.ProcessMessage: Not prepared for routing message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessMessage: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

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

            self.CommandsModule = self.InitializeModule(self.Configuration.WebsocketModule, self.Configuration.WebsocketConfigFile)

            self.MarketDataModule =  self.InitializeModule(self.Configuration.IncomingModule,self.Configuration.IncomingConfigFile)

            self.OrderRoutingModule = self.InitializeModule(self.Configuration.OutgoingModule,self.Configuration.OutgoingConfigFile)

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
