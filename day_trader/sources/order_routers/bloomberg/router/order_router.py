from sources.framework.util.singleton.common.util.singleton import *
from sources.framework.common.abstract.base_communication_module import BaseCommunicationModule
from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.wrappers.execution_report_list_wrapper import *
from sources.framework.common.wrappers.generic_execution_report_wrapper import *
from sources.framework.common.wrappers.error_wrapper import *
from sources.order_routers.bloomberg.common.wrappers.historical_prices_wrapper import *
from sources.framework.common.enums.CxlRejReason import *
from sources.framework.common.enums.CxlRejResponseTo import *
from sources.framework.business_entities.market_data.candle_bar import *
from sources.framework.common.wrappers.market_data_wrapper import *
from sources.order_routers.bloomberg.common.wrappers.candle_bar_data_wrapper import *
from sources.order_routers.bloomberg.common.converter.market_data_request_converter import *
from sources.order_routers.bloomberg.common.configuration.configuration import Configuration
from sources.order_routers.bloomberg.common.wrappers.rejected_execution_report_wrapper import *
from sources.order_routers.bloomberg.common.wrappers.new_execution_report_wrapper import *
from sources.order_routers.bloomberg.common.wrappers.filled_execution_report_wrapper import *
from sources.order_routers.bloomberg.common.wrappers.execution_report_wrapper import *
from sources.order_routers.bloomberg.common.util.subscription_helper import *
from sources.framework.common.dto.cm_state import *
from sources.order_routers.bloomberg.common.converter.order_converter import *
from sources.framework.common.wrappers.order_cancel_reject_wrapper import *
from sources.framework.common.enums.TimeUnit import *
from sources.framework.util.log_helper import *
import threading
import time
import uuid
from datetime import datetime
import traceback
import queue


ORDER_FIELDS      = blpapi.Name("OrderFields")
ORDER_ROUTE_FIELDS      = blpapi.Name("OrderRouteFields")
MARKET_DATA_EVENTS      = blpapi.Name("MarketDataEvents")
MARKET_BAR_START      = blpapi.Name("MarketBarStart")
MARKET_BAR_UPDATE      = blpapi.Name("MarketBarUpdate")
MARKET_BAR_INTERVAL_END      = blpapi.Name("MarketBarIntervalEnd")
MARKET_BAR_END      = blpapi.Name("MarketBarEnd")
HISTORICAL_DATA_REPONSE      = blpapi.Name("HistoricalDataResponse")
SESSION_STARTED         = blpapi.Name("SessionStarted")
SESSION_TERMINATED      = blpapi.Name("SessionTerminated")
SESSION_STARTUP_FAILURE = blpapi.Name("SessionStartupFailure")
SESSION_CONNECTION_UP   = blpapi.Name("SessionConnectionUp")
SESSION_CONNECTION_DOWN = blpapi.Name("SessionConnectionDown")

SERVICE_OPENED          = blpapi.Name("ServiceOpened")
SERVICE_OPEN_FAILURE    = blpapi.Name("ServiceOpenFailure")
ERROR_INFO              = blpapi.Name("ErrorInfo")
CREATE_ORDER            = blpapi.Name("CreateOrder")
CANCEL_ROUTE            = blpapi.Name("CancelRoute")
CREATE_ORDER_AND_ROUTE_EX            = blpapi.Name("CreateOrderAndRouteEx")
SUBSCRIPTION_FAILURE            = blpapi.Name("SubscriptionFailure")
SUBSCRIPTION_STARTED            = blpapi.Name("SubscriptionStarted")
SUBSCRIPTION_TERMINATED         = blpapi.Name("SubscriptionTerminated")
_EVENT_STATUS_HEARTBEAT = 1
_EVENT_STATUS_INIT_PAINT = 4
_EVENT_STATUS_NEW_ORDER = 6
_EVENT_STATUS_UPD_ORDER = 7
_EVENT_STATUS_DELETE_ORDER = 8
_EVENT_STATUS_INIT_PAINT_END = 1
_HALTING_TIME_IN_SECONDS=300

_CANCEL_CORRELATION_ID = 90

@Singleton
class OrderRouter( BaseCommunicationModule, ICommunicationModule):

    # region Constructors

    def __init__(self):
        # region Attributes
        self.Name = "Order Router Bloomberg"
        self.Connected = False
        self.Session=None
        self.id = None
        self.MarketDataSubscriptionLock=threading.Lock()
        self.CandleBarSubscriptionLock = threading.Lock()
        self.HistoricalPricesSubscriptionLock = threading.Lock()
        self.ActiveOrdersLock = threading.Lock()

        self.ClOrdIdsTranslators = {}
        self.PendingNewOrders = {}

        self.ApiSeqNum = 0

        self.ExecutionReportsPendinToBeSent = []

        self.MarketDataSubscriptions = {}
        self.CandleBarSubscriptions = {}

        self.PendingCancels = {}
        self.ActiveOrders = {}
        self.ExternalOrders = {}
        self.ExternalExecutionReports = {}

        self.PreExitingOrders=[]
        self.PreExistingExecutionReports=[]

        self.MaxOrderPerSecondDict = {}
        self.LastHaltingTime=None

        self.InitialPaintOrder = False
        self.InitialPaintExecutionReports=False

        self.OnMarketData=None
        self.OnExecutionReport=None
        self.Initialized=False
        # endregion

    # endregion

    # region Private Methods

    def ValidateMarketDataPacing(self,marketdata):


        if marketdata.Timestamp is not None:

            secElapsed = int( abs((datetime.now()- marketdata.Timestamp).seconds))

            return secElapsed >= self.Configuration.MarketDataUpdateFreqSeconds or  self.Configuration.MarketDataUpdateFreqSeconds is None
        else:
            return True


    def UpdateAndSendCandlebar(self,msg,candlebar,isStart):
        if self.ValidateMarketDataPacing(candlebar) or isStart:
            SubscriptionHelper.UpdateCandleBar(self, msg, candlebar,isStart)
            LogHelper.LogPublishCandleBarOnSecurity("Bloomberg Order Router",self, candlebar.Security.Symbol, candlebar)
            cbWrapper = CandleBarDataWrapper(self, candlebar)
            self.OnMarketData.ProcessIncoming(cbWrapper)

    def ValidateMaxOrdersPerSecondLimit(self):
        now = datetime.now()  # current date and time
        strNow = now.strftime("%m/%d/%Y, %H:%M:%S")

        if(self.LastHaltingTime is not None):
            elapsed=(now-self.LastHaltingTime)
            if elapsed.seconds > _HALTING_TIME_IN_SECONDS:
                self.LastHaltingTime=None
            else:
                self.DoLog( "Not allowed to route orders for 5 minutes (max orders per second halting validation activated)",MessageType.INFO)
                return False

        if not strNow in self.MaxOrderPerSecondDict:
            self.MaxOrderPerSecondDict[strNow]=1
            return True
        else:
            currentCount = self.MaxOrderPerSecondDict[strNow]
            if(currentCount<self.Configuration.MaxOrdersPerSecond):
                self.MaxOrderPerSecondDict[strNow]+=1
                return True
            else:
                self.DoLog("Halting execution because of Dead Man Switch (max orders per second) activated",MessageType.INFO)
                self.LastHaltingTime=now
                return False

    def FetchPreExistingOrder(self,orderId):
        order = None

        for x in self.PreExitingOrders:
            if x.OrderId == orderId:
                order = x
                break

        return order

    def FetchActiveOrder(self,msg):
        try:
            if(msg.hasElement("EMSX_SEQUENCE")):
                EMSX_SEQUENCE = msg.getElementAsString("EMSX_SEQUENCE")

                activeOrder = None
                self.ActiveOrdersLock.acquire()
                try:
                    if EMSX_SEQUENCE in self.ActiveOrders:
                        activeOrder = self.ActiveOrders[EMSX_SEQUENCE]
                    else:
                        activeOrder= self.FetchPreExistingOrder(EMSX_SEQUENCE)
                finally:
                    if self.ActiveOrdersLock.locked():
                        self.ActiveOrdersLock.release()
                return activeOrder
            else:
                return None
        except Exception as e:
            self.DoLog("Error searching for orders for EMSX_SEQUENCE {}:{}".format(BloombergTranslationHelper.GetSafeString(self,msg,"EMSX_SEQUENCE","?"),e), MessageType.ERROR)
            raise e
        finally:
            if self.ActiveOrdersLock.locked():
                self.ActiveOrdersLock.release()

    def FetchExternalOrders(self,msg):
        try:
            if(BloombergTranslationHelper.GetSafeString(self,msg,"EMSX_SEQUENCE",None) is not None):
                EMSX_SEQUENCE = BloombergTranslationHelper.GetSafeString(self,msg,"EMSX_SEQUENCE",None)

                self.ActiveOrdersLock.acquire()

                if EMSX_SEQUENCE in self.ExternalOrders:
                    return self.ExternalOrders[EMSX_SEQUENCE]
                else:
                    return None

            else:
                return None
        except Exception as e:
            self.DoLog("Error searching for external orders for EMSX_SEQUENCE {}:{}".format(BloombergTranslationHelper.GetSafeString(self,msg,"EMSX_SEQUENCE","?"),e), MessageType.ERROR)
            raise e
        finally:
            if self.ActiveOrdersLock.locked():
                self.ActiveOrdersLock.release()

    def ProcessOrderInitialPaint(self,msg):
        try:
            self.ActiveOrdersLock.acquire()
            order = SubscriptionHelper.BuildOrder(self,msg)
            self.PreExitingOrders.append(order)
        finally:
            self.ActiveOrdersLock.release()

    def ProcessExecutionReportsInitialPaint(self,msg):
        try:
            self.ActiveOrdersLock.acquire()
            execReport = SubscriptionHelper.BuildExecutionReport(self,msg)
            self.PreExistingExecutionReports.append(execReport)
        finally:
            self.ActiveOrdersLock.release()

    def DoSendExecutionReportThread(self,execReport):

        try:

            if(self.Configuration.ImplementMock):
                self.OnExecutionReport.ProcessOutgoing(execReport)
            else:
                if self.InitialPaintExecutionReports and self.InitialPaintOrder:
                    self.OnExecutionReport.ProcessOutgoing(execReport)
                else:#the initial paint is still in progress
                    self.ExecutionReportsPendinToBeSent.append(execReport)


        except Exception as e:
            self.DoLog("Error sending execution report:{}".format(str(e)), MessageType.ERROR)

    def DoSendExternalExecutionReport(self,extOrder,execReport):
        try:
            extExecReportWr = GenericExecutionReportWrapper(pOrder= extOrder,pExecutionReport=execReport)

            if extOrder.OrderId not in self.ExternalExecutionReports:
                self.ExternalExecutionReports[extOrder.OrderId]= queue.Queue(maxsize=1000000)

            self.ExternalExecutionReports[extOrder.OrderId].put(extExecReportWr)
            time.sleep(self.Configuration.ExternalOrdersPacingSeconds)
            if extOrder.OrderId in self.ExternalExecutionReports:
                while not self.ExternalExecutionReports[extOrder.OrderId].empty():
                    self.DoLog("Sending ExecReport for external order. OrderId={} Symbol={}".format(extOrder.OrderId,extOrder.Security.Symbol),
                               MessageType.INFO)
                    execReportWr = self.ExternalExecutionReports[extOrder.OrderId].get()
                    self.DoSendExecutionReportThread(execReportWr)

        except Exception as e:
            self.DoLog("ERROR sending external execution report:{}".format(str(e)), MessageType.ERROR)

    def DoSendExecutionReport(self,activeOrder,msg):
        try:
            self.ActiveOrdersLock.acquire()
            msgSeqNum=BloombergTranslationHelper.GetSafeInt(self,msg,"API_SEQ_NUM",0)


            if msgSeqNum>=self.ApiSeqNum:
                self.ApiSeqNum=msgSeqNum
                if activeOrder is not None:
                    activeOrder.OrdStatus = BloombergTranslationHelper.GetOrdStatus(self,msg)

                self.DoLog("Bloomberg Order Router: Sending message with SeqNum {} for OrderId{} AvgPx={}"
                           .format(msgSeqNum,activeOrder.OrderId if activeOrder is not None else "",
                                   BloombergTranslationHelper.GetSafeFloat(self,msg, "EMSX_AVG_PRICE",0)), MessageType.DEBUG)
                execReport = ExecutionReportWrapper(activeOrder,msg,pParent=self)
                #if(execReport.GetExecType()==ExecType.Canceled):
                    #print("Received canceled exec report for security {}".format(execReport.GetField(ExecutionReportField.Symbol)))
                self.DoSendExecutionReportThread(execReport)
                time.sleep(50 / 1000)
            else:
                self.DoLog("Ignoring execution report because out of sync with seq num {}".format(msgSeqNum),MessageType.WARNING)
        finally:
            self.ActiveOrdersLock.release()
        #threading.Thread(target=self.DoSendExecutionReportThread, args=(execReport,)).start()

    def LoadConfig(self):
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True

    def ProcessSessionStatusEvent(self, event, session):

        self.DoLog("Processing Bloomberg SESSION_STATUS event", MessageType.INFO)

        for msg in event:
            if msg.messageType() == SESSION_STARTED:
                self.DoLog("Bloomberg Session started...",MessageType.INFO)
                self.Session= session
                self.Session.openServiceAsync(self.Configuration.EMSX_Environment)
                self.Connected=True

            elif msg.messageType() == SESSION_STARTUP_FAILURE:
                self.DoLog("Bloomberg Session failed to start...", MessageType.ERROR)
                self.Session=session
                self.Connected = False

            elif msg.messageType() == SESSION_TERMINATED:
                self.DoLog("Bloomberg Session Terminated...", MessageType.ERROR)
                self.Session=session
                self.Connected = False

            elif msg.messageType() == SESSION_CONNECTION_UP:
                self.DoLog("Bloomberg Session Connection is UP...", MessageType.INFO)
                self.Connected = True

            elif msg.messageType() == SESSION_CONNECTION_DOWN:
                self.DoLog("Bloomberg Session Connection is DOWN...", MessageType.ERROR)
                self.Connected = False

            else:
                self.DoLog(msg, MessageType.INFO)

    def ProcessServiceStatusEvent(self, event, session):

        self.DoLog("Processing SERVICE_STATUS event",MessageType.INFO)

        for msg in event:

            if msg.messageType() == SERVICE_OPENED:
                svc = BloombergTranslationHelper.GetSafeString(self,msg,"serviceName",self.Configuration.EMSX_Environment)
                self.DoLog("Service {} opened...".format(svc),MessageType.INFO)

            elif msg.messageType() == SERVICE_OPEN_FAILURE:
                svc = BloombergTranslationHelper.GetSafeString(self, msg, "serviceName", self.Configuration.EMSX_Environment)
                self.DoLog("Error: Service {} failed to open".format(svc),MessageType.ERROR)
                self.Connected=False

    def ProcessSubscriptionStatusEvent(self, event, session):

        self.DoLog("@{0}:Processing {1}".format("Bloomberg Orde Router",event.eventType()),MessageType.DEBUG)

        for msg in event:

            if msg.messageType() == SUBSCRIPTION_STARTED:

                if msg.correlationIds()[0].value() == orderSubscriptionID.value():
                    self.DoLog("Order subscription started successfully",MessageType.INFO)

                elif msg.correlationIds()[0].value() == routeSubscriptionID.value():
                    self.DoLog("Route subscription started successfully",MessageType.INFO)

            elif msg.messageType() == SUBSCRIPTION_FAILURE:
                reason = msg.getElement("reason")
                errorcode = reason.getElementAsInteger("errorCode")
                description = reason.getElementAsString("description")
                symbol = msg.correlationIds()[0].value()

                self.DoLog("Error Subscribing to Bloomberg Events:{}-{} (Symbol {})".format(errorcode,description,symbol),MessageType.ERROR)

            elif msg.messageType() == SUBSCRIPTION_TERMINATED:
                self.DoLog("Subscription terminated connected to Bloomberg Events:{}".format(msg),MessageType.ERROR)

    def ProcessMiscEvents(self, event):

        self.DoLog("Processing {} event".format(str(event.eventType())),MessageType.DEBUG)

        for msg in event:
            self.DoLog("MESSAGE: %s" % (str(msg)),MessageType.DEBUG)

    def ProcessHistoricalPrice(self,msg):

        try:
            sec = SubscriptionHelper.ExtractSecurity(self, msg)
            if sec is not None:
                histPricesWrapper = HistoricalPricesWrapper(self,TimeUnit.Day,msg)
                self.OnMarketData.ProcessIncoming(histPricesWrapper)
            else:
                raise Exception("Could not find security when recovering market data:{}".format(str(msg)))
        except Exception as e:
            errWrapper =  ErrorWrapper(Exception("Error recovering historical price:{}".format(str(e))))
            self.OnMarketData.ProcessIncoming(errWrapper)
            self.DoLog("Error @ProcessHistoricalPrice:{}".format(str(e)), MessageType.ERROR)

    def ProcessResponseEvent(self, event):

        for msg in event:

            if msg.correlationIds()[0].value() in self.PendingNewOrders:
                activeOrder = self.PendingNewOrders[msg.correlationIds()[0].value()]

                if msg.messageType() == ERROR_INFO:

                    errorCode = msg.getElementAsInteger("ERROR_CODE")
                    errorMessage = msg.getElementAsString("ERROR_MESSAGE")
                    errorMsg = "{}-{}".format(errorCode,errorMessage)

                    activeOrder.OrdStatus=OrdStatus.Rejected
                    activeOrder.RejReason = errorMsg

                    execReportWrapper = RejectedExecutionReportWrapper(activeOrder, errorMsg)
                    self.OnExecutionReport.ProcessOutgoing(execReportWrapper)
                    self.DoLog("Received rejection for order {}:{}".format(activeOrder.ClOrdId,errorMessage),MessageType.INFO)

                elif msg.messageType() == CREATE_ORDER_AND_ROUTE_EX:

                    if  msg.hasElement("EMSX_SEQUENCE"):

                        emsxSequence = msg.getElementAsString("EMSX_SEQUENCE")
                        message = msg.getElementAsString("MESSAGE")

                        activeOrder.OrderId = emsxSequence
                        activeOrder.OrdStatus = OrdStatus.PendingNew
                        activeOrder.MarketArrivalTime = datetime.now()
                        self.ActiveOrders[emsxSequence]=activeOrder

                        if emsxSequence in self.ExternalExecutionReports:
                            del self.ExternalExecutionReports[emsxSequence]

                        if emsxSequence in self.ExternalOrders:
                            del self.ExternalOrders[emsxSequence]
                        self.DoLog("EMSX_Sequence assigned for Order {}:{} - Message={}".format(activeOrder.ClOrdId,
                                                                                                emsxSequence, message), MessageType.INFO)
                        # this is not a New message- This just means that the order was sent to the exchange
                        # The New status will be received through ProcessSubscriptionStatusEvent

                #global bEnd
                #bEnd = True
            elif msg.correlationIds()[0].value() in self.PendingCancels:
                cancelOrder = self.PendingCancels[msg.correlationIds()[0].value()]
                del self.PendingCancels[msg.correlationIds()[0].value()]
                if msg.messageType() == ERROR_INFO:
                    errorCode = msg.getElementAsInteger("ERROR_CODE")
                    errorMessage = msg.getElementAsString("ERROR_MESSAGE")
                    wrapper = OrderCancelRejectWrapper(pText="{}-{}".format(errorCode,errorMessage),
                                                       pCxlRejResponseTo=CxlRejResponseTo.OrderCancelRequest,
                                                       pCxlRejReason=CxlRejReason.Other,
                                                       pOrder= cancelOrder,pClOrdId=None,pOrigClOrdId=None,pOrderId=None)
                    self.OnExecutionReport.ProcessOutgoing(wrapper)
                    self.DoLog("Received Rejected cancellation for ClOrdId={}.Error Code={} Error Msg={}".format(msg.correlationIds()[0].value(),errorCode,errorMessage),MessageType.DEBUG)
                elif msg.messageType() == CANCEL_ROUTE:
                    status = msg.getElementAsInteger("STATUS")
                    message = msg.getElementAsString("MESSAGE")
                    self.DoLog("Received Pending Cancel confirmation for ClOrdId={}.Status={} Msg={}".format(
                        msg.correlationIds()[0].value(), status, message), MessageType.DEBUG)
            elif msg.messageType() == HISTORICAL_DATA_REPONSE:
                self.ProcessHistoricalPrice(msg)
            else:
                self.DoLog("Received response for unknown CorrelationId {}".format(msg.correlationIds()[0].value()),MessageType.INFO)

    def ProcessInitialPaint(self,msg):
        if msg.correlationIds()[0].value() == orderSubscriptionID.value():
            self.ProcessOrderInitialPaint(msg)
        elif msg.correlationIds()[0].value() == routeSubscriptionID.value():
            self.ProcessExecutionReportsInitialPaint(msg)
        else:
            self.DoLog("Received INIT_PAINT for unknown correlation id: {}".format(msg.correlationIds()[0].value()),MessageType)

    def ProcessInitialPaintEnd(self,msg):
        if msg.correlationIds()[0].value() == routeSubscriptionID.value():
            self.InitialPaintExecutionReports = True
        elif msg.correlationIds()[0].value() == orderSubscriptionID.value():
            self.InitialPaintOrder = True
        else:
            self.DoLog("Received Initial Paint End for unknown correlation id. ".format(msg.correlationIds()[0].value()),MessageType.ERROR)

    def ProcessOrdersFromExchange(self,msg):
        if (self.FetchActiveOrder(msg) is None
                and BloombergTranslationHelper.GetSafeString(self, msg, "EMSX_SEQUENCE", None) is not None
                and BloombergTranslationHelper.GetSafeString(self, msg,"EMSX_TICKER",None) is not None):

            unkOrder = SubscriptionHelper.BuildOrder(self, msg)
            unkOrder.ClOrdId=uuid.uuid4()
            self.ExternalOrders[unkOrder.OrderId]=unkOrder



    def ProcessExecutionReports(self,msg):
        eventStatus = msg.getElementAsInteger("EVENT_STATUS")

        if msg.correlationIds()[0].value() == routeSubscriptionID.value():  # we only want execution reports to be updated

            activeOrder = self.FetchActiveOrder(msg)

            if activeOrder is not None:

                if (eventStatus == _EVENT_STATUS_NEW_ORDER or eventStatus == _EVENT_STATUS_UPD_ORDER or eventStatus == _EVENT_STATUS_DELETE_ORDER):
                    self.DoLog("Received execution report for order {}. EMSX_SEQUENCE= {}".format(activeOrder.ClOrdId,activeOrder.OrderId),MessageType.DEBUG)
                    self.DoSendExecutionReport(activeOrder, msg)
            elif self.FetchExternalOrders(msg) is not None:
                if (eventStatus == _EVENT_STATUS_NEW_ORDER or eventStatus == _EVENT_STATUS_UPD_ORDER or eventStatus == _EVENT_STATUS_DELETE_ORDER):
                    extOrder =self.FetchExternalOrders(msg)
                    self.DoLog("Received execution report for potential external order -> EMSX_SEQUENCE= {}".format(extOrder.OrderId),MessageType.DEBUG)
                    extExecReport= SubscriptionHelper.BuildExecutionReport(self,msg)
                    threading.Thread(target=self.DoSendExternalExecutionReport, args=(extOrder,extExecReport)).start()
            else:
                self.DoLog("Received response for unknown order:{}.".format(msg), MessageType.DEBUG)
        elif msg.correlationIds()[0].value() == orderSubscriptionID.value():
            self.ProcessOrdersFromExchange(msg)
            self.DoLog("Saving order for potential external trading analysis", MessageType.DEBUG)

        else:
            self.DoLog( "Received Subscription Event for unknown correlationId= {}".format(msg.correlationIds()[0].value()),MessageType.DEBUG)

    def ProcessMarketData(self,msg):
        if msg.correlationIds()[0].value() in self.MarketDataSubscriptions:
            symbol = msg.correlationIds()[0].value()
            sec = self.MarketDataSubscriptions[msg.correlationIds()[0].value()]
            if self.ValidateMarketDataPacing(sec.MarketData):
                SubscriptionHelper.UpdateMarketData(self, msg, sec.MarketData)
                LogHelper.LogPublishMarketDataOnSecurity("Bloomberg Order Router",self, symbol, sec.MarketData)
                mdWrapper = MarketDataWrapper(sec.MarketData)
                self.OnMarketData.ProcessIncoming(mdWrapper)
        else:
            self.DoLog( "Received market data for unknown subscription. Symbol= {}".format(msg.correlationIds()[0].value()),MessageType.ERROR)

    def ProcessCandlebarStart(self,msg):
        symbol = msg.correlationIds()[0].value()
        if symbol in self.CandleBarSubscriptions:
            cb = self.CandleBarSubscriptions[symbol]
            cb = CandleBar(cb.Security)
            self.UpdateAndSendCandlebar(msg, cb,isStart=True)
        else:
            self.DoLog( "Received candlebar for unknown subscription. Symbol= {}".format(msg.correlationIds()[0].value()), MessageType.ERROR)

    def ProcessCandlebarUpdate(self,msg):
        symbol = msg.correlationIds()[0].value()
        if symbol in self.CandleBarSubscriptions:
            cb = self.CandleBarSubscriptions[symbol]
            self.UpdateAndSendCandlebar(msg, cb,isStart=False)
        else:
            self.DoLog("Received candlebar for unknown subscription. Symbol= {}".format(msg.correlationIds()[0].value()),MessageType.ERROR)

    def ProcessSubscriptionDataEvent(self, event):
        for msg in event:

            if msg.messageType() == ORDER_ROUTE_FIELDS:
                eventStatus = msg.getElementAsInteger("EVENT_STATUS")
                if eventStatus ==_EVENT_STATUS_INIT_PAINT:
                    self.ProcessInitialPaint(msg)
                elif eventStatus == _EVENT_STATUS_INIT_PAINT_END:
                    self.ProcessInitialPaintEnd(msg)
                else:
                    self.ProcessExecutionReports(msg)
            elif msg.messageType() == MARKET_DATA_EVENTS:
                self.ProcessMarketData(msg)
            elif msg.messageType() == MARKET_BAR_START:
                self.ProcessCandlebarStart(msg)
            elif (msg.messageType() == MARKET_BAR_UPDATE or msg.messageType() == MARKET_BAR_INTERVAL_END or  msg.messageType() == MARKET_BAR_END):
                self.ProcessCandlebarUpdate(msg)
            else:

                self.DoLog("Received message for not tracked message type . MsgType= {}".format(msg.messageType()),MessageType.ERROR)

    def ProcessEvent(self, event, session):
        try:
            if event.eventType() == blpapi.Event.SESSION_STATUS:
                self.ProcessSessionStatusEvent(event, session)

            elif event.eventType() == blpapi.Event.SERVICE_STATUS:
                self.ProcessServiceStatusEvent(event, session)

            elif event.eventType() == blpapi.Event.RESPONSE:
                self.ProcessResponseEvent(event)

            elif event.eventType() == blpapi.Event.PARTIAL_RESPONSE:
                self.ProcessResponseEvent(event)

            elif event.eventType() == blpapi.Event.SUBSCRIPTION_DATA:
                self.ProcessSubscriptionDataEvent(event)

            elif event.eventType() == blpapi.Event.SUBSCRIPTION_STATUS:
                self.ProcessSubscriptionStatusEvent(event,session)

            else:
                self.ProcessMiscEvents(event)

        except Exception as e:
            traceback.print_exc()
            self.DoLog("Error processing Bloomberg event ({} @ProcessEvent) @OrderRouter.Bloomberg module:{}".format(event.eventType(),str(e)), MessageType.ERROR)


    def LoadNoneStrategy(self, request):
        strategy = request.getElement("EMSX_STRATEGY_PARAMS")
        strategy.setElement("EMSX_STRATEGY_NAME", "none")

        indicator = strategy.getElement("EMSX_STRATEGY_FIELD_INDICATORS")
        data = strategy.getElement("EMSX_STRATEGY_FIELDS")

        # Strategy parameters must be appended in the correct order. See the output
        # of GetBrokerStrategyInfo request for the order. The indicator value is 0 for
        # a field that carries a value, and 1 where the field should be ignored

        data.appendElement().setElement("EMSX_FIELD_DATA", "09:30:00")  # StartTime
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 0)

        data.appendElement().setElement("EMSX_FIELD_DATA", "10:30:00")  # EndTime
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 0)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # Max%Volume
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # %AMSession
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # OPG
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # MOC
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # CompletePX
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # TriggerPX
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # DarkComplete
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # DarkCompPX
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # RefIndex
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # Discretion
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

    def LoadStrategy(self, request, strategy_name):
        strategy = request.getElement("EMSX_STRATEGY_PARAMS")
        strategy.setElement("EMSX_STRATEGY_NAME", strategy_name)

        indicator = strategy.getElement("EMSX_STRATEGY_FIELD_INDICATORS")
        data = strategy.getElement("EMSX_STRATEGY_FIELDS")

        # Strategy parameters must be appended in the correct order. See the output
        # of GetBrokerStrategyInfo request for the order. The indicator value is 0 for
        # a field that carries a value, and 1 where the field should be ignored

        
        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # Display Quantity:
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # Aggressiveness
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

      

    def LoadSession(self):

        sessionOptions = SessionOptions()
        sessionOptions.setServerHost(self.Configuration.Server)
        sessionOptions.setServerPort(self.Configuration.Port)

        self.DoLog("Connecting to %s:%d" % (self.Configuration.Server, self.Configuration.Port), MessageType.INFO)

        self.Session = Session(sessionOptions, self.ProcessEvent)

        if not self.Session.startAsync():
            self.DoLog("Failed to start session.", MessageType.INFO)
            self.Connected = False
            return

        # global bEnd
        # while bEnd == False:
        #    pass

        # session.stop()

    def ProcessRejectedExecutionReport(self, wrapper,reason):
        newOrder = OrderConverter.ConvertNewOrder(self, wrapper)

        execReportWrapper = RejectedExecutionReportWrapper(newOrder,reason)
        self.OnExecutionReport.ProcessOutgoing(execReportWrapper)

        errorWrapper = ErrorWrapper(Exception(reason))
        self.OnExecutionReport.ProcessOutgoing(errorWrapper)
        return CMState.BuildSuccess(self)

    def CreateRequest(self, newOrder,svc):
        service = self.Session.getService(self.Configuration.EMSX_Environment)

        request = service.createRequest(svc)

        # The fields below are mandatory
        request.set("EMSX_TICKER", "{} {} {}".format(newOrder.Security.Symbol,
                                                     newOrder.Security.Exchange if newOrder.Security.Exchange is not None else self.Configuration.Exchange,
                                                     BloombergTranslationHelper.GetBloombergSecType(newOrder.Security.SecurityType) if newOrder.Security.SecurityType is not None else self.Configuration.SecurityType))
        request.set("EMSX_AMOUNT", newOrder.OrderQty)
        request.set("EMSX_ORDER_TYPE", BloombergTranslationHelper.GetBloombergOrdType(self,newOrder.OrdType))
        request.set("EMSX_TIF", self.Configuration.DefaultTIF)
        request.set("EMSX_HAND_INSTRUCTION", self.Configuration.HandInst)
        request.set("EMSX_SIDE", BloombergTranslationHelper.GetBloombergSide(self,newOrder.Side))

        if(newOrder.OrdType==OrdType.Limit and newOrder.Price is not None):
            request.set("EMSX_LIMIT_PRICE", float(newOrder.Price))

        if(newOrder.Broker is not None):
            request.set("EMSX_BROKER", newOrder.Broker)
        else:
            request.set("EMSX_BROKER", self.Configuration.DefaultBroker)

        if(newOrder.Account is not None):
            request.set("EMSX_ACCOUNT", newOrder.Account)

        if(self.Configuration.ImplementStrategy is not None and self.Configuration.ImplementStrategy =="OMEGA2") :
            self.LoadStrategy(request,self.Configuration.ImplementStrategy)
        elif (self.Configuration.ImplementStrategy is not None and self.Configuration.ImplementStrategy == "NONE"):
            self.LoadNoneStrategy(request)

        return request

    def ProcessOrderCancelReject(self,orderId,ex):

        try:
            msg = "Error processing order cancel request for orderId {}: {} ".format(orderId,str(ex))
            order=self.ActiveOrders[orderId] if (orderId is not None and orderId in self.ActiveOrders) else None
            rejWrapper = OrderCancelRejectWrapper(pText=msg, pCxlRejResponseTo=CxlRejResponseTo.OrderCancelRequest,
                                                  pCxlRejReason=CxlRejReason.Other,pOrder=order)
            self.OnExecutionReport.ProcessOutgoing(rejWrapper)

        except Exception as e:
            msg = "Critical Error @ProcessOrderCancelReject @OrderRouter.Bloomberg module :{}".format(str(e))
            self.DoLog(msg, MessageType.ERROR)


    def DoCancel(self,activeOrder):
        service = self.Session.getService(self.Configuration.EMSX_Environment)

        request = service.createRequest("CancelRoute")

        routes = request.getElement("ROUTES")

        route = routes.appendElement()
        route.getElement("EMSX_SEQUENCE").setValue(activeOrder.OrderId)
        route.getElement("EMSX_ROUTE_ID").setValue(1)

        requestID = blpapi.CorrelationId(activeOrder.ClOrdId)

        self.PendingCancels[activeOrder.ClOrdId] = activeOrder

        self.Session.sendRequest(request, correlationId=requestID)


    def FetchOrderByIds(self,wrapper):
        clOrdId = wrapper.GetField(OrderField.ClOrdID)
        orderId = wrapper.GetField(OrderField.OrderId)
        if (orderId is not None and orderId in self.ActiveOrders):
            return self.ActiveOrders[orderId]
        elif(clOrdId is not None):
            return next(iter(list(filter(lambda x: x.ClOrdId is not None and x.ClOrdId == clOrdId, self.ActiveOrders.values()))),None)
        else:
            raise Exception("Could not find an order for OrderId {} - ClOrdId {}".format(orderId if orderId is not None else "-",clOrdId if clOrdId is not None else "-" ))
            #return None

    def CancelOrder(self,wrapper):

        self.ActiveOrdersLock.acquire()
        orderId = None
        try:

            order= self.FetchOrderByIds(wrapper)

            if order is not None and order.IsOpenOrder():
                orderId = order.OrderId
                self.DoCancel(order)
            else:
                raise Exception("OrderId {} is not an active order".format(orderId))

        except Exception as e:
            self.ProcessOrderCancelReject(orderId,e)
        finally:
            if self.ActiveOrdersLock.locked():
                self.ActiveOrdersLock.release()


    def CancellAllOrders(self,wrapper):


        self.ActiveOrdersLock.acquire()

        for orderId in self.ActiveOrders:
            try:
                if self.ActiveOrders[orderId].IsOpenOrder():
                    activeOrder = self.ActiveOrders[orderId]
                    self.DoCancel(activeOrder)

            except Exception as e:
               self.ProcessOrderCancelReject(orderId,e)

        self.ActiveOrdersLock.release()

    def SendMockFilledExecutionReportsThread(self,newOrder):
        try:

            newOrder.OrderId = int(time.time())
            newOrder.MarketArrivalTime = datetime.now()
            self.ActiveOrders[newOrder.OrderId] = newOrder

            newWrapper = NewExecutionReportWrapper(newOrder)
            self.DoSendExecutionReportThread(newWrapper)
            time.sleep(self.Configuration.SecondsToSleepOnTradeForMock)

            lastCandlebar = None
            fullSymbol = "{} {} {}".format(newOrder.Security.Symbol,
                                           newOrder.Security.Exchange if newOrder.Security.Exchange is not None else self.Configuration.Exchange,
                                           BloombergTranslationHelper.GetBloombergSecType(newOrder.Security.SecurityType) if newOrder.Security.SecurityType is not None else self.Configuration.SecurityType)

            if fullSymbol in  self.CandleBarSubscriptions:
               lastCandlebar = self.CandleBarSubscriptions[fullSymbol]

            executionPrice = newOrder.Price if newOrder.Price is not None else (lastCandlebar.Close if lastCandlebar is not None else None)

            filledWrapper = FilledExecutionReportWrapper(newOrder,executionPrice)
            self.DoSendExecutionReportThread(filledWrapper)

        except Exception as e:
            msg = "Critical error @SendMockFilledExecutionReportsThread:{}".format(str(e))
            self.DoLog(msg, MessageType.ERROR)
            errorWrapper = ErrorWrapper(e)
            self.OnMarketData.ProcessIncoming(errorWrapper)


    def ProcessNewOrderMock(self,wrapper):

        newOrder = OrderConverter.ConvertNewOrder(self, wrapper)

        if self.Configuration.MockSendsToBloomberg:

            if not self.Connected:
                return self.ProcessRejectedExecutionReport(wrapper, "Not Connected to Bloomberg")

            request = self.CreateRequest(newOrder,"CreateOrder")

            LogHelper.LogNewOrder(self, newOrder)

            requestID = blpapi.CorrelationId(newOrder.ClOrdId)

            self.ClOrdIdsTranslators[requestID.value()] = newOrder.ClOrdId
            self.PendingNewOrders[requestID.value()] = newOrder

            self.Session.sendRequest(request, correlationId=requestID)

        threading.Thread(target=self.SendMockFilledExecutionReportsThread, args=(newOrder,)).start()

    def ProcessNewOrder(self, wrapper):

        if not self.Connected:
            return self.ProcessRejectedExecutionReport(wrapper, "Not Connected to Bloomberg")

        if self.ValidateMaxOrdersPerSecondLimit() == False:
            return self.ProcessRejectedExecutionReport(wrapper, "Max orders per second limit surpassed! Wait 5 minutes after {}".format(self.LastHaltingTime))

        newOrder = OrderConverter.ConvertNewOrder(self, wrapper)

        request = self.CreateRequest(newOrder,"CreateOrderAndRouteEx")

        LogHelper.LogNewOrder(self,newOrder)

        requestID = blpapi.CorrelationId(newOrder.ClOrdId)

        self.ClOrdIdsTranslators[requestID.value()] = newOrder.ClOrdId
        self.PendingNewOrders[requestID.value()] = newOrder

        self.Session.sendRequest(request, correlationId=requestID)

    def ProcessExecutionReportListThread(self,wrapper):

        try:
            MAX_ATTEMPTS=self.Configuration.InitialRecoveryTimeoutInSeconds
            i=1
            while (self.InitialPaintOrder==False or self.InitialPaintExecutionReports==False):
                i+=1
                self.DoLog("Waiting initial paints to finish to return active execution reports",MessageType.INFO)
                time.sleep(int(1))

                if i>MAX_ATTEMPTS:
                    raise Exception("Timeout waiting for the previous orders")

            self.ActiveOrdersLock.acquire()

            executionReportWrappersList = []
            for execReport in self.PreExistingExecutionReports:
                order = self.FetchPreExistingOrder(execReport.Order.OrderId) if execReport.Order is not None else None

                if order is not None:
                    execReportWrapper = GenericExecutionReportWrapper(order,execReport)
                    #self.DoLog("Initial Load for Exec Report for OrderId={} AvgPx={}".format(order.OrderId,execReport.AvgPx),MessageType.INFO)
                else:
                    tempOrder = Order()
                    tempOrder.OrderId=execReport.Order.OrderId if execReport.Order is not None else None
                    execReportWrapper = ExecutionReportWrapper(tempOrder, execReport,pParent=self)

                executionReportWrappersList.append(execReportWrapper)
                if order is not None and order.IsOpenOrder() and execReport.LeavesQty>0:
                    self.ActiveOrders[order.OrderId]=order

            self.DoLog("Recovered {} previously existing execution reports".format(len(executionReportWrappersList)),MessageType.INFO)
            wrapper = ExecutionReportListWrapper(executionReportWrappersList)
            self.OnExecutionReport.ProcessOutgoing(wrapper)

            self.ActiveOrdersLock.release()

            for execReport in self.ExecutionReportsPendinToBeSent:
                self.DoSendExecutionReport(execReport)


        finally:
            if self.ActiveOrdersLock.locked():
                self.ActiveOrdersLock.release()

    def ProcessExecutionReportList(self,wrapper):
        threading.Thread(target=self.ProcessExecutionReportListThread, args=(wrapper,)).start()
        self.DoLog("Subscribing to order and route events", MessageType.INFO)
        SubscriptionHelper.CreateOrderSubscription(self, self.Configuration.EMSX_Environment, self.Session)
        SubscriptionHelper.CreateRouteSubscription(self, self.Configuration.EMSX_Environment, self.Session)
        return CMState.BuildSuccess(self)


    def ProcessCandleBarRequest(self,wrapper):
        cbReq = MarketDataRequestConverter.ConvertCandleBarRequest( wrapper)
        try:

            if cbReq.TimeUnit != TimeUnit.Minute:
                raise Exception("Not valid time unit for candle bar request {}".format(cbReq.TimeUnit))

            self.CandleBarSubscriptionLock.acquire()
            if cbReq.SubscriptionRequestType == SubscriptionRequestType.Unsuscribe:

                self.DoLog("Bloomberg Order Router: Received Bar Subscription Request for symbol:{}".format(cbReq.Security.Symbol), MessageType.INFO)
                blSymbol = "{} {} {}".cbReq(cbReq.Security.Symbol,
                                           BloombergTranslationHelper.GetBloombergExchange(cbReq.Security.Exchange),
                                           BloombergTranslationHelper.GetBloombergSecType(cbReq.Security.SecurityType))
                if blSymbol in self.CandleBarSubscriptions:
                    del self.CandleBarSubscriptions[blSymbol]
                    requestID = blpapi.CorrelationId(blSymbol)
                    SubscriptionHelper.EndCandleBarSubscription(self.Session,self.Configuration.MktBar_Environment, blSymbol,cbReq.Time, requestID)
                else:
                    self.DoLog("Symbol {} is not currently subscribed for candle bars".format(blSymbol))
            else:
                self.DoLog("Bloomberg Order Router: Received Candle Bars Subscription Request for symbol:{}".format(cbReq.Security.Symbol), MessageType.INFO)
                blSymbol = "{} {} {}".format(cbReq.Security.Symbol,
                                           BloombergTranslationHelper.GetBloombergExchange(cbReq.Security.Exchange),
                                           BloombergTranslationHelper.GetBloombergSecType(cbReq.Security.SecurityType))
                requestID = blpapi.CorrelationId(blSymbol)

                self.CandleBarSubscriptions[blSymbol] = CandleBar(cbReq.Security)
                SubscriptionHelper.CreateCandleBarSubscription(self.Session,self.Configuration.MktBar_Environment, blSymbol,cbReq.Time, requestID)
        except Exception as e:
            msg = "Critical error subscribing for candlebars for symbol {}:{}".format(cbReq.Security.Symbol, str(e))
            self.DoLog(msg, MessageType.ERROR)
            errorWrapper = ErrorWrapper(e)
            self.OnMarketData.ProcessIncoming(errorWrapper)

        finally:
            if self.CandleBarSubscriptionLock.locked():
                self.CandleBarSubscriptionLock.release()

    def ProcessHistoricalPricesRequest(self,wrapper):
        hpReq = MarketDataRequestConverter.ConvertHistoricalPricesRequest( wrapper)
        try:

            if hpReq.TimeUnit != TimeUnit.Day:
                raise Exception("Not valid time unit for historical prices request {}".format(hpReq.TimeUnit))

            self.HistoricalPricesSubscriptionLock.acquire()
            if hpReq.SubscriptionRequestType == SubscriptionRequestType.Snapshot:
                self.DoLog("Bloomberg Order Router: Received Historical Prices Snapshot Subscription Request for symbol:{}".format(hpReq.Security.Symbol), MessageType.INFO)
                blSymbol = "{} {} {}".format(hpReq.Security.Symbol,
                                           BloombergTranslationHelper.GetBloombergExchange(hpReq.Security.Exchange),
                                           BloombergTranslationHelper.GetBloombergSecType(hpReq.Security.SecurityType))
                requestID = blpapi.CorrelationId(blSymbol)

                SubscriptionHelper.GetHistoricalPrices(self.Session,self.Configuration.RefData_Environment,
                                                       blSymbol,
                                                       hpReq.TimeUnit,
                                                       hpReq.Time,
                                                       requestID)
            else:
                self.DoLog("Bloomberg Order Router: Invalid subscription type for historical prices for symbol {}:{}".format(
                    hpReq.Security.Symbol,hpReq.SubscriptionRequestType), MessageType.ERROR)
        except Exception as e:
            msg = "Critical error subscribing for historical prices for symbol {}:{}".format(hpReq.Security.Symbol, str(e))
            self.DoLog(msg, MessageType.ERROR)
            errorWrapper = ErrorWrapper(e)
            self.OnMarketData.ProcessIncoming(errorWrapper)
        finally:
            if self.HistoricalPricesSubscriptionLock.locked():
                self.HistoricalPricesSubscriptionLock.release()

    def ProcessMarketDataRequest(self,wrapper):
        mdReq = MarketDataRequestConverter.ConvertMarketDataRequest(wrapper)
        try:

            self.MarketDataSubscriptionLock.acquire()
            if mdReq.SubscriptionRequestType == SubscriptionRequestType.Unsuscribe:

                self.DoLog("Bloomberg Order Router: Received Market Data Subscription Request for symbol:{0}".format(mdReq.Security.Symbol), MessageType.INFO)
                symbol = "{} {} {}".format(mdReq.Security.Symbol,
                                           BloombergTranslationHelper.GetBloombergExchange(mdReq.Security.Exchange),
                                           BloombergTranslationHelper.GetBloombergSecType(mdReq.Security.SecurityType))
                if symbol in self.MarketDataSubscriptions:
                    del self.MarketDataSubscriptions[symbol]
                    requestID = blpapi.CorrelationId(symbol)
                    SubscriptionHelper.EndMarketDataSubscription(self.Session, symbol, requestID)
                else:
                    self.DoLog("Symbol {} is not currently subscribed".format(symbol))
            else:
                self.DoLog("Bloomberg Order Router: Received Market Data Subscription Request for symbol:{0}".format(mdReq.Security.Symbol), MessageType.INFO)
                symbol = "{} {} {}".format(mdReq.Security.Symbol,
                                           BloombergTranslationHelper.GetBloombergExchange(mdReq.Security.Exchange),
                                           BloombergTranslationHelper.GetBloombergSecType(mdReq.Security.SecurityType))
                requestID = blpapi.CorrelationId(symbol)
                mdReq.Security.MarketData.Security=mdReq.Security
                self.MarketDataSubscriptions[symbol]=mdReq.Security
                SubscriptionHelper.CreateMarketDataSubscription(self.Session,symbol,requestID)
        except Exception as e:
            msg="Critical error subscribing for Market Data for symbol {}:{}".format(mdReq.Security.Symbol,str(e))
            self.DoLog(msg, MessageType.ERROR)
            errorWrapper = ErrorWrapper(e)
            self.OnMarketData.ProcessIncoming(errorWrapper)
        finally:
            if self.MarketDataSubscriptionLock.locked():
                self.MarketDataSubscriptionLock.release()

    #endregion

    # region Public Methods

    def SetOutgoingModule(self,outgoingModule):
        self.OnExecutionReport = outgoingModule

    def SetIncomingModule(self,incomingModule):
        self.OnMarketData = incomingModule

    def ProcessOutgoing(self, wrapper):
        pass

    def ProcessMessage(self, wrapper):
        try:

            if wrapper.GetAction() == Actions.NEW_ORDER:
                if(self.Configuration.ImplementMock):

                    self.ProcessNewOrderMock(wrapper)
                else:

                    self.ProcessNewOrder(wrapper)
            elif wrapper.GetAction() == Actions.UPDATE_ORDER:
                raise Exception("Update Order not implemented @Bloomberg order router")
            elif wrapper.GetAction() == Actions.CANCEL_ORDER:
                self.CancelOrder(wrapper)
            elif wrapper.GetAction() == Actions.CANCEL_ALL_POSITIONS:
                self.CancellAllOrders(wrapper)
            elif wrapper.GetAction() == Actions.EXECUTION_REPORT_LIST_REQUEST:
                self.ProcessExecutionReportList(wrapper)
            elif wrapper.GetAction() == Actions.MARKET_DATA_REQUEST:
                self.ProcessMarketDataRequest(wrapper)
            elif wrapper.GetAction() == Actions.CANDLE_BAR_REQUEST:
                self.ProcessCandleBarRequest(wrapper)
            elif wrapper.GetAction() == Actions.HISTORICAL_PRICES_REQUEST:
                self.ProcessHistoricalPricesRequest(wrapper)
            else:
                self.DoLog("Routing to market: Order Router not prepared for routing message {}".format(wrapper.GetAction()), MessageType.WARNING)

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Error running ProcessMessage @OrderRouter.Bloomberg module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def Initialize(self,pInvokingModule, pConfigFile):

        self.InvokingModule=pInvokingModule
        self.ModuleConfigFile=pConfigFile

        try:

            if  not self.Initialized:
                self.Initialized=True
                self.DoLog("Initializing Bloomberg Order Router", MessageType.INFO)
                if self.LoadConfig():

                    BloombergTranslationHelper.Init(self.Configuration.TimeZone)

                    self.LoadSession()

                    self.DoLog("Bloomberg Order Router Initialized", MessageType.INFO)
                    return CMState.BuildSuccess(self)
                else:
                    raise Exception("Unknown error initializing config file for Bloomberg Order Router")

            else:
                return CMState.BuildSuccess(self)

        except Exception as e:

            self.DoLog("Error Loading Bloomberg Order Router module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    #endregion