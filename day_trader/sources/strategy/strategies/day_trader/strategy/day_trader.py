from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.enums.fields.order_cancel_reject_field import *
from sources.framework.common.enums.fields.position_trading_signal_subscription_field import *
from sources.framework.common.wrappers.error_wrapper import *
from sources.strategy.strategies.day_trader.common.configuration.configuration import Configuration
from sources.framework.common.converters.execution_report_converter import *
from sources.framework.common.enums.fields.execution_report_field import *
from sources.framework.common.enums.fields.position_list_field import *
from sources.framework.common.enums.fields.strategy_backtest_field import *
from sources.framework.common.enums.fields.portfolio_positions_trade_list_request_field import *
from sources.strategy.strategies.day_trader.common.enums.fields.model_param_field import *
from sources.framework.common.enums.fields.portfolio_positions_trade_list_request_field import *
from sources.framework.common.enums.fields.position_field import *
from sources.framework.common.abstract.base_communication_module import *
from sources.framework.business_entities.positions.execution_summary import *
from sources.framework.business_entities.positions.position import *
from sources.framework.common.wrappers.cancel_all_wrapper import *
from sources.strategy.strategies.day_trader.common.wrappers.trading_signal_wrapper  import *
from sources.strategy.strategies.day_trader.common.wrappers.historical_prices_wrapper import *
from sources.framework.common.wrappers.market_data_request_wrapper import *
from sources.framework.common.wrappers.historical_prices_request_wrapper import *
from sources.strategy.strategies.day_trader.common.wrappers.cancel_position_wrapper import *
from sources.framework.common.wrappers.candle_bar_request_wrapper import *
from sources.framework.common.enums.SubscriptionRequestType import *
from sources.strategy.strategies.day_trader.common.converters.market_data_converter import *
from sources.framework.common.dto.cm_state import *
from sources.strategy.common.wrappers.position_list_request_wrapper import *
from sources.framework.common.wrappers.market_data_wrapper import *
from sources.strategy.common.wrappers.position_wrapper import *
from sources.strategy.strategies.day_trader.common.wrappers.model_param_wrapper import *
from sources.strategy.strategies.day_trader.common.wrappers.execution_summary_list_wrapper import *
from sources.strategy.strategies.day_trader.common.wrappers.execution_summary_wrapper import *
from sources.strategy.data_access_layer.day_trading_position_manager import *
from sources.strategy.data_access_layer.model_parameters_manager import *
from sources.strategy.data_access_layer.execution_summary_manager import *
from sources.strategy.data_access_layer.trading_signal_manager import *
from sources.strategy.strategies.day_trader.common.wrappers.portfolio_position_list_wrapper import *
from sources.strategy.strategies.day_trader.common.wrappers.portfolio_position_wrapper import *
from sources.strategy.strategies.day_trader.common.wrappers.strategy_backtest_result_wrapper import *
from sources.strategy.strategies.day_trader.common.util.model_parameters_handler import *
from sources.strategy.strategies.day_trader.common.util.trading_signal_helper import *
from sources.strategy.strategies.day_trader.business_entities.trading_signal import *
from sources.strategy.strategies.day_trader.common.dto.backtest_dto import *
from sources.strategy.strategies.day_trader.business_entities.testers.brooms_tester import *
from sources.strategy.strategies.day_trader.business_entities.testers.rsi_indicator_tester import *
from sources.framework.util.log_helper import *
from dateutil.parser import parse
import threading
import time
from time import mktime
import datetime
import uuid
import queue
import traceback

_BAR_FREQUENCY="BAR_FREQUENCY"
_TRADING_MODE_AUTOMATIC = "AUTOMATIC"
_TRADING_MODE_MANUAL = "MANUAL"

_ACTION_OPEN="OPEN"
_ACTION_CLOSE="CLOSE"
_AUTOMATIC_TRADING_MODE_GENERIC=1
_AUTOMATIC_TRADING_MODE_MACD_RSI=2

class DayTrader(BaseCommunicationModule, ICommunicationModule):

    def __init__(self):#test-develop

        self.LockCandlebar = threading.Lock()
        self.LockMarketData = threading.Lock()
        self.RoutingLock = threading.Lock()
        self.Configuration = None
        self.NextPostId = uuid.uuid4()

        self.PositionSecurities = {}
        self.SingleExecutionSummaries = {}
        self.DayTradingPositions = []
        self.PendingCancels = {}

        self.DayTradingPositionManager = None
        self.ModelParametersManager = None
        self.ExecutionSummaryManager = None
        self.TradingSignalManager = None
        self.TradingSignalHelper=None

        self.ModelParametersHandler = None
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
        self.DayTradingPositionsQueue = queue.Queue(maxsize=1000000)

        self.LastSubscriptionDateTime = None


    def ProcessCriticalError(self, exception,msg):
        self.FailureException=exception
        self.ServiceFailure=True
        self.DoLog(msg, MessageType.ERROR)

    def PublishSummaryThread(self,summary,dayTradingPosId):
        try:
            wrapper =ExecutionSummaryWrapper(summary,dayTradingPosId)
            self.SendToInvokingModule(wrapper)
        except Exception as e:
            self.DoLog("Critical error publishing summary: {}".format(str(e)), MessageType.ERROR)

    def PublishPortfolioPositionThread(self,dayTradingPos):
        try:
            self.DayTradingPositionsQueue.put(dayTradingPos)
            dayTradingPosWrapper = PortfolioPositionWrapper(dayTradingPos)
            self.SendToInvokingModule(dayTradingPosWrapper)
        except Exception as e:
            self.DoLog("Critical error publishing position: {}".format(str(e)), MessageType.ERROR)


    def PublishTradingSignalThread(self,tradingSignal):
        try:

            tradingSignalWrapper = TradingSignalWrapper(tradingSignal)
            self.SendToInvokingModule(tradingSignalWrapper)
        except Exception as e:
            self.DoLog("Critical error publishing trading signal: {}".format(str(e)), MessageType.ERROR)

    def OrdersPersistanceThread(self):

        while True:

            while not self.OrdersQueue.empty():
                try:
                    order = self.OrdersQueue.get()
                    #TODO persist orders!
                except Exception as e:
                    self.DoLog("Error Saving Orders to DB: {}".format(e), MessageType.ERROR)
            time.sleep(int(1))

    def DayTradingPersistanceThread(self):

        while True:

            while not self.DayTradingPositionsQueue.empty():

                try:
                    dayTradingPos = self.DayTradingPositionsQueue.get()
                    self.DayTradingPositionManager.PersistDayTradingPosition(dayTradingPos)

                except Exception as e:
                    self.DoLog("Error Saving Day Trading Position to DB: {}".format(e), MessageType.ERROR)
            time.sleep(int(1))

    def TradesPersistanceThread(self):

        while True:

            while not self.SummariesQueue.empty():

                try:
                    summary = self.SummariesQueue.get()
                    if summary.Position.PosId in self.PositionSecurities:
                        dayTradingPos = self.PositionSecurities[summary.Position.PosId]
                        self.ExecutionSummaryManager.PersistExecutionSummary(summary,dayTradingPos.Id if dayTradingPos is not None else None)
                    else:
                        self.ExecutionSummaryManager.PersistExecutionSummary(summary,None)

                except Exception as e:
                    self.DoLog("Error Saving Trades to DB: {}".format(e), MessageType.ERROR)
            time.sleep(int(1))

    def MarketSubscriptionsThread(self):
        while True:
            try:
                now = datetime.datetime.now()

                resetTime = time.strptime(self.Configuration.MarketDataSubscriptionResetTime, "%I:%M %p")
                todayResetTime = now.replace(hour=resetTime.tm_hour, minute=resetTime.tm_min, second=0,microsecond=0)

                if (self.LastSubscriptionDateTime is None or
                    (self.LastSubscriptionDateTime.day != todayResetTime.day and now> todayResetTime)):

                    self.RoutingLock.acquire()

                    for dayTradingPos in self.DayTradingPositions:
                        dayTradingPos.ResetProfitCounters(now)

                    self.LastSubscriptionDateTime = now

                    self.RequestMarketData()

                    self.RequestPositionList()

                    self.RequestBars()

                    self.RequestHistoricalPrices()

                    if self.RoutingLock.locked():
                        self.RoutingLock.release()

                time.sleep(1)

            except Exception as e:
                msg = "Critical error @DayTrader.MarketSubscriptionsThread:{}".format(str(e))
                self.ProcessCriticalError(e, msg)
                self.SendToInvokingModule(ErrorWrapper(Exception(msg)))
            finally:
                if self.RoutingLock.locked():
                    self.RoutingLock.release()

    def ProcessOrder(self,summary, isRecovery):
        order = summary.Position.GetLastOrder()

        if order is not None and summary.Position.IsFinishedPosition():
            self.OrdersQueue.put(order)
        else:
            self.DoLog("Order not found for position {}".format(summary.Position.PosId), MessageType.DEBUG)

    #If we are in testing mode, we use the Market Data as the real execution price for testing
    def ProcessExecutionPrices(self,dayTradingPos,execReport):

        if(self.Configuration.TestMode and execReport is not None and execReport.AvgPx is not None):
            if dayTradingPos.Security.Symbol in self.MarketData:
                md = self.MarketData[dayTradingPos.Security.Symbol]
                if md.Trade is not None:
                    execReport.AvgPx=md.Trade

    def UpdateManagedPosExecutionSummary(self,dayTradingPos, summary, execReport):

        self.ProcessExecutionPrices(dayTradingPos,execReport)
        summary.UpdateStatus(execReport, marketDataToUse=dayTradingPos.MarketData if dayTradingPos.RunningBacktest else None)
        dayTradingPos.UpdateRouting() #order is important!
        if summary.Position.IsFinishedPosition():
            LogHelper.LogPositionUpdate(self, "Managed Position Finished", summary, execReport)
            #print("Position Status={} Routing={}".format(summary.Position.PosStatus,dayTradingPos.Routing))
            if summary.Position.PosId in self.PendingCancels:
                #print("removing pending cancel for posId {} for security {}".format(summary.Position.PosId,summary.Position.Security.Symbol))
                del self.PendingCancels[summary.Position.PosId]

        else:
            LogHelper.LogPositionUpdate(self, "Managed Position Updated", summary, execReport)

        self.SummariesQueue.put(summary)


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

        try:
            self.SummariesQueue.put(summary)
            #if  (recovered == False):
                #self.SummariesQueue.put(summary)
            #else:
                #self.DoLog( "Critical error saving traded single position with no fill Id.PosId:{}".format(summary.Position.PosId), MessageType.ERROR)

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

    def ProcessExternalTrading(self,posId,exec_report, evalRouting = True):

        try:

            proceExtTradParam = self.ModelParametersHandler.Get(ModelParametersHandler.PROCESS_EXTERNAL_TRADING(),exec_report.Security.Symbol)

            dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == exec_report.Security.Symbol, self.DayTradingPositions))), None)

            if dayTradingPos is not None and (proceExtTradParam is not None and proceExtTradParam.IntValue>0):

                if dayTradingPos.Routing and evalRouting:
                    raise Exception("External trading detected for security {}. It will be ignored as the security has other orders in progress!".format(exec_report.Security.Symbol))

                extPos = Position(PosId=posId,Security=exec_report.Security,Side=exec_report.Side,
                                  PriceType=exec_report.Order.PriceType, Qty=exec_report.OrderQty,
                                  QuantityType=exec_report.Order.QuantityType,Account= exec_report.Order.Account,
                                  Broker=exec_report.Order.Broker, Strategy=exec_report.Order.Strategy,
                                  OrderType=exec_report.Order.OrdType,OrderPrice=exec_report.Order.Price)

                summary = ExecutionSummary(exec_report.TransactTime, extPos)
                self.PositionSecurities[posId]=dayTradingPos

                dayTradingPos.ExecutionSummaries[posId] = summary
                summary.UpdateStatus(exec_report)
                dayTradingPos.UpdateRouting()

                threading.Thread(target=self.PublishPortfolioPositionThread, args=(dayTradingPos,)).start()
                threading.Thread(target=self.PublishSummaryThread, args=(summary, dayTradingPos.Id)).start()

                self.SummariesQueue.put(summary)
            else:
                self.DoLog("Ignoring external trading for security: {}".format(exec_report.Security.Symbol) , MessageType.INFO)
        except Exception as e:
            self.SendToInvokingModule(ErrorWrapper(e))

    def ProcessExecutionReport(self, wrapper):
        try:

            try:
                exec_report = ExecutionReportConverter.ConvertExecutionReport(wrapper)
            except Exception as e:
                self.DoLog("Discarding execution report with bad data: " + str(e), MessageType.INFO)
                #exec_report = ExecutionReportConverter.ConvertExecutionReport(wrapper)
                return

            pos_id = wrapper.GetField(ExecutionReportField.PosId)

            if pos_id is not None:

                self.RoutingLock.acquire()

                if pos_id in self.PositionSecurities:
                    dayTradingPos = self.PositionSecurities[pos_id]
                    if pos_id in dayTradingPos.ExecutionSummaries:
                        summary = dayTradingPos.ExecutionSummaries[pos_id]
                        self.UpdateManagedPosExecutionSummary(dayTradingPos,summary,exec_report)
                        self.ProcessOrder(summary, False)
                        threading.Thread(target=self.PublishPortfolioPositionThread, args=(dayTradingPos,)).start()
                        threading.Thread(target=self.PublishSummaryThread, args=(summary, dayTradingPos.Id)).start()
                        return CMState.BuildSuccess(self)
                    else:
                        self.DoLog("Received execution report for a managed position {},, but we cannot find its execution summary".format(pos_id),MessageType.ERROR)

                elif pos_id in self.SingleExecutionSummaries:
                    #we have a single position
                    summary = self.SingleExecutionSummaries[pos_id]
                    self.UpdateSinglePosExecutionSummary(summary, exec_report)
                    self.ProcessOrder(summary, False)
                    threading.Thread(target=self.PublishSummaryThread, args=(summary, None)).start()
                    return CMState.BuildSuccess(self)
                else:
                    self.ProcessExternalTrading(pos_id,exec_report)
                    #self.DoLog("Received execution report for unknown PosId {}".format(pos_id), MessageType.INFO)
            else:
                raise Exception("Received execution report without PosId")
        except Exception as e:
            traceback.print_exc()
            self.DoLog("Critical error @DayTrader.ProcessExecutionReport: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)
        finally:
            if self.RoutingLock.locked():
                self.RoutingLock.release()

    def LoadConfig(self):
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True


    def LoadExecutionSummaryForPositions(self, backDaysFromParam):

        if(backDaysFromParam is None or backDaysFromParam.IntValue is None):
            raise Exception("Config parameter BACKWARD_DAYS_SUMMARIES_IN_MEMORY was not specified!")

        now = datetime.datetime.utcnow()
        fromDate = now - datetime.timedelta(days=backDaysFromParam.IntValue)

        for dayTradingPosition in self.DayTradingPositions:
            summaries = self.ExecutionSummaryManager.GetExecutionSummaries(dayTradingPosition,fromDate)
            self.DoLog("Loading {} summaries for security {}".format(len(summaries),dayTradingPosition.Security.Symbol),MessageType.INFO)
            for summary in summaries:
                dayTradingPosition.ExecutionSummaries[summary.Position.PosId]=summary
                self.PositionSecurities[summary.Position.PosId]=dayTradingPosition

    def LoadManagers(self):
        self.DayTradingPositionManager = DayTradingPositionManager(self.Configuration.DBConectionString)

        self.ExecutionSummaryManager = ExecutionSummaryManager(self.Configuration.DBConectionString)

        self.DayTradingPositions = self.DayTradingPositionManager.GetDayTradingPositions()

        self.ModelParametersManager = ModelParametersManager(self.Configuration.DBConectionString)

        self.TradingSignalManager = TradingSignalManager(self.Configuration.DBConectionString)

        modelParams = self.ModelParametersManager.GetModelParametersManager()
        self.ModelParametersHandler = ModelParametersHandler(modelParams)

        self.LoadExecutionSummaryForPositions(self.ModelParametersHandler.Get(ModelParametersHandler.BACKWARD_DAYS_SUMMARIES_IN_MEMORY()))

        self.TradingSignalHelper = TradingSignalHelper(self.ModelParametersHandler, self.TradingSignalManager)


    def CancelAllPositions(self):

        for posId in self.SingleExecutionSummaries:
            if(self.SingleExecutionSummaries[posId].Position.IsOpenPosition()):
                pos = self.SingleExecutionSummaries[posId]
                pos.PosStatus = PositionStatus.PendingCancel

        for posId in self.PositionSecurities:
            dayTradingPos = self.PositionSecurities[posId]
            for sPosId in dayTradingPos.ExecutionSummaries:
                pos = dayTradingPos.ExecutionSummaries[sPosId]
                pos.PosStatus = PositionStatus.PendingCancel

        cancelWrapper = CancelAllWrapper()
        self.OutgoingModule.ProcessMessage(cancelWrapper)

    def UpdateManagedPositionOnInitialLoad(self,routePos):

        dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol==routePos.Security.Symbol, self.DayTradingPositions))), None)


        if dayTradingPos is None:
            return False


        try:
            summary = next(iter(list(filter(lambda x:    x.Position.GetLastOrder() is not None
                                                     and routePos.GetLastOrder() is not None
                                                     and x.Position.GetLastOrder().OrderId == routePos.GetLastOrder().OrderId,
                                 dayTradingPos.ExecutionSummaries.values()))), None)

            #if summary is not None and routePos.IsOpenPosition():
            if summary is not None:

                del dayTradingPos.ExecutionSummaries[summary.Position.PosId]
                del self.PositionSecurities[summary.Position.PosId]

                summary.Position.PosId = routePos.PosId
                dayTradingPos.ExecutionSummaries[summary.Position.PosId]=summary
                self.PositionSecurities[summary.Position.PosId]=dayTradingPos
                execReport=routePos.GetLastExecutionReport()

                self.DoLog("Final AvgPx on initial load for order id {}:Prev={} ".format(execReport.Order.OrderId,summary.AvgPx),MessageType.INFO)
                if self.Configuration.TestMode :
                    execReport.AvgPx=summary.AvgPx

                summary.UpdateStatus(execReport)
                self.DoLog("Final AvgPx on initial load for order id {}:Prev={} ".format(execReport.Order.OrderId,summary.AvgPx), MessageType.INFO)
                dayTradingPos.UpdateRouting()

                self.SummariesQueue.put(summary)
                self.DayTradingPositionsQueue.put(dayTradingPos)
                #self.ExecutionSummaryManager.PersistExecutionSummary(summary, dayTradingPos.Id)
                threading.Thread(target=self.PublishSummaryThread, args=(summary, dayTradingPos.Id)).start()
                threading.Thread(target=self.PublishPortfolioPositionThread, args=(dayTradingPos,)).start()
                return True
            else:
                self.DoLog("External trading detected for Symbol:{}".format(dayTradingPos.Security.Symbol),MessageType.INFO)
                return False

        except Exception as e:
            msg = "Critical error @DayTrader.UpdateManagedPositionOnInitialLoad for symbol {} :{}".format(dayTradingPos.Security.Symbol,e)
            self.ProcessCriticalError(e,msg )
            self.SendToInvokingModule(ErrorWrapper(Exception(msg)))
            return True



    def ClosedUnknownStatusSummaries(self,positions):

        for dayTradingPos in self.DayTradingPositions:

            for summary in dayTradingPos.ExecutionSummaries.values():

                if summary.Position.IsOpenPosition():

                    exchPos =   next(iter(list(filter(lambda x: x.GetLastOrder() is not None and summary.Position.GetLastOrder() is not None
                                                                and summary.Position.GetLastOrder().OrderId == x.GetLastOrder().OrderId,positions))), None)
                    if exchPos is None:
                        summary.Position.PosStatus=PositionStatus.Unknown
                        summary.LeavesQty = 0
                        summary.Position.LeavesQty=0
                        self.SummariesQueue.put(summary)
                        threading.Thread(target=self.PublishSummaryThread, args=(summary, dayTradingPos.Id)).start()


    def ProcessPositionList(self, wrapper):
        try:
            success = wrapper.GetField(PositionListField.Status)

            if success:
                positions = wrapper.GetField(PositionListField.Positions)

                self.DoLog("Received list of Open Positions: {} positions".format(Position.CountOpenPositions(self, positions)),
                    MessageType.INFO)
                i=0

                self.RoutingLock.acquire()
                for pos in positions:

                    summary = ExecutionSummary(datetime.datetime.now(), pos)
                    if pos.GetLastExecutionReport() is not None:

                        if not self.UpdateManagedPositionOnInitialLoad(pos):
                            processExtTradParam = self.ModelParametersHandler.Get(ModelParametersHandler.PROCESS_EXTERNAL_TRADING(), pos.Security.Symbol)
                            if processExtTradParam.IntValue == 1:
                                self.ProcessExternalTrading(pos.PosId,pos.GetLastExecutionReport(),evalRouting=False)
                            else:
                                self.UpdateSinglePosExecutionSummary(summary, pos.GetLastExecutionReport(),recovered=True)  # we will persist only if we have an existing position
                                self.ProcessOrder(summary,True)
                    else:
                        self.DoLog("Could not find execution report for position id {}".format(pos.PosId),MessageType.ERROR)
                self.ClosedUnknownStatusSummaries(positions)

                self.DoLog("Process ready to receive commands and trade", MessageType.INFO)
            else:
                exception= wrapper.GetField(PositionListField.Error)
                raise exception

        except Exception as e:
            self.ProcessCriticalError(e,"Critical error @DayTrader.ProcessPositionList:{}".format(e))
        finally:
            self.PositionsSynchronization = False
            if self.RoutingLock.locked():
                self.RoutingLock.release()

    def ProcessMarketData(self,wrapper):

        md = MarketDataConverter.ConvertMarketData(wrapper)

        try:
            self.LockMarketData.acquire()
            md = MarketDataConverter.ConvertMarketData(wrapper)

            LogHelper.LogPublishMarketDataOnSecurity("DayTrader Recv MarketData", self, md.Security.Symbol,md)

            dayTradingPositions = list(filter(lambda x: x.Security.Symbol == md.Security.Symbol, self.DayTradingPositions))

            for dayTradingPos in dayTradingPositions:
                if not dayTradingPos.RunningBacktest:
                    self.MarketData[md.Security.Symbol] = md
                    if(dayTradingPos.MarketData is not None and dayTradingPos.MarketData.Trade!=md.Trade):
                        dayTradingPos.MarketData=md
                        threading.Thread(target=self.PublishPortfolioPositionThread, args=(dayTradingPos,)).start()

                    else:
                        dayTradingPos.MarketData=md
                    dayTradingPos.CalculateCurrentDayProfits(md)

                    LogHelper.LogPublishMarketDataOnSecurity("DayTrader Proc MarketData", self, md.Security.Symbol, md)

        except Exception as e:
            traceback.print_exc()
            self.ProcessErrorInMethod("@DayTrader.ProcessMarketData", e,md.Security.Symbol is md if not None else None)
        finally:
            self.LockMarketData.release()

    def ProcessErrorInMethod(self,method,e, symbol=None):
        try:
            msg = "Error @{} for security {}:{} ".format(method, symbol if symbol is not None else "-",str(e))
            error = ErrorWrapper(Exception(msg))
            self.ProcessError(error)
            self.DoLog(msg, MessageType.ERROR)
        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessError2: " + str(e), MessageType.ERROR)

    def SendToInvokingModule(self,wrapper):
        try:
           self.CommandsModule.ProcessMessage(wrapper)
        except Exception as e:
            self.DoLog("Critical error @DayTrader.SendToInvokingModule.:{}".format(str(e)), MessageType.ERROR)

    def ProcessError(self,wrapper):
        try:
           self.CommandsModule.ProcessMessage(wrapper)

        except Exception as e:
            self.DoLog("Critical error @DayTrader.ProcessError: " + str(e), MessageType.ERROR)

    def ProcessHistoricalPrices(self,wrapper):

        security = MarketDataConverter.ConvertHistoricalPrices(wrapper)

        try:

            self.HistoricalPrices[security.Symbol]=security.MarketDataArr

            datTradingPos = next(iter(list(filter(lambda x:  x.Security.Symbol==security.Symbol, self.DayTradingPositions))), None)

            if(datTradingPos is not None):
                try:
                    datTradingPos.CalculateStdDevForLastNDays(security.MarketDataArr,
                                                              self.ModelParametersHandler.Get(ModelParametersHandler.HISTORICAL_PRICES_PAST_DAYS_STD_DEV()))

                    datTradingPos.DailyRSIIndicator.UpdateDaily(security.MarketDataArr,self.ModelParametersHandler.Get(ModelParametersHandler.HISTORICAL_PRICES_PAST_DAYS_DAILY_RSI()).IntValue)
                    #print("RSI calculated for symbol {}:{}".format(security.Symbol,datTradingPos.DailyRSIIndicator.RSI))
                except Exception as e:
                    self.DoLog(str(e),MessageType.ERROR)
                    self.SendToInvokingModule(ErrorWrapper(str(e)))


            self.DoLog("Historical prices successfully loaded for symbol {} ".format(security.Symbol), MessageType.INFO)
        except Exception as e:
            self.ProcessErrorInMethod("@DayTrader.ProcessHistoricalPrices",e,security.Symbol if security is not None else None)

    def UpdateTradingSignals(self, candlebar,cbDict):

        try:

            dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))),None)

            if dayTradingPos is not None and dayTradingPos.ShowTradingRecommndations:


                if dayTradingPos.TerminalClose:
                    # Publish Terminal Close
                    self.DoLog("dayTradingPos.TerminalClose: cond={}".format(dayTradingPos.TerminalCloseCond), MessageType.INFO)
                    threading.Thread(target=self.PublishTradingSignalThread,
                                     args=(TradingSignal(security=dayTradingPos.Security,
                                                         signal=dayTradingPos.TerminalCloseCond,
                                                         recommendation=dayTradingPos._TERMINALLY_CLOSED()),)).start()
                    return 

                if not dayTradingPos.Open():

                    openLong =  self.EvaluateMACDRSILongTrade(dayTradingPos, dayTradingPos.Security.Symbol , cbDict, candlebar)
                    openShort=  self.EvaluateMACDRSIShorTrade(dayTradingPos, dayTradingPos.Security.Symbol , cbDict, candlebar)

                    if openLong is not None:
                        # Publish TradingSignal GO LONG NOW
                        threading.Thread(target=self.PublishTradingSignalThread,
                                         args=(TradingSignal(security=dayTradingPos.Security,
                                                             signal=openLong,
                                                             recommendation=dayTradingPos._REC_GO_LONG_NOW()),)).start()
                    elif openShort is not None:
                        # Publish TradingSignal GO SHORT NOW
                        threading.Thread(target=self.PublishTradingSignalThread,
                                         args=(TradingSignal(security=dayTradingPos.Security,
                                                             signal=openShort,
                                                             recommendation=dayTradingPos._REC_GO_SHORT_NOW()),)).start()
                    else:
                        #Publish STAY OUT
                        threading.Thread(target=self.PublishTradingSignalThread,
                                         args=(TradingSignal(security=dayTradingPos.Security,
                                                             signal="",
                                                             recommendation=dayTradingPos._REC_STAY_OUT()),)).start()
                else:
                    if dayTradingPos.GetNetOpenShares()>0:
                        closeLong = self.EvaluateClosingMACDRSILongPositions(candlebar,cbDict,runClose=False)
                        if closeLong is not None:
                            #Publish Trading Signal EXIT LONG NOW
                            threading.Thread(target=self.PublishTradingSignalThread,
                                             args=(TradingSignal(security=dayTradingPos.Security,
                                                                 signal=closeLong,
                                                                 recommendation=dayTradingPos._REC_EXIT_LONG_NOW()),)).start()
                        else:
                            #Publish Trading Signal STAY LONG
                            threading.Thread(target=self.PublishTradingSignalThread,
                                             args=(TradingSignal(security=dayTradingPos.Security,
                                                                 signal="",
                                                                 recommendation=dayTradingPos._REC_STAY_LONG()),)).start()
                    elif dayTradingPos.GetNetOpenShares()<0:
                        closeShort = self.EvaluateClosingMACDRSIShortPositions(candlebar,cbDict,runClose=False)
                        if closeShort is not None:
                            #Publish Trading Signal EXIT SHORT NOW
                            threading.Thread(target=self.PublishTradingSignalThread,
                                             args=(TradingSignal(security=dayTradingPos.Security,
                                                                 signal=closeShort,
                                                                 recommendation=dayTradingPos._REC_EXIT_SHORT_NOW()),)).start()
                        else:
                            #Publish Trading Signal STAY SHORT
                            threading.Thread(target=self.PublishTradingSignalThread,
                                             args=(TradingSignal(security=dayTradingPos.Security,
                                                                 signal="",
                                                                 recommendation=dayTradingPos._REC_STAY_SHORT()),)).start()
        except Exception as e:
            msg = "Critical error @DayTrader.UpdateTradingSignals.:{}".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))



    def UpdateTechnicalAnalysisParameters(self, candlebar,candlebarDict):
        dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))),None)
        if dayTradingPos is not None:
            #prevLastProcessedTime = dayTradingPos.MinuteSmoothedRSIIndicator.LastProcessedDateTime
            dayTradingPos.MinuteNonSmoothedRSIIndicator.Update(candlebarDict.values(),
                                                    self.ModelParametersHandler.Get(ModelParametersHandler.CANDLE_BARS_NON_SMOTHED_MINUTES_RSI()).IntValue)
            dayTradingPos.MinuteSmoothedRSIIndicator.Update(candlebarDict.values(),
                                                    self.ModelParametersHandler.Get(ModelParametersHandler.CANDLE_BARS_SMOOTHED_MINUTES_RSI()).IntValue)

            dayTradingPos.MACDIndicator.Update(candlebarDict.values(),
                                               slow=self.ModelParametersHandler.Get(ModelParametersHandler.MACD_SLOW()).IntValue,
                                               fast=self.ModelParametersHandler.Get(ModelParametersHandler.MACD_FAST()).IntValue,
                                               signal=self.ModelParametersHandler.Get(ModelParametersHandler.MACD_SIGNAL()).IntValue,
                                               #absMaxMSPeriod= self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_ABS_MAX_MS_PERIOD()).IntValue
                                               absMaxMSPeriod=0
                                               )


            dayTradingPos.BollingerIndicator.Update(candlebarDict.values(),
                                                    self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_TPMA_A()),
                                                    self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_TPSD_B()),
                                                    self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BOLLUP_C()),
                                                    self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BOLLDN_D()),
                                                    self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BOLLINGER_K()),
                                                    self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BOLLINGER_L())
                                                    )


            dayTradingPos.MSStrengthIndicator.Update(candlebarDict.values(),dayTradingPos.MACDIndicator.MS,
                                                     self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_TPSD_B()),
                                                     self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_MS_STRENGTH_M()),
                                                     self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_MS_STRENGTH_N()),
                                                     self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_MS_STRENGTH_P()),
                                                     self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_MS_STRENGTH_Q()),
                                                     )


            dayTradingPos.BroomsIndicator.Update(candlebarDict.values(),
                                                 dayTradingPos.BollingerIndicator.TP,
                                                 dayTradingPos.BollingerIndicator.BSI,
                                                 dayTradingPos.MSStrengthIndicator.MSI,
                                                 dayTradingPos.MinuteNonSmoothedRSIIndicator.RSI,
                                                 dayTradingPos.MACDIndicator.MS,
                                                 dayTradingPos.MinuteSmoothedRSIIndicator.GetRSIReggr(30),#RSI30smSL
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_NN()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_PP()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_QQ()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_RR()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_SS()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_R()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_S()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_T()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_U()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_V()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_W()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_X()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_Y()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_Z()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_CC()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_DD()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_EE()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_TT()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_UU()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_VV()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_WW()),
                                                 self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_XX())
                                                 )


    def EvaluateGenericLongTrade(self,dayTradingPos,symbol,cbDict,candlebar):
        if (dayTradingPos.EvaluateValidTimeToEnterTrade(candlebar,
                self.ModelParametersHandler.Get(ModelParametersHandler.LOW_VOL_ENTRY_THRESHOLD(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_ENTRY_THRESHOLD(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.LOW_VOL_FROM_TIME(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.LOW_VOL_TO_TIME(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_FROM_TIME_1(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_TO_TIME_1(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_FROM_TIME_2(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_TO_TIME_2(), symbol),
                )

                and not dayTradingPos.TerminalClose

                and dayTradingPos.EvaluateClosingTerminalCondition(list(cbDict.values()),
                   self.ModelParametersHandler.Get(ModelParametersHandler.END_OF_DAY_LIMIT(),symbol),
                   self.ModelParametersHandler.Get(ModelParametersHandler.TAKE_GAIN_LIMIT(),symbol),
                   self.ModelParametersHandler.Get(ModelParametersHandler.STOP_LOSS_LIMIT(),symbol)) is None

        ):

            if dayTradingPos.EvaluateGenericLongTrade(
                    self.ModelParametersHandler.Get(ModelParametersHandler.DAILY_BIAS(), symbol),
                    self.ModelParametersHandler.Get(ModelParametersHandler.DAILY_SLOPE(), symbol),
                    self.ModelParametersHandler.Get(ModelParametersHandler.MAXIM_PCT_CHANGE_3_MIN(), symbol),
                    self.ModelParametersHandler.Get(ModelParametersHandler.POS_LONG_MAX_DELTA(), symbol),
                    self.ModelParametersHandler.Get(ModelParametersHandler.NON_SMOOTHED_RSI_LONG_THRESHOLD(), symbol),
                    list(cbDict.values())):

                self.DoLog("Generic Automatic = Running long trade for symbol {}".format(dayTradingPos.Security.Symbol), MessageType.INFO)
                self.TradingSignalHelper.PersistTradingSignal(dayTradingPos, TradingSignalHelper._ACTION_OPEN(),
                                                              Side.Buy, dayTradingPos.GetStatisticalParameters(list(cbDict.values())), candlebar, self)
                self.ProcessNewPositionReqManagedPos(dayTradingPos, Side.Buy, dayTradingPos.SharesQuantity,self.Configuration.DefaultAccount)
                dayTradingPos.Routing=True
                return True
        return False #Nothing happens

    def EvaluateGenericShortTrade(self, dayTradingPos, symbol, cbDict, candlebar):

        if (dayTradingPos.EvaluateValidTimeToEnterTrade(candlebar,
                self.ModelParametersHandler.Get(ModelParametersHandler.LOW_VOL_ENTRY_THRESHOLD(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_ENTRY_THRESHOLD(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.LOW_VOL_FROM_TIME(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.LOW_VOL_TO_TIME(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_FROM_TIME_1(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_TO_TIME_1(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_FROM_TIME_2(), symbol),
                self.ModelParametersHandler.Get(ModelParametersHandler.HIGH_VOL_TO_TIME_2(), symbol),
                )
                and not dayTradingPos.TerminalClose
                and dayTradingPos.EvaluateClosingTerminalCondition(list(cbDict.values()),
                   self.ModelParametersHandler.Get(ModelParametersHandler.END_OF_DAY_LIMIT(),symbol),
                   self.ModelParametersHandler.Get( ModelParametersHandler.TAKE_GAIN_LIMIT(),symbol),
                   self.ModelParametersHandler.Get(ModelParametersHandler.STOP_LOSS_LIMIT(),symbol)) is None
            ):

            if dayTradingPos.EvaluateGenericShortTrade(
                    self.ModelParametersHandler.Get(ModelParametersHandler.DAILY_BIAS(), symbol),
                    self.ModelParametersHandler.Get(ModelParametersHandler.DAILY_SLOPE(), symbol),
                    self.ModelParametersHandler.Get(ModelParametersHandler.MAXIM_SHORT_PCT_CHANGE_3_MIN(), symbol),
                    self.ModelParametersHandler.Get(ModelParametersHandler.POS_SHORT_MAX_DELTA(), symbol),
                    self.ModelParametersHandler.Get(ModelParametersHandler.NON_SMOOTHED_RSI_SHORT_THRESHOLD(), symbol),
                    list(cbDict.values())):
                self.DoLog("Generic Automatic = Running short trade for symbol {}".format(dayTradingPos.Security.Symbol), MessageType.INFO)
                self.TradingSignalHelper.PersistTradingSignal(dayTradingPos, TradingSignalHelper._ACTION_OPEN(),
                                                              Side.SellShort, dayTradingPos.GetStatisticalParameters(list(cbDict.values())), candlebar, self)
                self.ProcessNewPositionReqManagedPos(dayTradingPos, Side.Sell, dayTradingPos.SharesQuantity,self.Configuration.DefaultAccount)
                dayTradingPos.Routing = True
                return True

            return False


        return False #Nothing happens


    def EvaluateOpeningGenericAutomaticTrading(self,dayTradingPos,symbol,cbDict,candlebar):
        return  self.EvaluateGenericLongTrade(dayTradingPos, symbol, cbDict, candlebar) or \
                self.EvaluateGenericShortTrade(dayTradingPos, symbol, cbDict, candlebar)

    def EvaluateMACDRSILongTrade(self,dayTradingPos,symbol,cbDict,candlebar):

        terminallyClosed = dayTradingPos.TerminalClose
        terminalCond = dayTradingPos.EvaluateClosingTerminalCondition(list(cbDict.values()),
                     self.ModelParametersHandler.Get(ModelParametersHandler.END_OF_DAY_LIMIT(),symbol),
                     self.ModelParametersHandler.Get(ModelParametersHandler.TAKE_GAIN_LIMIT(),symbol),
                     self.ModelParametersHandler.Get(ModelParametersHandler.STOP_LOSS_LIMIT(),symbol))



        if (not terminallyClosed  and  terminalCond is  None):

               longCondition =  dayTradingPos.EvaluateMACDRSILongTrade(self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_A(),symbol),
                                  self.ModelParametersHandler.Get( ModelParametersHandler.M_S_MIN_B(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MIN_B_B(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.RSI_30_SLOPE_SKIP_5_C(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_CC(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BIAS(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_D(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_D_D(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_MAX_E(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_F(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_F_F(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.RSI_30_SLOPE_SKIP_10_G(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.ABS_M_S_MAX_MIN_LAST_5_H(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.ABS_M_S_MAX_MIN_LAST_5_H_H(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.SEC_5_MIN_SLOPE_I(), symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.RSI_14_SLOPE_SKIP_3_V(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.M_S_3_SLOPE_X(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.M_S_3_SLOPE_X_X(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_SMOOTHED_MODE(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_ABS_MAX_MS_PERIOD(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_LONG_RULE_1(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_LONG_RULE_2(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_LONG_RULE_3(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_LONG_RULE_4(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_LONG_RULE_BROOMS(),symbol),
                                  self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_START_TRADING(),symbol),
                                  list(cbDict.values()))
               if longCondition is not None:

                   self.DoLog("MACD/RSI = Running long trade for symbol {}".format(dayTradingPos.Security.Symbol),MessageType.INFO)
                   self.TradingSignalHelper.PersistMACDRSITradingSignal(dayTradingPos,TradingSignalHelper._ACTION_OPEN(), Side.Buy,candlebar, self,condition=longCondition)
                   self.ProcessNewPositionReqManagedPos(dayTradingPos, Side.Buy, dayTradingPos.SharesQuantity,self.Configuration.DefaultAccount)
                   dayTradingPos.Routing = True
                   #print("Open Pos Long --> Routing=True")
                   dayTradingPos.MACDIndicator.UpdateLastTradeTimestamp()
                   return longCondition
               else:
                   return None

        else:
            return terminalCond if not terminallyClosed else dayTradingPos._TERMINALLY_CLOSED

    def EvaluateMACDRSIShorTrade(self,  dayTradingPos, symbol, cbDict, candlebar):

        terminallyClosed = dayTradingPos.TerminalClose
        terminalCond = dayTradingPos.EvaluateClosingTerminalCondition(list(cbDict.values()),
                            self.ModelParametersHandler.Get(ModelParametersHandler.END_OF_DAY_LIMIT(),symbol),
                            self.ModelParametersHandler.Get(ModelParametersHandler.TAKE_GAIN_LIMIT(),symbol),
                            self.ModelParametersHandler.Get(ModelParametersHandler.STOP_LOSS_LIMIT(),symbol))

        if (not terminallyClosed  and terminalCond is None):


            shortCondition = dayTradingPos.EvaluateMACDRSIShortTrade(
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_A(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MIN_B(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MIN_B_B(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.RSI_30_SLOPE_SKIP_5_C(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_D(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_D_D(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_MAX_E(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_F(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_F_F(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.RSI_30_SLOPE_SKIP_10_G(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.ABS_M_S_MAX_MIN_LAST_5_H(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.ABS_M_S_MAX_MIN_LAST_5_H_H(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.SEC_5_MIN_SLOPE_I(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.RSI_14_SLOPE_SKIP_3_V(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_3_SLOPE_X(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.M_S_3_SLOPE_X_X(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_Z(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.BROOMS_BIAS(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_SMOOTHED_MODE(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_ABS_MAX_MS_PERIOD(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_SHORT_RULE_1(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_SHORT_RULE_2(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_SHORT_RULE_3(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_SHORT_RULE_4(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_OPEN_SHORT_RULE_BROOMS(), symbol),
                                                                    self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_START_TRADING(), symbol),
                                                                    list(cbDict.values()))

            if shortCondition is not None:

                self.DoLog("MACD/RSI = Running short trade for symbol {}".format(dayTradingPos.Security.Symbol),MessageType.INFO)
                self.TradingSignalHelper.PersistMACDRSITradingSignal(dayTradingPos, TradingSignalHelper._ACTION_OPEN(),Side.SellShort, candlebar,
                                                                     self,condition=shortCondition)
                self.ProcessNewPositionReqManagedPos(dayTradingPos, Side.Sell, dayTradingPos.SharesQuantity,
                                                     self.Configuration.DefaultAccount)
                dayTradingPos.Routing = True
                #print("Open Pos Short --> Routing=True")
                dayTradingPos.MACDIndicator.UpdateLastTradeTimestamp()
                return shortCondition
            else:
                return None
        else:
            return terminalCond if not terminallyClosed else dayTradingPos._TERMINALLY_CLOSED

    def EvaluateOpeningMACDRSIAutomaticTrading(self,dayTradingPos,symbol,cbDict,candlebar):

        return self.EvaluateMACDRSILongTrade(dayTradingPos,symbol,cbDict,candlebar) or \
               self.EvaluateMACDRSIShorTrade(dayTradingPos,symbol,cbDict,candlebar)


    def EvaluateOpeningPositions(self, candlebar,cbDict):

        symbol = candlebar.Security.Symbol

        tradingMode = self.ModelParametersHandler.Get(ModelParametersHandler.TRADING_MODE(),symbol)
        dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))),None)

        if tradingMode.StringValue == _TRADING_MODE_AUTOMATIC or dayTradingPos.RunningBacktest:

            if dayTradingPos is not None:

                automTradingModeModelParam = self.ModelParametersHandler.Get(ModelParametersHandler.AUTOMATIC_TRADING_MODE(), symbol)

                if automTradingModeModelParam is None or automTradingModeModelParam.IntValue is None:
                    raise Exception("Critical error for automatic trading: You must specify parameter AUTOMATIC_TRADING_MODE")

                if  automTradingModeModelParam.IntValue==_AUTOMATIC_TRADING_MODE_GENERIC:#First version of the auomatic trading algo
                    return self.EvaluateOpeningGenericAutomaticTrading(dayTradingPos,symbol,cbDict,candlebar)
                elif  automTradingModeModelParam.IntValue==_AUTOMATIC_TRADING_MODE_MACD_RSI:#Second version of the auomatic trading algo
                    return self.EvaluateOpeningMACDRSIAutomaticTrading(dayTradingPos,symbol,cbDict,candlebar)
                else:
                    raise Exception("Unknown automatic trading mode {}".format(automTradingModeModelParam.IntValue))


            else:
                msg = "Could not find Day Trading Position for candlebar symbol {}. Please Resync.".format(candlebar.Security.Symbol)
                self.SendToInvokingModule(ErrorWrapper(Exception(msg)))
                self.DoLog(msg, MessageType.ERROR)
                return False
        else:
            return False

    def EvaluateClosingGenericAutomaticTrading(self,cbDict,candlebar):
        closingLong = self.EvaluateClosingGenericLongPositions(candlebar, cbDict)
        closingShort = self.EvaluateClosingGenericShortPositions(candlebar, cbDict)

        return closingLong is not None or closingShort is not None

    def EvaluateClosingMACDRSIAutomaticTrading(self,cbDict,candlebar):
        closingLong = self.EvaluateClosingMACDRSILongPositions(candlebar,cbDict)
        closingShort = self.EvaluateClosingMACDRSIShortPositions(candlebar,cbDict)

        return closingLong is not None or closingShort is not None

    def EvaluateClosingPositions(self, candlebar, cbDict):
        symbol = candlebar.Security.Symbol

        tradingMode = self.ModelParametersHandler.Get(ModelParametersHandler.TRADING_MODE(), symbol)

        dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))),None)

        if tradingMode.StringValue == _TRADING_MODE_AUTOMATIC or dayTradingPos.RunningBacktest:

            if dayTradingPos is not None:

                automTradingModeModelParam = self.ModelParametersHandler.Get(ModelParametersHandler.AUTOMATIC_TRADING_MODE(),symbol)

                if automTradingModeModelParam is None or automTradingModeModelParam.IntValue is None:
                    raise Exception("Critical error for automatic trading: You must specify parameter AUTOMATIC_TRADING_MODE")

                if automTradingModeModelParam.IntValue == _AUTOMATIC_TRADING_MODE_GENERIC:  # First version of the auomatic trading algo
                    return self.EvaluateClosingGenericAutomaticTrading( cbDict,candlebar )
                elif automTradingModeModelParam.IntValue == _AUTOMATIC_TRADING_MODE_MACD_RSI:  # Second version of the auomatic trading algo
                    return self.EvaluateClosingMACDRSIAutomaticTrading( cbDict, candlebar)
                else:
                    raise Exception("Unknown automatic trading mode {}".format(automTradingModeModelParam.IntValue))

            else:
                msg = "Could not find Day Trading Position for candlebar symbol {} @EvaluateClosingPositions. Please Resync.".format(candlebar.Security.Symbol)
                self.SendToInvokingModule(ErrorWrapper(Exception(msg)))
                self.DoLog(msg, MessageType.ERROR)
                return False
        else:
            return False

    def RunClose(self,dayTradingPos,side,statisticalParam,candlebar, text=None, generic = False, closingCond = None):

        if dayTradingPos.Routing:
            for summary in dayTradingPos.GetOpenSummaries():

                # we just cancel summaries whose side is different than the closing side. We don't want to cancel the close
                if  (
                    summary.Position.PosId not in self.PendingCancels  and
                    (dayTradingPos.GetNetOpenShares() ==0 or summary.Position.Side !=side)):
                    self.DoLog("Cancelling order previously to closing position for symbol {}".format(dayTradingPos.Security.Symbol),MessageType.INFO)
                    self.PendingCancels[summary.Position.PosId] = summary
                    cxlWrapper = CancelPositionWrapper(summary.Position.PosId)
                    state= self.OrderRoutingModule.ProcessMessage(cxlWrapper)
                    if not state.Success:
                        self.ProcessError(state.Exception)

        else:
            netShares = dayTradingPos.GetNetOpenShares()
            if netShares!=0: #if there is something to close
                # print("Now we do close positions for security {} for net open shares {}".format(dayTradingPos.Security.Symbol, netShares))

                if generic:
                    self.TradingSignalHelper.PersistTradingSignal(dayTradingPos, TradingSignalHelper._ACTION_CLOSE(),
                                                                  self.TranslateSide(dayTradingPos,side), statisticalParam,
                                                                  candlebar, self,closingCond)
                else:
                    self.TradingSignalHelper.PersistMACDRSITradingSignal(dayTradingPos,TradingSignalHelper._ACTION_CLOSE(),
                                                                         self.TranslateSide(dayTradingPos,side),candlebar,
                                                                         self,closingCond)

                self.ProcessNewPositionReqManagedPos(dayTradingPos,side,netShares if netShares > 0 else netShares * (-1),
                                                     self.Configuration.DefaultAccount,text=text)


    def EvaluateClosingForManualConditions(self,candlebar,cbDict):

        tradingMode = self.ModelParametersHandler.Get(ModelParametersHandler.TRADING_MODE(), candlebar.Security.Symbol)

        if tradingMode.StringValue == _TRADING_MODE_MANUAL:
            dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))),None)

            if dayTradingPos is not None:

                if dayTradingPos.EvaluateClosingOnStopLoss(candlebar):
                    self.RunClose(dayTradingPos,Side.Sell if dayTradingPos.GetNetOpenShares() > 0 else Side.Buy,
                                  dayTradingPos.GetStatisticalParameters(list(cbDict.values())), candlebar,
                                  text="Closing for stop loss",closingCond="Stop Loss")

                if dayTradingPos.EvaluateClosingOnTakeProfit(candlebar):
                    self.RunClose(dayTradingPos,Side.Sell if dayTradingPos.GetNetOpenShares() > 0 else Side.Buy,
                                  dayTradingPos.GetStatisticalParameters(list(cbDict.values())), candlebar,
                                  text="Closing on take profit",closingCond="Take Profit")

                if dayTradingPos.EvaluateClosingOnEndOfDay(candlebar,
                                                           self.ModelParametersHandler.Get(ModelParametersHandler.END_OF_DAY_LIMIT(),dayTradingPos.Security.Symbol)):
                    self.RunClose(dayTradingPos,Side.Sell if dayTradingPos.GetNetOpenShares() > 0 else Side.Buy,
                                  dayTradingPos.GetStatisticalParameters(list(cbDict.values())), candlebar,
                                  text="Closing on end of day for manual trades",closingCond="End of Day")

            else:
                msg = "Could not find Day Trading Position for candlebar symbol {}. Please Resync.".format(candlebar.Security.Symbol)
                self.SendToInvokingModule(ErrorWrapper(Exception(msg)))
                self.DoLog(msg, MessageType.ERROR)

    def EvaluateClosingGenericLongPositions(self, candlebar,cbDict):

        symbol = candlebar.Security.Symbol

        tradingMode = self.ModelParametersHandler.Get(ModelParametersHandler.TRADING_MODE(),symbol)

        if tradingMode.StringValue == _TRADING_MODE_AUTOMATIC:

            dayTradingPos =  next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))), None)

            if dayTradingPos is not None:

                closingCond = dayTradingPos.EvaluateClosingGenericLongTrade(list(cbDict.values()),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.MAX_GAIN_FOR_DAY(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.PCT_MAX_GAIN_CLOSING(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.MAX_LOSS_FOR_DAY(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.PCT_MAX_LOSS_CLOSING(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.TAKE_GAIN_LIMIT(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.STOP_LOSS_LIMIT(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.PCT_SLOPE_TO_CLOSE_LONG(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.END_OF_DAY_LIMIT(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.NON_SMOOTHED_RSI_SHORT_THRESHOLD(),symbol),
                                                )

                if closingCond is not None:

                    self.RunClose(dayTradingPos,Side.Sell if dayTradingPos.GetNetOpenShares() > 0 else Side.Buy,
                                  dayTradingPos.GetStatisticalParameters(list(cbDict.values())), candlebar,
                                  closingCond=closingCond)

            else:
                msg = "Could not find Day Trading Position for candlebar symbol {} @EvaluateClosingGenericLongPositions. Please Resync.".format(candlebar.Security.Symbol)
                self.SendToInvokingModule(ErrorWrapper(Exception(msg)))
                self.DoLog(msg, MessageType.ERROR)

    def EvaluateClosingGenericShortPositions(self, candlebar,cbDict):

        symbol = candlebar.Security.Symbol

        tradingMode = self.ModelParametersHandler.Get(ModelParametersHandler.TRADING_MODE(),symbol)

        if tradingMode.StringValue == _TRADING_MODE_AUTOMATIC:

            dayTradingPos =  next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))), None)

            if dayTradingPos is not None:

                closingCond = dayTradingPos.EvaluateClosingGenericShortTrade(list(cbDict.values()),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.MAX_GAIN_FOR_DAY(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.PCT_MAX_GAIN_CLOSING(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.MAX_LOSS_FOR_DAY(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.PCT_MAX_LOSS_CLOSING(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.TAKE_GAIN_LIMIT(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.STOP_LOSS_LIMIT(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.PCT_SLOPE_TO_CLOSE_SHORT(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.END_OF_DAY_LIMIT(),symbol),
                                                self.ModelParametersHandler.Get(ModelParametersHandler.NON_SMOOTHED_RSI_LONG_THRESHOLD(),symbol)
                                                )

                if closingCond is not None:
                    #print("closing short position for security {}".format(dayTradingPos.Security.Symbol))

                    self.RunClose(dayTradingPos,Side.Sell if dayTradingPos.GetNetOpenShares() > 0 else Side.Buy,
                                  dayTradingPos.GetStatisticalParameters(list(cbDict.values())), candlebar,
                                  closingCond=closingCond)

            else:
                msg = "Could not find Day Trading Position for candlebar symbol {} @EvaluateClosingGenericShortPositions. Please Resync.".format(candlebar.Security.Symbol)
                self.SendToInvokingModule(ErrorWrapper(Exception(msg)))
                self.DoLog(msg, MessageType.ERROR)

    def EvaluateClosingMACDRSILongPositions(self, candlebar, cbDict, runClose=True):
        symbol = candlebar.Security.Symbol

        dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))),None)

        if dayTradingPos is not None:

            closingCond = dayTradingPos.EvaluateClosingMACDRSILongTrade(list(cbDict.values()),self.ModelParametersHandler.Get( ModelParametersHandler.M_S_NOW_A(), symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_MAX_GAIN_J(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_MAX_GAIN_J_J(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_GAIN_NOW_MAX_K(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.RSI_30_SLOPE_SKIP_5_EXIT_L(),symbol),
                                                                        self.ModelParametersHandler.Get( ModelParametersHandler.M_S_NOW_EXIT_N(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_EXIT_N_N(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_EXIT_N_BIS(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_EXIT_N_N_BIS(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_MAX_MIN_EXIT_P(),symbol),
                                                                        self.ModelParametersHandler.Get( ModelParametersHandler.M_S_NOW_EXIT_Q(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_EXIT_Q_Q(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.RSI_30_SLOPE_SKIP_10_EXIT_R(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_EXIT_S(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_EXIT_S_S(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.SEC_5_MIN_SLOPE_EXIT_T(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_U(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_U_U(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_W(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_W_W(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_STOP_LOSS_EXIT_Y(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_Z(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_Z_Z(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.END_OF_DAY_LIMIT(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.TAKE_GAIN_LIMIT(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.STOP_LOSS_LIMIT(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_SMOOTHED_MODE(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_ABS_MAX_MS_PERIOD(), symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_1(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_2(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_3(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_4(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_5(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_6(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_7(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_8(),symbol),
                                                                        self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_LONG_RULE_9(),symbol)
                                                                        )

            if closingCond is not None and runClose:

                self.RunClose(dayTradingPos, Side.Sell if dayTradingPos.GetNetOpenShares() > 0 else Side.Buy,
                              dayTradingPos.GetStatisticalParameters(list(cbDict.values())), candlebar,generic=False,
                              closingCond=closingCond)
            return closingCond

        else:
            msg = "Could not find Day Trading Position for candlebar symbol {} @EvaluateClosingMACDRSILongPositions. Please Resync.".format(candlebar.Security.Symbol)
            self.SendToInvokingModule(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)
            return None

    def EvaluateClosingMACDRSIShortPositions(self, candlebar, cbDict,runClose=True):
        symbol = candlebar.Security.Symbol

        dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))), None)

        if dayTradingPos is not None:

            closingCond = dayTradingPos.EvaluateClosingMACDRSIShortTrade(list(cbDict.values()),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_A(),symbol),
                                                                         self.ModelParametersHandler.Get( ModelParametersHandler.MACD_MAX_GAIN_J(), symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_MAX_GAIN_J_J(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_GAIN_NOW_MAX_K(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.RSI_30_SLOPE_SKIP_5_EXIT_L(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_EXIT_N(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_EXIT_N_N(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_EXIT_N_BIS(),symbol),
                                                                         self.ModelParametersHandler.Get( ModelParametersHandler.M_S_MAX_MIN_EXIT_N_N_BIS(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_MAX_MIN_EXIT_P(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_EXIT_Q(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.M_S_NOW_EXIT_Q_Q(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.RSI_30_SLOPE_SKIP_10_EXIT_R(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_EXIT_S(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.M_S_MAX_MIN_EXIT_S_S(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.SEC_5_MIN_SLOPE_EXIT_T(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_U(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_U_U(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_W(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_W_W(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_STOP_LOSS_EXIT_Y(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_Z(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.GAIN_MIN_STOP_LOSS_EXIT_Z_Z(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.END_OF_DAY_LIMIT(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.TAKE_GAIN_LIMIT(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.STOP_LOSS_LIMIT(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_SMOOTHED_MODE(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_ABS_MAX_MS_PERIOD(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_1(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_2(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_3(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_4(),symbol),
                                                                         self.ModelParametersHandler.Get( ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_5(),symbol),
                                                                         self.ModelParametersHandler.Get( ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_6(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_7(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_8(),symbol),
                                                                         self.ModelParametersHandler.Get(ModelParametersHandler.MACD_RSI_CLOSE_SHORT_RULE_9(),symbol)
                                                                         )

            if closingCond is not None and runClose:

                self.RunClose(dayTradingPos, Side.Sell if dayTradingPos.GetNetOpenShares() > 0 else Side.Buy,
                              dayTradingPos.GetStatisticalParameters(list(cbDict.values())), candlebar,generic=False,
                              closingCond=closingCond)

            return closingCond
        else:
            msg = "Could not find Day Trading Position for candlebar symbol {} @EvaluateClosingMACDRSIShortPositions. Please Resync.".format(candlebar.Security.Symbol)
            self.SendToInvokingModule(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)
            return None

    def ProcessCandleBar(self,wrapper):

        candlebar = MarketDataConverter.ConvertCandlebar(wrapper)

        try:
            if(candlebar is None):
                raise Exception("Invalid candlebar received")
            LogHelper.LogPublishCandleBarOnSecurity("DayTrader Recv Candlebar", self, candlebar.Security.Symbol,candlebar)
            self.LockCandlebar.acquire()

            dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == candlebar.Security.Symbol, self.DayTradingPositions))),
                            None)

            if  not dayTradingPos.RunningBacktest:
                cbDict = self.Candlebars[candlebar.Security.Symbol]
                if cbDict is  None:
                    cbDict = {}

                cbDict[candlebar.DateTime] = candlebar

                self.Candlebars[candlebar.Security.Symbol] = cbDict

                self.UpdateTechnicalAnalysisParameters(candlebar,cbDict)
                self.EvaluateOpeningPositions(candlebar,cbDict)
                self.EvaluateClosingPositions(candlebar,cbDict)
                self.UpdateTradingSignals(candlebar,cbDict)

                self.EvaluateClosingForManualConditions(candlebar, cbDict)

                #self.DoLog("Candlebars successfully loaded for symbol {} ".format(candlebar.Security.Symbol),MessageType.DEBUG)
            else:
                self.DoLog("Received unknown null candlebar",MessageType.DEBUG)

            LogHelper.LogPublishCandleBarOnSecurity("DayTrader Processed Candlebar", self, candlebar.Security.Symbol,candlebar)

        except Exception as e:

            self.ProcessErrorInMethod("@DayTrader.ProcessCandleBar", e,candlebar.Security.Symbol if candlebar is not None else None)
        finally:
            if self.LockCandlebar.locked():
                self.LockCandlebar.release()

    def ProcessPortfolioPositionsTradeListRequestThread(self,wrapper):
        try:
            self.RoutingLock.acquire()
            dayTradingPosId = int( wrapper.GetField(PortfolioPositionTradeListRequestFields.PositionId))
            dayTradingPos = next(iter(list(filter(lambda x: x.Id == dayTradingPosId, self.DayTradingPositions))), None)
            self.RoutingLock.release()

            if dayTradingPos is not None:
                wrapper = ExecutionSummaryListWrapper(dayTradingPos)
                self.SendToInvokingModule(wrapper)
            else:
                wrapper = ExecutionSummaryListWrapper(pDayTradingPosition=None,pError="Could not find day trading position for position Id {}".format(dayTradingPosId))
                self.SendToInvokingModule(wrapper)
        except Exception as e:
            msg="Critical error @DayTrader.ProcessPortfolioPositionsTradeListRequestThread.:{}".format(str(e))
            #self.ProcessCriticalError(e,msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))
        finally:
            if self.RoutingLock.locked():
                self.RoutingLock.release()

    def ProcessPortfolioPositionsRequestThread(self,wrapper):
        try:

            portfListWrapper = PortfolioPositionListWrapper(self.DayTradingPositions)
            self.CommandsModule.ProcessMessage(portfListWrapper)
        except Exception as e:
            msg="Critical error @DayTrader.ProcessPortfolioPositionsRequestThread.:{}".format(str(e))
            self.ProcessCriticalError(e,msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))

    def ValidateSideAndQty(self,dayTradingPos,side,qty):

        if self.Configuration.ImplementDetailedSides and dayTradingPos is not None:
            if (side==Side.Sell and dayTradingPos.GetNetOpenShares()>0):
                if qty > dayTradingPos.GetNetOpenShares():
                    raise Exception("You are net long {} shares and you are trying to sell {} shares. First sell your {} net long shares!".format(dayTradingPos.GetNetOpenShares(),qty,dayTradingPos.GetNetOpenShares()))

            if (side == Side.Buy and dayTradingPos.GetNetOpenShares() < 0):
                if qty > (-1 * dayTradingPos.GetNetOpenShares()):
                    raise Exception("You are net short {} shares and you are trying to cover {} shares. First cover your {} net short shares!".format( -1* dayTradingPos.GetNetOpenShares(), qty, -1* dayTradingPos.GetNetOpenShares()))


    def TranslateSide(self, dayTradingPos,side):
        if self.Configuration.ImplementDetailedSides:

            if dayTradingPos is not None:
                if dayTradingPos.GetNetOpenShares()>0:
                    return side
                elif dayTradingPos.GetNetOpenShares() == 0 and side==Side.Sell:
                    return Side.SellShort
                elif dayTradingPos.GetNetOpenShares() == 0 and side==Side.Buy:
                    return Side.Buy
                else:
                    return Side.SellShort if side==Side.Sell else Side.BuyToClose
            else:
                return side
        else:
            return side


    #we just route a position and ignore the answers
    def ProcessNewPositionReqSinglePos(self,wrapper):
        try:

            symbol = wrapper.GetField(PositionField.Symbol)
            secType = wrapper.GetField(PositionField.SecurityType)
            side = wrapper.GetField(PositionField.Side)
            qty = wrapper.GetField(PositionField.Qty)
            account = wrapper.GetField(PositionField.Account)
            price = wrapper.GetField(PositionField.OrderPrice)

            self.RoutingLock.acquire()

            newPos = Position(PosId=self.NextPostId,
                              Security=Security(Symbol=symbol,Exchange=self.Configuration.DefaultExchange,SecType=secType),
                              Side=side,PriceType=PriceType.FixedAmount,Qty=qty,QuantityType=QuantityType.SHARES,
                              Account=account if account is not None else self.Configuration.DefaultAccount,
                              Broker=None,Strategy=None,
                              OrderType=OrdType.Market if price is None else OrdType.Limit,
                              OrderPrice=price)

            newPos.ValidateNewPosition()

            self.SingleExecutionSummaries[self.NextPostId] = ExecutionSummary(datetime.datetime.now(), newPos)
            self.NextPostId = uuid.uuid4()

            if self.RoutingLock.locked():
                self.RoutingLock.release()

            posWrapper = PositionWrapper(newPos)
            self.OrderRoutingModule.ProcessMessage(posWrapper)

        except Exception as e:
            msg = "Exception @DayTrader.ProcessNewPositionReqSinglePos: {}!".format(str(e))
            self.ProcessCriticalError(e, msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))
        finally:
            if self.RoutingLock.locked():
                self.RoutingLock.release()

    def ProcessNewPositionReqManagedPos(self, dayTradingPos, side,qty,account, price = None,stopLoss=None,
                                        takeProfit=None,closeEndOfDay=None, text=None):
        try:
            self.RoutingLock.acquire()

            if dayTradingPos.Routing:
                return

            side = self.TranslateSide(dayTradingPos, side)

            newPos = Position(PosId=self.NextPostId,
                              Security=dayTradingPos.Security,
                              Side=side, PriceType=PriceType.FixedAmount, Qty=qty, QuantityType=QuantityType.SHARES,
                              Account=account if account is not None else self.Configuration.DefaultAccount,
                              Broker=None, Strategy=None,
                              OrderType=OrdType.Market if price is None else OrdType.Limit,
                              OrderPrice=price)

            newPos.StopLoss=stopLoss
            newPos.TakeProfit=takeProfit
            newPos.CloseEndOfDay=closeEndOfDay

            newPos.ValidateNewPosition()

            summary = ExecutionSummary(datetime.datetime.now(), newPos)
            summary.Text=text
            dayTradingPos.ExecutionSummaries[self.NextPostId] = summary
            dayTradingPos.Routing=True
            self.PositionSecurities[self.NextPostId] = dayTradingPos
            self.NextPostId = uuid.uuid4()
            if self.RoutingLock.locked():
                self.RoutingLock.release()

            posWrapper = PositionWrapper(newPos)
            state = self.OrderRoutingModule.ProcessMessage(posWrapper)

            if state.Success:
                threading.Thread(target=self.PublishPortfolioPositionThread, args=(dayTradingPos,)).start()
                threading.Thread(target=self.PublishSummaryThread, args=(summary, dayTradingPos.Id)).start()
            else:
                del dayTradingPos.ExecutionSummaries[summary.Position.PosId]
                del self.PositionSecurities[summary.Position.PosId]
                dayTradingPos.Routing=False
                raise state.Exception

        finally:
            if self.RoutingLock.locked():
                self.RoutingLock.release()

    #now we are trading a managed position
    def ProcessManualNewPositionReqManagedPos(self,wrapper):

        posId = wrapper.GetField(PositionField.PosId)
        try:

            dayTradingPos = next(iter(list(filter(lambda x: x.Id == posId, self.DayTradingPositions))), None)
            if(dayTradingPos is not None):

                if(dayTradingPos.Routing):
                    raise Exception("Could not send a new order for a position that is already routing. Cancel the previous order.")

                side = wrapper.GetField(PositionField.Side)
                qty = wrapper.GetField(PositionField.Qty)
                account = wrapper.GetField(PositionField.Account)
                price = wrapper.GetField(PositionField.OrderPrice)
                stopLoss = wrapper.GetField(PositionField.StopLoss)
                takeProfit = wrapper.GetField(PositionField.TakeProfit)
                closeEndOfDay = wrapper.GetField(PositionField.CloseEndOfDay)

                self.ValidateSideAndQty(dayTradingPos,side,qty)

                self.ProcessNewPositionReqManagedPos(dayTradingPos,side,qty,account,price,stopLoss,takeProfit,closeEndOfDay)
            else:
                raise Exception("Could not find a security to trade (position) for position id {}".format(posId))

        except Exception as e:
            msg = "Exception @DayTrader.ProcessManualNewPositionReqManagedPos: {}!".format(str(e))
            #self.ProcessCriticalError(e, msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))

    def ProcessNewPositionReqThread(self,wrapper):
        try:

            symbol = wrapper.GetField(PositionField.Symbol)
            posId = wrapper.GetField(PositionField.PosId)

            if symbol is not None:
                self.ProcessNewPositionReqSinglePos(wrapper)
            elif posId is not None:
                self.ProcessManualNewPositionReqManagedPos(wrapper)
            else:
                raise Exception("You need to provide the symbol or positionId for a new position!")

        except Exception as e:
            msg = "Exception @DayTrader.ProcessNewPositionReqThread: {}!".format(str(e))
            #self.ProcessCriticalError(e, msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))

    def ProcessCancelAllPositionReqThread(self,wrapper):
        try:
            state = self.OrderRoutingModule.ProcessMessage(wrapper)

            if not state.Success:
                self.ProcessError(ErrorWrapper(state.Exception))

        except Exception as e:
            msg = "Exception @DayTrader.ProcessCancelAllPositionReqThread: {}!".format(str(e))
            #self.ProcessCriticalError(e, msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))

    def ProcessCancePositionReqThread(self,wrapper):
        try:

            posId = wrapper.GetField(PositionField.PosId)

            if posId is not None:

                self.RoutingLock.acquire()
                dayTradingPos = next(iter(list(filter(lambda x: x.Id == posId, self.DayTradingPositions))),None)
                self.RoutingLock.release()
                if dayTradingPos is not None:
                    for routPosId in dayTradingPos.ExecutionSummaries:
                        summary = dayTradingPos.ExecutionSummaries[routPosId]
                        if summary.Position.IsOpenPosition():

                            cxlWrapper = CancelPositionWrapper(summary.Position.PosId)
                            state = self.OrderRoutingModule.ProcessMessage(cxlWrapper)

                            if not state.Success:
                                self.ProcessError(ErrorWrapper(state.Exception))
                else:
                    raise Exception("Could not find a daytrading position for Id {}".format(posId))
            else:
                raise Exception("You have to specify a position id to cancel a position")
        except Exception as e:
            msg = "Exception @DayTrader.ProcessCancePositionReqThread: {}!".format(str(e))
            # self.ProcessCriticalError(e, msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))
        finally:
            if self.RoutingLock.locked():
                self.RoutingLock.release()


    def UpdateModelParamters(self,dayTradingPos,modelParamDict):

        modelParamsBackup = []

        for modelKey in modelParamDict:

            modelParamInMem = self.ModelParametersHandler.Get(modelKey, dayTradingPos.Security.Symbol)

            if modelParamInMem is None:
                raise Exception("Could not find a model parameter for the key {}. Please validate that you are using the correct key".format(key))

            backtestModelParam = ModelParameter(key=modelKey,symbol=dayTradingPos.Security.Symbol,stringValue=None,intValue=None,floatValue=None)
            backtestModelParam.IntValue = int(modelParamDict[modelKey]) if modelParamInMem.IntValue is not None else None
            backtestModelParam.FloatValue = float(modelParamDict[modelKey]) if modelParamInMem.FloatValue is not None else None
            backtestModelParam.StringValue = str(modelParamDict[modelKey]) if modelParamInMem.StringValue is not None else None
            backtestModelParam.Symbol=modelParamInMem.Symbol

            self.ModelParametersHandler.Set(modelKey, backtestModelParam.Symbol, backtestModelParam)

            modelParamsBackup.append(modelParamInMem)

        return modelParamsBackup


    def RunBacktest(self,dayTradingPos,refDate,candelBarDict,marketDataDict):

        backtestDTOArr = []

        currDate = refDate
        self.ResetForNewDayOnBackTest(dayTradingPos, currDate)
        routingCounter = 0

        for date in candelBarDict:
            time.sleep(1)#This has to be here so the ExecutinSummaries are not cleared @ResetForNewDayOnBackTest
                         #when swithing between trading days
            self.DoLog("Starting to process for date:{}".format(currDate.date()), MessageType.INFO)
            if datetime.datetime.fromtimestamp(mktime(date)).date() !=currDate.date():
                currDate=datetime.datetime.fromtimestamp(mktime(date))
                self.ResetForNewDayOnBackTest(dayTradingPos, currDate)

            candleBarsArray = candelBarDict[date]
            marketDataArray = None

            if date in marketDataDict:
                marketDataArray = marketDataDict[date]
            else:
                raise Exception("Could not find market data for date {}. There is some inconsistency in the input data".format(date))

            if len(candleBarsArray) != len(marketDataArray):
                raise Exception(
                    "Market Data length and Candlebar length present inconsistent values: Market Data Length={} CandleBar Length={}".format(
                        len(candleBarsArray), len(marketDataArray)))

            i = 0

            for candlebar in candleBarsArray:
                self.RoutingLock.acquire()

                try:
                    md = marketDataArray[i]

                    cbDict = self.Candlebars[candlebar.Security.Symbol]
                    if cbDict is None:
                        cbDict = {}
                    cbDict[candlebar.DateTime] = candlebar
                    self.Candlebars[candlebar.Security.Symbol] = cbDict
                    self.UpdateTechnicalAnalysisParameters(candlebar, cbDict)
                    dayTradingPos.MarketData = md
                    dayTradingPos.CalculateCurrentDayProfits(md)

                    if not dayTradingPos.Routing:
                        self.EvaluateOpeningPositions(candlebar, cbDict)
                        closing = self.EvaluateClosingPositions(candlebar, cbDict)
                        routingCounter = 0
                    else:
                        closing=None
                        routingCounter = routingCounter + 1

                    if routingCounter>=3:
                        raise Exception("The backtested position has been in a routing state for more than 3 candles. This means that some Filled Execution Report was lost. The backtest has to be finished!")

                    backtestDto = BacktestDTO(pSymbol=dayTradingPos.Security.Symbol,
                                              pDate=candlebar.DateTime.date(),
                                              pTime=candlebar.DateTime.time() ,
                                              pShares=dayTradingPos.GetNetOpenShares(),
                                              pCurrentProfit=dayTradingPos.CurrentProfitMonetaryLastTrade if closing else "")

                    backtestDTOArr.append(backtestDto)

                except Exception as e:
                    traceback.print_exc()
                    msg = "Error processing strategy backtest for date {} : {}!".format(candlebar.DateTime,str(e))
                    self.ProcessError(ErrorWrapper(Exception(msg)))
                    self.DoLog(msg, MessageType.ERROR)
                finally:
                    if self.RoutingLock.locked():
                        self.RoutingLock.release()

                threading.Thread(target=self.PublishPortfolioPositionThread, args=(dayTradingPos,)).start()

                sleepMilisec =self.ModelParametersHandler.Get(ModelParametersHandler.PACING_ON_BACKTEST_MILISEC(),dayTradingPos.Security.Symbol)
                time.sleep(sleepMilisec.IntValue/1000)

                i+=1

        return backtestDTOArr

    def ResetForNewDayOnBackTest(self,dayTradingPos,refDate, running=True):
        dayTradingPos.ResetProfitCounters(refDate)
        dayTradingPos.RunningBacktest = running
        dayTradingPos.ResetExecutionSummaries()
        if self.Candlebars[dayTradingPos.Security.Symbol] is not None:
            self.Candlebars[dayTradingPos.Security.Symbol].clear()
        else:
            self.Candlebars[dayTradingPos.Security.Symbol]={}

        self.MarketData[dayTradingPos.Security.Symbol]=MarketData()



    def ProcessStrategyBacktestThread(self,dayTradingPos,wrapper):
        try:

            tradingMode = self.ModelParametersHandler.Get(ModelParametersHandler.TRADING_MODE(), dayTradingPos.Security.Symbol)

            if dayTradingPos.RunningBacktest:
                raise Exception("Another backtest is already running for symbol {}. You have to wait for the preious backtest to finish".format(dayTradingPos.Security.Symbol))

            if dayTradingPos.Routing:
                raise Exception("The position for security {} is routing (open orders in the exchange). Cancel the open orders or depurate the position".format(dayTradingPos.Security.Symbol))

            if tradingMode.StringValue == _TRADING_MODE_MANUAL:

                candelBarDict = wrapper.GetField(StrategyBacktestField.CandleBarDict)
                marketDataDict = wrapper.GetField(StrategyBacktestField.MarketDataDict)
                modelParamDict = wrapper.GetField(StrategyBacktestField.ModelParametersDict)
                refDate = wrapper.GetField(StrategyBacktestField.ReferenceDate)

                # 1- We update the model parameters in memotry with the ones that will use the backtest
                modelParamsBackup = self.UpdateModelParamters(dayTradingPos,modelParamDict)

                #2- Reset Statistics!
                #self.ResetForNewDayOnBackTest(dayTradingPos,refDate)

                #3-We execute the backtest
                backtestDtoArr = self.RunBacktest(dayTradingPos,refDate,candelBarDict,marketDataDict)

                #4-We restore model parameters previous values
                for originalModelParam in modelParamsBackup:
                    self.ModelParametersHandler.Set(originalModelParam.Key, originalModelParam.Symbol, originalModelParam)

                self.SendToInvokingModule(ErrorWrapper(Exception("Process successfully completed...")))

                #5-We publish the response
                wrapper = StrategyBacktestResultWrapper(pSymbol=dayTradingPos.Security.Symbol,pBacktestResultDtoArr=backtestDtoArr)
                self.FileHandlerModule.ProcessMessage(wrapper)

                self.DoLog("Backtest successfully completed...",MessageType.INFO)

            else:
                raise Exception("Security {} is in automatic mode. It's unsafe to run a backtest while the security it's in this state. Please turn it to manual mode".format(dayTradingPos.Security.Symbol))

        except Exception as e:
            traceback.print_exc()
            msg = "Critical Error processing strategy backtest (@thread): {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)
        finally:
            self.ResetForNewDayOnBackTest(dayTradingPos,datetime.datetime.now(),running=False)


    def ProcessStrategyBacktest(self,wrapper):
        try:
            symbol = wrapper.GetField(StrategyBacktestField.Symbol)

            #we look for the daytrading position
            dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == symbol, self.DayTradingPositions))), None)

            if dayTradingPos is not None:

                threading.Thread(target=self.ProcessStrategyBacktestThread, args=(dayTradingPos,wrapper,)).start()

                return CMState.BuildSuccess(self)
            else:
                raise Exception( "Could not find day trading position for symbol {}".format(symbol if symbol is not None else "-"))

        except Exception as e:

            msg = "Critical Error processing strategy backtest: {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessPositionTradingSignalSubscription(self,wrapper):
        try:
            posId =  wrapper.GetField(PositionTradingSignalSubscriptionField.PositionId)
            subsc= wrapper.GetField(PositionTradingSignalSubscriptionField.Subscribe)

            dayTradingPos = next(iter(list(filter(lambda x: x.Id == posId, self.DayTradingPositions))), None)

            if dayTradingPos is not None:
                dayTradingPos.ShowTradingRecommndations= subsc
            else:
                raise Exception("There is not a position for Id {}".format(posId))

            return CMState.BuildSuccess(self)
        except Exception as e:
            msg = "Exception @DayTrader.ProcessPositionTradingSignalSubscription: {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            return CMState.BuildFailure(self, Exception=e)

    def ProcessMarketDataReq(self,wrapper):
        try:
            symbol = wrapper.GetField(MarketDataRequestField.Symbol)

            if symbol in self.MarketData:

                md = self.MarketData[symbol]

                dayTradingPos = next(iter(list(filter(lambda x: x.Security.Symbol == symbol, self.DayTradingPositions))), None)

                md.StdDev=dayTradingPos.LastNDaysStdDev if dayTradingPos is not None else None

                mdWrapper = MarketDataWrapper(md)

                threading.Thread(target=self.SendToInvokingModule, args=(mdWrapper,)).start()

                return CMState.BuildSuccess(self)
            else:
                raise Exception(
                    "Could not find market data for symbol {}".format(symbol if symbol is not None else "-"))

        except Exception as e:
            msg = "Critical Error requesting market data: {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def ProcessDayTradingPositionNewReq (self,wrapper):
        try:
            symbol = wrapper.GetField(PositionField.Symbol)
            secType = wrapper.GetField(PositionField.SecurityType)
            exchange = wrapper.GetField(PositionField.Exchange)

            if self.DayTradingPositionManager.GetDayTradingPosition(symbol) is not None:
                raise Exception("There is already an active position for symbol {}".format(symbol))

            # We instantiate the new DayTradingPositon
            dayTradingPos = DayTradingPosition(-1,Security(Symbol=symbol,
                                                           SecType= Security.GetSecurityType(secType),
                                                           Exchange= exchange
                                                           ),
                                               shares=0,active=True,routing=False,open=False,
                                               longSignal=False,shortSignal=False,signalType=None,signalDesc="")

            self.DayTradingPositionManager.PersistDayTradingPosition(dayTradingPos)
            persistedDayTradingPos = self.DayTradingPositionManager.GetDayTradingPosition(dayTradingPos.Security.Symbol)

            paramBias = ModelParameter(key=ModelParametersHandler.DAILY_BIAS(), symbol=symbol, stringValue=None, intValue=None, floatValue=0)
            self.ModelParametersManager.PersistModelParameter(paramBias)
            self.ModelParametersHandler.Set(ModelParametersHandler.DAILY_BIAS(),symbol,paramBias)

            paramMode = ModelParameter(key=ModelParametersHandler.TRADING_MODE(), symbol=symbol, stringValue="MANUAL",intValue=None, floatValue=None)
            self.ModelParametersManager.PersistModelParameter(paramMode)
            self.ModelParametersHandler.Set(ModelParametersHandler.TRADING_MODE(), symbol, paramMode)

            if persistedDayTradingPos is None:
                raise Exception("Position created for symbol {} could not be recovered from database!".format(symbol))

            self.DayTradingPositions.append(persistedDayTradingPos)

            #1- We request historical prices
            histLength=self.ModelParametersHandler.Get(ModelParametersHandler.HISTORICAL_PRICES_CAL_DAYS_TO_REQ(),None).IntValue
            hpReqWrapper = HistoricalPricesRequestWrapper(dayTradingPos.Security,histLength,TimeUnit.Day, SubscriptionRequestType.Snapshot)
            self.MarketDataModule.ProcessMessage(hpReqWrapper)

            #2- We request candle bars
            cbReqWrapper = CandleBarRequestWrapper(dayTradingPos.Security, time, TimeUnit.Minute,SubscriptionRequestType.SnapshotAndUpdates)
            self.MarketDataModule.ProcessMessage(cbReqWrapper)

            #3- We request the market data
            mdReqWrapper = MarketDataRequestWrapper(dayTradingPos.Security, SubscriptionRequestType.SnapshotAndUpdates)
            self.MarketDataModule.ProcessMessage(mdReqWrapper)

            threading.Thread(target=self.PublishPortfolioPositionThread, args=(persistedDayTradingPos,)).start()

            return CMState.BuildSuccess(self)

        except Exception as e:
            msg = "Critical Error creating day trading position : {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessCleanTringgersDayTradingPosition(self,dayTradingPos,cleanStopLoss, cleanTakeProfit, cleanEndOfDay):
        longSummary = dayTradingPos.GetLastTradedSummary(Side.Buy)
        shortSummary = dayTradingPos.GetLastTradedSummary(Side.Sell)

        if cleanStopLoss is not None and cleanStopLoss:
            if longSummary is not None:
                longSummary.Position.StopLoss=None
            if shortSummary is not None:
                shortSummary.Position.StopLoss=None


        if cleanTakeProfit is not None and cleanTakeProfit:
            if longSummary is not None:
                longSummary.Position.TakeProfit=None
            if shortSummary is not None:
                shortSummary.Position.TakeProfit=None


        if cleanEndOfDay is not None and cleanEndOfDay:
            if longSummary is not None:
                longSummary.Position.CloseEndOfDay=False
            if shortSummary is not None:
                shortSummary.Position.CloseEndOfDay=False

        if longSummary is not None:
            self.SummariesQueue.put(longSummary)
            threading.Thread(target=self.PublishSummaryThread, args=(longSummary, dayTradingPos.Id)).start()

        if shortSummary is not None:
            self.SummariesQueue.put(shortSummary)
            threading.Thread(target=self.PublishSummaryThread, args=(shortSummary, dayTradingPos.Id)).start()


    def ProcessDepurateDayTradingPosition(self,dayTradingPos):
        depuratedSummaries = dayTradingPos.DepurateSummaries()

        for depuratedSummary in depuratedSummaries:
            self.SummariesQueue.put(depuratedSummary)
            threading.Thread(target=self.PublishSummaryThread, args=(depuratedSummary, dayTradingPos.Id)).start()

        self.DayTradingPositionsQueue.put(dayTradingPos)
        threading.Thread(target=self.PublishPortfolioPositionThread, args=(dayTradingPos,)).start()


    def ProcessDayTradingPositionTradingModeUpdate(self,dayTradingPos,tradingMode):
        if tradingMode != _TRADING_MODE_AUTOMATIC and tradingMode != _TRADING_MODE_MANUAL:
            raise Exception("Invalid trading mode {}".format(tradingMode))

        tradingModeInMem = self.ModelParametersHandler.Get(ModelParametersHandler.TRADING_MODE(),
                                                           dayTradingPos.Security.Symbol)

        if tradingModeInMem is None or tradingModeInMem.Symbol is None:
            raise Exception("Security {} has a generic trading mode".format(dayTradingPos.Security.Symbol))

        if tradingModeInMem.StringValue != tradingMode:
            tradingModeInMem.StringValue = tradingMode
            self.ModelParametersManager.PersistModelParameter(tradingModeInMem)



    def ProcessDayTradingPositionUpdateReq (self,wrapper):
        try:
            posId = wrapper.GetField(PositionField.PosId)
            qtyShares = wrapper.GetField(PositionField.Qty)
            active = wrapper.GetField(PositionField.PosStatus)
            tradingMode = wrapper.GetField(PositionField.TradingMode)
            depurate = wrapper.GetField(PositionField.Depurate)
            cleanStopLoss = wrapper.GetField(PositionField.CleanStopLoss)
            cleanTakeProfit = wrapper.GetField(PositionField.CleanTakeProfit)
            cleanEndOfDay = wrapper.GetField(PositionField.CleanEndOfDay)

            dayTradingPos = next( iter(list(filter(lambda x: x.Id == posId, self.DayTradingPositions))),None)

            if dayTradingPos is not None:

                if qtyShares is not None:
                    dayTradingPos.SharesQuantity=qtyShares
                if active is not None:
                    dayTradingPos.Active=active
                if tradingMode is not None:
                    self.ProcessDayTradingPositionTradingModeUpdate(dayTradingPos,tradingMode)
                if depurate is not None:
                    self.ProcessDepurateDayTradingPosition(dayTradingPos)
                if cleanStopLoss is not None or cleanTakeProfit is not None or cleanEndOfDay is not None:
                    self.ProcessCleanTringgersDayTradingPosition(dayTradingPos,cleanStopLoss,cleanTakeProfit,cleanEndOfDay)


                threading.Thread(target=self.PublishPortfolioPositionThread, args=(dayTradingPos,)).start()

                return CMState.BuildSuccess(self)
            else:
                raise Exception("Could not find a day traing position for posId {}".format(posId if posId is not None else "-"))

        except Exception as e:
            msg = "Critical Error updating day trading position attribute: {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def SendBulkModelParameters(self,parameters):
        try:
            for paramInMem in parameters:
                modelParmWrapper = ModelParameterWrapper(paramInMem)
                self.SendToInvokingModule(modelParmWrapper)
        except Exception as e:
            msg = "Critical Error @SendBulkModelParameters: {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)

    def ProcessModelParamReq(self,wrapper):
        try:
            symbol = wrapper.GetField(ModelParamField.Symbol)
            key = wrapper.GetField(ModelParamField.Key)


            if(key is not None and key !="*"):

                paramInMem = self.ModelParametersHandler.Get(key=key,symbol=symbol if symbol is not None else None)

                modelParmWrapper = ModelParameterWrapper (paramInMem)

                threading.Thread(target=self.SendToInvokingModule, args=(modelParmWrapper,)).start()

                return CMState.BuildSuccess(self)
            else:
                parameters = self.ModelParametersHandler.GetAll(symbol=symbol if symbol !="*" else None )
                threading.Thread(target=self.SendBulkModelParameters, args=(parameters,)).start()
                return CMState.BuildSuccess(self)

        except Exception as e:
            msg = "Critical Error recovering model parameter from memory: {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessHistoricalPricesReq(self,wrapper):
        try:
            symbol = wrapper.GetField(HistoricalPricesRequestField.Security)
            fromDate = parse( wrapper.GetField(HistoricalPricesRequestField.From))
            toDate = parse( wrapper.GetField(HistoricalPricesRequestField.To))


            if symbol in self.HistoricalPrices and self.HistoricalPrices[symbol] is not None :

                #we won't validate that the date range is too big
                marketDataArr  = list(filter(lambda x:  x.MDEntryDate >=fromDate.date() and x.MDEntryDate<=toDate.date(), self.HistoricalPrices[symbol].values()))

                histPricesWrapper =  HistoricalPricesWrapper(symbol,fromDate,toDate,marketDataArr)

                threading.Thread(target=self.SendToInvokingModule, args=(histPricesWrapper,)).start()

                return CMState.BuildSuccess(self)

            else:
                raise Exception("No historical prices loaded for symbol {}".format(symbol))


        except Exception as e:
            msg = "Critical Error recovering historical prices from memory: {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessCreateModelParamReq(self,wrapper):

        try:
            symbol = wrapper.GetField(ModelParamField.Symbol)
            key = wrapper.GetField(ModelParamField.Key)
            intValue = int( wrapper.GetField(ModelParamField.IntValue)) if wrapper.GetField(ModelParamField.IntValue) is not None else None
            stringValue =  str( wrapper.GetField(ModelParamField.StringValue)) if wrapper.GetField(ModelParamField.StringValue) is not None else None
            floatValue = float( wrapper.GetField(ModelParamField.FloatValue)) if wrapper.GetField(ModelParamField.FloatValue) is not None else None

            paramToUpd = ModelParameter(key=key,symbol=symbol,stringValue=stringValue,intValue=intValue,floatValue=floatValue)

            paramInMem = self.ModelParametersHandler.GetLight(key,symbol)

            if paramInMem is not None:
                raise Exception("Could not create a model parameters for a key-symbol that already exsits!-> key: {}  symbol:{}. Update the existing parameters "
                                .format(key,symbol if symbol is not None else "*"))

            self.ModelParametersManager.PersistModelParameter(paramToUpd)

            self.ModelParametersHandler.Set(key,symbol,paramToUpd)

            return CMState.BuildSuccess(self)
        except Exception as e:
            msg = "Critical Error creating model param: {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg,MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)



    def ProcessUpdateModelParamReq(self,wrapper):

        try:
            symbol = wrapper.GetField(ModelParamField.Symbol)
            key = wrapper.GetField(ModelParamField.Key)
            intValue = int( wrapper.GetField(ModelParamField.IntValue)) if wrapper.GetField(ModelParamField.IntValue) is not None else None
            stringValue =  str( wrapper.GetField(ModelParamField.StringValue)) if wrapper.GetField(ModelParamField.StringValue) is not None else None
            floatValue = float( wrapper.GetField(ModelParamField.FloatValue)) if wrapper.GetField(ModelParamField.FloatValue) is not None else None

            paramToUpd = ModelParameter(key=key,symbol=symbol,stringValue=stringValue,intValue=intValue,floatValue=floatValue)

            paramInMem = self.ModelParametersHandler.GetLight(key,symbol)

            if paramInMem is None:
                raise Exception("Could not find a model parameters in memory for key {} and symbol{}. Parameters insertion should be made "
                                .format(key,symbol if symbol is not None else "unknown"))

            self.ModelParametersManager.PersistModelParameter(paramToUpd)

            paramInMem.IntValue=paramToUpd.IntValue
            paramInMem.StringValue = paramToUpd.StringValue
            paramInMem.FloatValue = paramToUpd.FloatValue

            if(key is None):
                raise Exception("Model parameter key cannot be null")

            return CMState.BuildSuccess(self)
        except Exception as e:
            msg = "Critical Error updating model param: {}!".format(str(e))
            self.ProcessError(ErrorWrapper(Exception(msg)))
            self.DoLog(msg,MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessCancePositionReq(self,wrapper):
        try:

            if self.PositionsSynchronization:
                raise Exception("The engine is in the synchronization process. Please try again later!")

            if self.ServiceFailure:
                return CMState.BuildFailure(self,Exception=self.FailureException)

            threading.Thread(target=self.ProcessCancePositionReqThread, args=(wrapper,)).start()

            return CMState.BuildSuccess(self)

        except Exception as e:
            msg = "Critical Error cancelling position to the exchange: {}!".format(str(e))
            self.ProcessCriticalError(e, msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))
            return CMState.BuildFailure(self, Exception=e)

    def ProcessCancelAllPositionReq(self,wrapper):
        try:

            if self.PositionsSynchronization:
                raise Exception("The engine is in the synchronization process. Please try again later!")

            if self.ServiceFailure:
                return CMState.BuildFailure(self,Exception=self.FailureException)

            threading.Thread(target=self.ProcessCancelAllPositionReqThread, args=(wrapper,)).start()

            return CMState.BuildSuccess(self)

        except Exception as e:
            msg = "Critical Error sending new position to the exchange: {}!".format(str(e))
            self.ProcessCriticalError(e, msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))
            return CMState.BuildFailure(self, Exception=e)

    def ProcessNewPositionReq(self,wrapper):

        try:

            if self.PositionsSynchronization:
                raise Exception("The engine is in the synchronization process. Please try again later!")

            if self.ServiceFailure:
                return CMState.BuildFailure(self,Exception=self.FailureException)

            threading.Thread(target=self.ProcessNewPositionReqThread, args=(wrapper,)).start()

            return CMState.BuildSuccess(self)

        except Exception as e:
            msg = "Critical Error sending new position to the exchange: {}!".format(str(e))
            self.ProcessCriticalError(e, msg)
            self.ProcessError(ErrorWrapper(Exception(msg)))
            return CMState.BuildFailure(self, Exception=e)

    def ProcessPortfolioPositionsTradeListRequest(self,wrapper):
        if self.ServiceFailure:
            return CMState.BuildFailure(self,Exception=self.FailureException)

        threading.Thread(target=self.ProcessPortfolioPositionsTradeListRequestThread, args=(wrapper,)).start()

        return CMState.BuildSuccess(self)

    def ProcessPortfolioPositionsRequest(self,wrapper):
        
        if self.ServiceFailure:
            return CMState.BuildFailure(self,Exception=self.FailureException)

        threading.Thread(target=self.ProcessPortfolioPositionsRequestThread, args=(wrapper,)).start()

        return CMState.BuildSuccess(self)

    def RequestPositionList(self):
        time.sleep(int(self.Configuration.PauseBeforeExecutionInSeconds))
        self.DoLog("Requesting for open orders...", MessageType.INFO)
        wrapper = PositionListRequestWrapper()
        self.OrderRoutingModule.ProcessMessage(wrapper)

    def RequestMarketData(self):
        for secIn in self.DayTradingPositions:
            try:
                self.LockMarketData.acquire()
                self.MarketData[secIn.Security.Symbol]=secIn.Security
                mdReqWrapper = MarketDataRequestWrapper(secIn.Security,SubscriptionRequestType.SnapshotAndUpdates)
                self.MarketDataModule.ProcessMessage(mdReqWrapper)
            finally:
                self.LockMarketData.release()


    def RequestBars(self):

        for secIn in self.DayTradingPositions:

            time = int( self.ModelParametersHandler.Get(ModelParametersHandler.BAR_FREQUENCY(),secIn.Security.Symbol).IntValue)

            self.Candlebars[secIn.Security.Symbol]=None
            mdReqWrapper = CandleBarRequestWrapper(secIn.Security,time,TimeUnit.Minute,
                                                   SubscriptionRequestType.SnapshotAndUpdates)

            self.MarketDataModule.ProcessMessage(mdReqWrapper)


    def RequestHistoricalPrices(self):
        for secIn in self.DayTradingPositions:
            self.HistoricalPrices[secIn.Security.Symbol]=None
            hpReqWrapper = HistoricalPricesRequestWrapper(secIn.Security,
                                                          self.ModelParametersHandler.Get(ModelParametersHandler.HISTORICAL_PRICES_CAL_DAYS_TO_REQ(),secIn.Security.Symbol).IntValue,
                                                          TimeUnit.Day, SubscriptionRequestType.Snapshot)
            self.MarketDataModule.ProcessMessage(hpReqWrapper)


    def ProcessMessage(self, wrapper):
        try:
            if wrapper.GetAction() == Actions.PORTFOLIO_POSITIONS_REQUEST:
                return self.ProcessPortfolioPositionsRequest(wrapper)
            elif wrapper.GetAction() == Actions.PORTFOLIO_POSITION_TRADE_LIST_REQUEST:
                return self.ProcessPortfolioPositionsTradeListRequest(wrapper)
            elif wrapper.GetAction() == Actions.NEW_POSITION:
                return self.ProcessNewPositionReq(wrapper)
            elif wrapper.GetAction() == Actions.CANCEL_ALL_POSITIONS:
                return self.ProcessCancelAllPositionReq(wrapper)
            elif wrapper.GetAction() == Actions.CANCEL_POSITION:
                return self.ProcessCancePositionReq(wrapper)
            elif wrapper.GetAction() == Actions.CREATE_MODEL_PARAM_REQUEST:
                return self.ProcessCreateModelParamReq(wrapper)
            elif wrapper.GetAction() == Actions.UPDATE_MODEL_PARAM_REQUEST:
                return self.ProcessUpdateModelParamReq(wrapper)
            elif wrapper.GetAction() == Actions.HISTORICAL_PRICES_REQUEST:
                return self.ProcessHistoricalPricesReq(wrapper)
            elif wrapper.GetAction() == Actions.MODEL_PARAM_REQUEST:
                return self.ProcessModelParamReq(wrapper)
            elif wrapper.GetAction() == Actions.DAY_TRADING_POSITION_UPDATE_REQUEST:
                return self.ProcessDayTradingPositionUpdateReq(wrapper)
            elif wrapper.GetAction() == Actions.DAY_TRADING_POSITION_NEW_REQUEST:
                return self.ProcessDayTradingPositionNewReq(wrapper)
            elif wrapper.GetAction() == Actions.MARKET_DATA_REQUEST:
                return self.ProcessMarketDataReq(wrapper)
            elif wrapper.GetAction() == Actions.POSITION_TRADING_SIGNAL_SUBSCRIPTION:
                return self.ProcessPositionTradingSignalSubscription(wrapper)
            elif wrapper.GetAction() == Actions.STRATEGY_BACKTEST:
                return self.ProcessStrategyBacktest(wrapper)
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

            threading.Thread(target=self.DayTradingPersistanceThread, args=()).start()

            self.LoadManagers()

            #broomsTester = BroomsTester(self.ModelParametersHandler)
            #broomsTester.DoTest()

            rsiTester= RSIIndicatorTester()
            rsiTester.DoTest()

            self.CommandsModule = self.InitializeModule(self.Configuration.WebsocketModule, self.Configuration.WebsocketConfigFile)

            self.FileHandlerModule = self.InitializeModule(self.Configuration.FileHandlerModule,self.Configuration.FileHandlerConfigFile)

            self.MarketDataModule =  self.InitializeModule(self.Configuration.IncomingModule,self.Configuration.IncomingConfigFile)

            self.OrderRoutingModule = self.InitializeModule(self.Configuration.OutgoingModule,self.Configuration.OutgoingConfigFile)

            time.sleep(self.Configuration.PauseBeforeExecutionInSeconds)

            threading.Thread(target=self.MarketSubscriptionsThread, args=()).start()

            self.DoLog("DayTrader Successfully initialized", MessageType.INFO)

            return CMState.BuildSuccess(self)

        else:
            msg = "Error initializing Day Trader"
            self.DoLog(msg, MessageType.ERROR)
            return CMState.BuildFailure(self,errorMsg=msg)
