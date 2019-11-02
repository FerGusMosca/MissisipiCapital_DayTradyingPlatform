import blpapi
from blpapi import SessionOptions, Session

from sources.framework.common.abstract.base_communication_module import BaseCommunicationModule
from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.wrappers.execution_report_list_wrapper import *
from sources.framework.common.wrappers.generic_execution_report_wrapper import *
from sources.framework.common.enums.OrdType import *
from sources.framework.common.enums.Side import *
from sources.order_routers.bloomberg.common.configuration.configuration import Configuration
from sources.order_routers.bloomberg.common.wrappers.rejected_execution_report_wrapper import *
from sources.order_routers.bloomberg.common.wrappers.execution_report_wrapper import *
from sources.order_routers.bloomberg.common.util.subscription_helper import *
from sources.framework.common.logger.message_type import MessageType
from sources.framework.common.dto.cm_state import *
from sources.order_routers.bloomberg.common.converter.order_converter import *
from sources.framework.common.wrappers.empty_order_list_wrapper import *
import threading
import time
from datetime import datetime

ORDER_FIELDS      = blpapi.Name("OrderFields")
ORDER_ROUTE_FIELDS      = blpapi.Name("OrderRouteFields")
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
_EVENT_STATUS_INIT_PAINT_END = 11
_HALTING_TIME_IN_SECONDS=300

_CANCEL_CORRELATION_ID = 90


class OrderRouter( BaseCommunicationModule, ICommunicationModule):

    # region Constructors

    def __init__(self):
        # region Attributes
        self.Name = "Order Router Bloomberg"
        self.Connected = False
        self.Session=None
        self.id = None
        self.ActiveOrdersLock = threading.Lock()

        self.ClOrdIdsTranslators = {}
        self.PendingNewOrders = {}
        self.PendingCancels = {}
        self.ActiveOrders = {}

        self.PreExitingOrders=[]
        self.PreExistingExecutionReports=[]

        self.MaxOrderPerSecondDict = {}
        self.LastHaltingTime=None

        self.InitialPaintOrder = False
        self.InitialPaintExecutionReports=False
        # endregion

    # endregion

    # region Private Methods


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
                    pass
                    self.ActiveOrdersLock.release()
                return activeOrder
            else:
                return None
        except Exception as e:
            self.DoLog("Error searching for orders for EMSX_SEQUENCE {}:{}".format(msg.getElementAsString("EMSX_SEQUENCE") if msg.hasElement("EMSX_SEQUENCE") else "",e), MessageType.ERROR)
            raise e

    def ProcessOrderInitialPaint(self,msg):
        self.ActiveOrdersLock.acquire()
        order = SubscriptionHelper.BuildOrder(self,msg)
        self.PreExitingOrders.append(order)
        self.ActiveOrdersLock.release()

    def ProcessExecutionReportsInitialPaint(self,msg):
        self.ActiveOrdersLock.acquire()
        execReport = SubscriptionHelper.BuildExecutionReport(self,msg)
        self.PreExistingExecutionReports.append(execReport)
        self.ActiveOrdersLock.release()

    def DoSendExecutionReportThread(self,execReport):

        try:
            self.InvokingModule.ProcessOutgoing(execReport)
        except Exception as e:
            self.DoLog("Error sending execution report:{}".format(str(e)), MessageType.ERROR)

    def DoSendExecutionReport(self,activeOrder,msg):

        if activeOrder is not None:
            activeOrder.OrdStatus = BloombergTranslationHelper.GetOrdStatus(self,msg)

        execReport = ExecutionReportWrapper(activeOrder,msg,pParent=self)
        self.DoSendExecutionReportThread(execReport)
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
                self.DoLog("Service {} opened...".format(self.Configuration.EMSX_Environment),MessageType.INFO)
                self.DoLog("Subscribing to order and route events", MessageType.INFO)
                SubscriptionHelper.CreateOrderSubscription(self,self.Configuration.EMSX_Environment,self.Session)
                SubscriptionHelper.CreateRouteSubscription(self,self.Configuration.EMSX_Environment,self.Session)

            elif msg.messageType() == SERVICE_OPEN_FAILURE:
                self.DoLog("Error: Service {} failed to open".format(self.Configuration.EMSX_Environment),MessageType.ERROR)
                self.Connected=False

    def ProcessSubscriptionStatusEvent(self, event, session):

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

        self.DoLog("Processing " + event.eventType() + " event",MessageType.INFO)

        for msg in event:
            self.DoLog("MESSAGE: %s" % (msg.tostring()),MessageType.INFO)

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
                    self.InvokingModule.ProcessOutgoing(execReportWrapper)
                    self.DoLog("Received rejection for order {}:{}".format(activeOrder.ClOrdId,errorMessage),MessageType.INFO)

                elif msg.messageType() == CREATE_ORDER_AND_ROUTE_EX:

                    if  msg.hasElement("EMSX_SEQUENCE"):

                        emsxSequence = msg.getElementAsString("EMSX_SEQUENCE")
                        message = msg.getElementAsString("MESSAGE")

                        activeOrder.OrderId = emsxSequence
                        activeOrder.OrdStatus = OrdStatus.PendingNew
                        activeOrder.MarketArrivalTime = datetime.now()
                        self.ActiveOrders[emsxSequence]=activeOrder
                        self.DoLog("EMSX_Sequence assigned for Order {}:{} - Message={}".format(activeOrder.ClOrdId,
                                                                                                emsxSequence, message), MessageType.INFO)
                        # this is not a New message- This just means that the order was sent to the exchange
                        # The New status will be received through ProcessSubscriptionStatusEvent

                #global bEnd
                #bEnd = True
            if msg.correlationIds()[0].value() in self.PendingCancels:
                del self.PendingCancels[msg.correlationIds()[0].value()]
                if msg.messageType() == ERROR_INFO:
                    errorCode = msg.getElementAsInteger("ERROR_CODE")
                    errorMessage = msg.getElementAsString("ERROR_MESSAGE")
                    self.DoLog("Received Rejected cancellation for ClOrdId={}.Error Code={} Error Msg={}".format(
                        msg.correlationIds()[0].value(),errorCode,errorMessage),MessageType.ERROR)
                elif msg.messageType() == CANCEL_ROUTE:
                    status = msg.getElementAsInteger("STATUS")
                    message = msg.getElementAsString("MESSAGE")
                    self.DoLog("Received Pending Cancel confirmation for ClOrdId={}.Status={} Msg={}".format(
                        msg.correlationIds()[0].value(), status, message), MessageType.DEBUG)
            else:
                self.DoLog("Received response for unknown CorrelationId {}".format(msg.correlationIds()[0].value()),MessageType.DEBUG)

    def ProcessSubscriptionDataEvent(self, event):
        for msg in event:

            if msg.messageType() == ORDER_ROUTE_FIELDS:
                eventStatus = msg.getElementAsInteger("EVENT_STATUS")

                if eventStatus ==_EVENT_STATUS_INIT_PAINT:
                    if msg.correlationIds()[0].value() == orderSubscriptionID.value():
                        self.ProcessOrderInitialPaint(msg)
                    elif msg.correlationIds()[0].value() == routeSubscriptionID.value():
                        self.ProcessExecutionReportsInitialPaint(msg)
                    else:
                        self.DoLog("Received INIT_PAINT for unknown correlation id: {}".format( msg.correlationIds()[0].value()),MessageType)

                elif eventStatus == _EVENT_STATUS_INIT_PAINT_END:
                    if msg.correlationIds()[0].value() == routeSubscriptionID.value():
                        self.InitialPaintExecutionReports=True
                    elif  msg.correlationIds()[0].value() == orderSubscriptionID.value():
                        self.InitialPaintOrder=True
                    else:
                        self.DoLog("Received Initial Paint End for unknown correlation id. ".format( msg.correlationIds()[0].value()), MessageType.DEBUG)
                else:
                    if msg.correlationIds()[0].value() == routeSubscriptionID.value():#we only want execution reports to be updated

                        activeOrder=self.FetchActiveOrder(msg)

                        if activeOrder is not None:

                            if (   eventStatus==_EVENT_STATUS_NEW_ORDER
                                or eventStatus==_EVENT_STATUS_UPD_ORDER
                                or eventStatus==_EVENT_STATUS_DELETE_ORDER):
                                self.DoLog("Received execution report for order {}. EMSX_SEQUENCE= {}".format(activeOrder.ClOrdId,activeOrder.OrderId), MessageType.DEBUG)
                                self.DoSendExecutionReport(activeOrder,msg)
                        else:
                            self.DoLog("Received response for unknown order:{}.".format(msg),MessageType.DEBUG)
                    elif msg.correlationIds()[0].value() == orderSubscriptionID.value():
                        self.DoLog("Received order subscription event. ", MessageType.DEBUG)
                    elif msg.correlationIds()[0].value() == _CANCEL_CORRELATION_ID:
                        self.DoLog("Received Subscription Event for unknown correlationId= {}".format(
                            msg.correlationIds()[0].value()), MessageType.DEBUG)
                    else:
                        self.DoLog("Received Subscription Event for unknown correlationId= {}".format(msg.correlationIds()[0].value()),MessageType.DEBUG)

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
            self.DoLog("Error processing Bloomberg event ({} @ProcessEvent) @OrderRouter.Bloomberg module:{}".format(event.eventType(),str(e)), MessageType.ERROR)

    def LoadStrategy(self, request, strategy_name):
        strategy = request.getElement("EMSX_STRATEGY_PARAMS")
        strategy.setElement("EMSX_STRATEGY_NAME", strategy_name)

        indicator = strategy.getElement("EMSX_STRATEGY_FIELD_INDICATORS")
        data = strategy.getElement("EMSX_STRATEGY_FIELDS")

        # Strategy parameters must be appended in the correct order. See the output
        # of GetBrokerStrategyInfo request for the order. The indicator value is 0 for
        # a field that carries a value, and 1 where the field should be ignored


        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # Display Size
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # SOR Pref
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # Session Pref
        indicator.appendElement().setElement("EMSX_FIELD_INDICATOR", 1)

        data.appendElement().setElement("EMSX_FIELD_DATA", "")  # Algo Instr
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
        self.InvokingModule.ProcessOutgoing(execReportWrapper)
        return CMState.BuildSuccess(self)

    def CreateRequest(self, newOrder):
        service = self.Session.getService(self.Configuration.EMSX_Environment)

        request = service.createRequest("CreateOrderAndRouteEx")

        # The fields below are mandatory
        request.set("EMSX_TICKER", "{} {} {}".format(newOrder.Security.Symbol,self.Configuration.Exchange,self.Configuration.SecurityType))
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

        if(self.Configuration.ImplementStrategy ==True):
            if (newOrder.Strategy is not None):
                self.LoadStrategy(request,newOrder.Strategy)

        return request

    def CancellAllOrders(self,wrapper):


        for orderId in self.ActiveOrders:
            if self.ActiveOrders[orderId].IsOpenOrder():
                activeOrder = self.ActiveOrders[orderId]
                service = self.Session.getService(self.Configuration.EMSX_Environment)

                request = service.createRequest("CancelRoute")

                routes = request.getElement("ROUTES")

                route = routes.appendElement()
                route.getElement("EMSX_SEQUENCE").setValue(orderId)
                route.getElement("EMSX_ROUTE_ID").setValue(1)

                requestID = blpapi.CorrelationId(activeOrder.ClOrdId)

                self.PendingCancels[activeOrder.ClOrdId]=activeOrder

                self.Session.sendRequest(request, correlationId=requestID)

    def ProcessNewOrder(self, wrapper):

        if not self.Connected:
            return self.ProcessRejectedExecutionReport(wrapper, "Not Connected to Bloomberg")

        if self.ValidateMaxOrdersPerSecondLimit() == False:
            return self.ProcessRejectedExecutionReport(wrapper, "Max orders per second limit surpassed! Wait 5 minutes after {}".format(self.LastHaltingTime))

        newOrder = OrderConverter.ConvertNewOrder(self, wrapper)

        request = self.CreateRequest(newOrder)

        self.DoLog(
            "Placing Order On Market: ClOrdId {} Symbol {} secType {} orderType {} totalQty {} "
                .format(newOrder.ClOrdId, newOrder.Security.Symbol, newOrder.Security.SecurityType,
                        newOrder.OrdType, newOrder.OrderQty), MessageType.INFO)

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

            executionReportWrappersList = []
            for execReport in self.PreExistingExecutionReports:
                order = self.FetchPreExistingOrder(execReport.Order.OrderId) if execReport.Order is not None else None

                if order is not None:
                    execReportWrapper = GenericExecutionReportWrapper(order,execReport)
                    self.ActiveOrders[order.OrderId] = order
                else:
                    tempOrder = Order()
                    tempOrder.OrderId=execReport.Order.OrderId if execReport.Order is not None else None
                    execReportWrapper = ExecutionReportWrapper(tempOrder, execReport,pParent=self)

                executionReportWrappersList.append(execReportWrapper)

            self.DoLog("Recovered {} previously existing execution reports".format(len(executionReportWrappersList)),MessageType.INFO)
            wrapper = ExecutionReportListWrapper(executionReportWrappersList)
            self.InvokingModule.ProcessOutgoing(wrapper)

        except Exception as e:
            self.DoLog("Critical Error running ProcessExecutionReportListThread @OrderRouter.Bloomberg module:{}".format(str(e)),MessageType.ERROR)
            emptyWrapper = ExecutionReportListWrapper([])
            self.InvokingModule.ProcessOutgoing(emptyWrapper)

    def ProcessExecutionReportList(self,wrapper):
        threading.Thread(target=self.ProcessExecutionReportListThread, args=(wrapper,)).start()
        return CMState.BuildSuccess(self)

    #endregion

    # region Public Methods
    def ProcessOutgoing(self, wrapper):
        pass

    def ProcessMessage(self, wrapper):
        try:

            if wrapper.GetAction() == Actions.NEW_ORDER:
                self.ProcessNewOrder(wrapper)
            elif wrapper.GetAction() == Actions.UPDATE_ORDER:
                raise Exception("Update Order not implemented @Bloomberg order router")
            elif wrapper.GetAction() == Actions.CANCEL_ORDER:
                raise Exception("Cancel Order not implemented @Bloomberg order router")
            elif wrapper.GetAction() == Actions.CANCEL_ALL_POSITIONS:
                self.CancellAllOrders(wrapper)
            elif wrapper.GetAction() == Actions.EXECUTION_REPORT_LIST_REQUEST:
                self.ProcessExecutionReportList(wrapper)
            else:
                self.DoLog(
                    "Routing to market: Order Router not prepared for routing message {}".format(wrapper.GetAction()),
                    MessageType.WARNING)

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Error running ProcessMessage @OrderRouter.Bloomberg module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def Initialize(self, pInvokingModule, pConfigFile):
        self.InvokingModule = pInvokingModule
        self.ModuleConfigFile = pConfigFile

        try:

            self.DoLog("Initializing Bloomberg Order Router", MessageType.INFO)
            if self.LoadConfig():

                self.LoadSession()

                self.DoLog("Bloomberg Order Router Initialized", MessageType.INFO)
                return CMState.BuildSuccess(self)
            else:
                raise Exception("Unknown error initializing config file for Bloomberg Order Router")

        except Exception as e:

            self.DoLog("Error Loading Bloomberg Order Router module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    #endregion