import time
import uuid

import websocket

from sources.framework.business_entities.market_data.candle_bar import CandleBar
from sources.framework.common.enums.fields.market_data_request_field import MarketDataRequestField
from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.abstract.base_communication_module import *
from sources.framework.common.logger.message_type import *
from sources.framework.common.enums.Actions import *
from sources.framework.common.dto.cm_state import *
from sources.framework.common.enums.fields.summary_field import *
from sources.framework.common.enums.fields.summary_list_fields import *
from sources.framework.common.enums.fields.error_field import *
from sources.framework.common.wrappers.error_wrapper import ErrorWrapper
from sources.framework.util.singleton.common.util.singleton import *
from sources.order_routers.bloomberg.common.converter.market_data_request_converter import MarketDataRequestConverter
from sources.order_routers.bloomberg.common.wrappers.filled_execution_report_wrapper import FilledExecutionReportWrapper
from sources.order_routers.bloomberg.common.wrappers.new_execution_report_wrapper import NewExecutionReportWrapper
from sources.order_routers.websocket.common.DTO.market_data.candlebar_dto import CandlebarDTO
from sources.order_routers.websocket.common.DTO.market_data.market_data_request_dto import MarketDataRequestDTO
from sources.order_routers.websocket.common.DTO.order_routing.cancel_order_req import CancelOrderReq
from sources.order_routers.websocket.common.DTO.order_routing.order_mass_status_request import \
    OrderMassStatusRequest
from sources.order_routers.websocket.common.DTO.order_routing.update_order_req import UpdateOrderReq
from sources.order_routers.websocket.common.configuration.configuration import *
from sources.order_routers.websocket.common.wrappers.candlebar_wrapper import CandlebarWrapper
from sources.order_routers.websocket.data_access_layer.websocket_client import WebsocketClient
from sources.order_routers.websocket.data_access_layer.websocket_server import *
from sources.framework.common.enums.TimeUnit import TimeUnit
from sources.order_routers.websocket.common.converters.order_converter import *
import tornado
import threading
import asyncio
from websocket import create_connection

@Singleton
class WebSocketModule(BaseCommunicationModule, ICommunicationModule):
    def __init__(self):
        self.LockConnections = threading.Lock()
        self.TradingLock = threading.Lock()
        self.CandleBarSubscriptionLock=threading.Lock()
        self.Configuration = None
        self.WebsocketServer = None
        self.Connections = []
        self.OnMarketData = None
        self.OnExecutionReport = None
        self.Initialized=False
        self.WsClient=None
        self.ActiveOrders = {}
        self.CandleBarSubscriptions={}
        self.MarketDataSubscriptions = {}


    #region Private Methods

    #region Process Message Methods

    def DoSendOrder(self, newOrder):

        try:
            self.TradingLock.acquire(blocking=True)

            self.DoLog("<order_router> Sending new Order with ClOrdId {}".format(newOrder.ClOrdId), MessageType.INFO)

            orderReqDto = RouteOrderReq(Msg="NewOrderReq", Side=newOrder.Side, ReqId=newOrder.ClOrdId,
                                        Qty=newOrder.OrderQty, Type=None, Account=newOrder.Account,
                                        Symbol=newOrder.Security.Symbol,
                                        ClOrdId=newOrder.ClOrdId, Price=newOrder.Price)

            if self.TradingLock.locked():
                self.TradingLock.release()

            self.ActiveOrders[str(newOrder.ClOrdId)] = newOrder

            for conn in self.Connections:
                conn.DoSendAsync(orderReqDto)

        finally:
            if self.TradingLock.locked():
                self.TradingLock.release()

    def DoUpdateOrder(self, updOrderReq):

        try:

            self.TradingLock.acquire(blocking=True)

            self.DoLog("<order_router> Updating order with new Price {} ({} -> {})".format(updOrderReq.Price,
                                                                                           updOrderReq.OrigClOrdId,
                                                                                           updOrderReq.ClOrdId),
                                                                                            MessageType.INFO)

            if updOrderReq.OrigClOrdId in self.ActiveOrders:

                oldOrder = self.ActiveOrders[updOrderReq.OrigClOrdId]
                newOrder = oldOrder.Clone()

                newOrder.Price = updOrderReq.Price
                newOrder.OrigClOrdId = updOrderReq.OrigClOrdId
                newOrder.ClOrdId = updOrderReq.ClOrdId

                self.ActiveOrders[updOrderReq.ClOrdId] = newOrder

                if self.TradingLock.locked():
                    self.TradingLock.release()

                for conn in self.Connections:
                    conn.DoSendAsync(updOrderReq)

            else:
                raise Exception(
                    "Critical error! Could not find order to update for OrigClOrdId {}".format(updOrderReq.OrigClOrdId))

        finally:
            if self.TradingLock.locked():
                self.TradingLock.release()

    def ProcessMarketDataDto(self, marketDataDto):
        try:

            self.TradingLock.acquire(blocking=True)
            self.DoLog("<order_router> Incoming Market Data for Symbol {}".format(marketDataDto.Symbol),MessageType.INFO)
            wrapper = MarketDataWrapper(marketDataDto)

            if self.TradingLock.locked():
                self.TradingLock.release()

            state = self.ProcessIncoming(wrapper)

            if state.Success:
                self.DoLog("Market Data Processed for symbol {}...".format(marketDataDto.Symbol),MessageType.INFO)
            else:
                raise state.Exception

        except Exception as e:
            msg = "Critical ERROR for market data for symbol {}. Error:{}".format(marketDataDto.Symbol, str(e))
            self.DoLog(msg, MessageType.ERROR)
        finally:
            if self.TradingLock.locked():
                self.TradingLock.release()

    def ProcessCandlebartDto(self,cbDto):
        try:

            self.DoLog("<order_router>-Incoming Candlebar for Symbol={} Date={} Open={} High={} Low={} Close={} Trade={} Volume={}".format(cbDto.Symbol,cbDto.Date,cbDto.Open,cbDto.High,cbDto.Low,cbDto.Close,cbDto.Trade,cbDto.Volume),MessageType.INFO)

            self.TradingLock.acquire(blocking=True)

            cbWrapper = CandlebarWrapper(self, cbDto)

            if self.TradingLock.locked():
                self.TradingLock.release()

            state = self.ProcessIncoming(cbWrapper)

            if state.Success:
                pass
            else:
                raise state.Exception

        except Exception as e:
            msg = "Critical ERROR for candlebar for Symbol {}. Error:{}".format(cbDto.Symbol, str(e))
            self.DoLog(msg, MessageType.ERROR)
        finally:
            # self.DoLog("DB-websocket.ProcessExecutionReport.exit {}".format(self.full_now()),MessageType.INFO)
            if self.TradingLock.locked():
                self.TradingLock.release()

    def ProcessExecutionReportDto(self, execReportDto):
        try:
            #self.DoLog("DB-websocket.ProcessExecutionReport {}".format(self.full_now()),MessageType.INFO)
            self.DoLog("<order_router>-Incoming Execution Report for ClOrdId {} OrigClOrdId={} Status={}"
                       .format(execReportDto.ClOrdId,execReportDto.OrigClOrdId, execReportDto.Status),
                       MessageType.INFO)

            self.TradingLock.acquire(blocking=True)

            wrapper = None
            if execReportDto.ClOrdId in self.ActiveOrders:
                activeOrder = self.ActiveOrders[execReportDto.ClOrdId]
                activeOrder.OrderId = execReportDto.OrderId

                wrapper = ExecutionReportWrapper(execReportDto, activeOrder)

                if self.TradingLock.locked():
                    self.TradingLock.release()

                state = self.ProcessOutgoing(wrapper)

                if state.Success:
                    pass
                    self.DoLog("<order_router> Execution Report for OrderId {}...".format(execReportDto.ClOrdId),MessageType.INFO)
                else:
                    raise state.Exception
            else:
                tempOrder = Order(ClOrdId=execReportDto.ClOrdId,
                                  OrigClOrdId=execReportDto.OrigClOrdId,
                                  Security=Security(Symbol=""))
                wrapper = ExecutionReportWrapper(execReportDto, tempOrder)
                self.ProcessOutgoing(wrapper)

        except Exception as e:
            msg = "Critical ERROR for Execution Report for OrderId {}. Error:{}".format(execReportDto.ClOrdId, str(e))
            self.DoLog(msg, MessageType.ERROR)
        finally:
            #self.DoLog("DB-websocket.ProcessExecutionReport.exit {}".format(self.full_now()),MessageType.INFO)
            if self.TradingLock.locked():
                self.TradingLock.release()

    def ProcessWebsocketMessage(self, message):

        try:

            fieldsDict = json.loads(message)

            if "Msg" in fieldsDict and fieldsDict["Msg"] == "MarketDataMsg":
                marketDataDto = MarketDataDTO(**json.loads(message))
                self.ProcessMarketDataDto(marketDataDto)
            elif "Msg" in fieldsDict and fieldsDict["Msg"] == "ExecutionReportMsg":
                execReport = ExecutionReportDto(**json.loads(message))
                self.ProcessExecutionReportDto(execReport)
            elif "Msg" in fieldsDict and fieldsDict["Msg"] == "CandlebarMsg":
                cb = CandlebarDTO(**json.loads(message))
                self.ProcessCandlebartDto(cb)

            elif "Msg" in fieldsDict and fieldsDict["Msg"] == "UpdOrderAck":
                pass
            elif "Msg" in fieldsDict and fieldsDict["Msg"] == "NewOrderAck":
                pass
            elif "Msg" in fieldsDict and fieldsDict["Msg"] == "OrderMassStatusRequestAck":
                pass
            else:
                self.DoLog("Unknown message :{}".format(message), MessageType.ERROR)

        except Exception as e:
            msg = "<order_router> Critical error @ProcessWebsocketMessage: " + str(e)
            self.DoLog(msg, MessageType.ERROR)
            # self.PublishError(msg)

        finally:
            if self.TradingLock.locked():
                self.TradingLock.release()


    #endregion


    def DoLog(self,msg, type):
        self.InvokingModule.DoLog(msg,type)

    def LoadConfig(self):
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True

    def CreateConnection(self,handler):
        try:
            self.LockConnections.acquire()
            self.Connections.append(handler)
        finally:
            self.LockConnections.release()

    def RemoveConnection(self,handler):
        try:
            self.LockConnections.acquire()
            self.Connections.remove(handler)
        finally:
            self.LockConnections.release()

    def OpenWebsocketServer(self):
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            self.WebsocketServer = tornado.web.Application([(r"/", WSHandler,{'pInvokingModule': self}),])
            self.WebsocketServer.listen(self.Configuration.ServerWebsocketPort)
            self.DoLog("Websocket commands successfully opened on port {}: ".format(self.Configuration.ServerWebsocketPort), MessageType.INFO)
            tornado.ioloop.IOLoop.instance().start()
        except Exception as e:
            self.DoLog("Critical error opening websocket @OpenWebsocketServer: " + str(e), MessageType.ERROR)


    def OpenWebsocketClient(self):

        ws=None
        try:
            self.DoLog("Opening websocket connection with server {}".format(self.Configuration.ClientUrl),MessageType.INFO)

            ws=WebsocketClient(self.Configuration.ClientUrl)
            self.Connections.append(ws)

            if not ws.IsConnected():
                raise Exception("Could not connect to url {}".format(self.Configuration.ClientUrl))

            while True:
                result = ws.DoReceive()
                threading.Thread(target=self.ProcessWebsocketMessage, args=(result,)).start()


        except Exception as e:
                self.DoLog("Critical error opening websocket @OpenWebsocketClient for {}: ".format(self.Configuration.ClientUrl) + str(e), MessageType.ERROR)
        finally:
            if ws is not None:
                ws.DoClose()
    #endregion

    #region Event Methods

    def ProcessError(self,wrapper):
        try:
            errMessage = wrapper.GetField(ErrorField.ErrorMessage)
            self.LockConnections.acquire()
            for conn in self.Connections:
                conn.PublishError(errMessage)

            return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessError:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)
        finally:
            if self.LockConnections.locked():
                self.LockConnections.release()

    def ProcessCandlebar(self,wrapper):
        try:
            self.OnMarketData.ProcessIncoming(wrapper)
            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessCandlebar:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def ProcessMarketData(self,wrapper):
        try:
            self.OnMarketData.ProcessIncoming(wrapper)
            self.OnExecutionReport.ProcessOutgoing(wrapper)#we need to send MD to the order router too
            #self.InvokingModule.ProcessIncoming(wrapper)

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessMarketData:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessExecutionReport(self,wrapper):
        try:
            self.OnExecutionReport.ProcessOutgoing(wrapper)
            #self.InvokingModule.ProcessOutgoing(wrapper)

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessExecutionReport:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def WaitForConnections(self):

        sleepCounts = self.Configuration.WaitForConnectionsPacingSec / 2
        i = 0
        while len(self.Connections) == 0:
            i += 1

            time.sleep(2)

            if i > sleepCounts:
                self.DoLog("ERROR - Discarding Market Data Request because no connection could be detected!",
                           MessageType.ERROR)
                break

    def OrderMassStatusRequestThread(self,wrapper):
        try:
            self.WaitForConnections()

            reqDto = OrderMassStatusRequest()

            for conn in self.Connections:
                conn.DoSendAsync(reqDto)

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.OrderMassStatusRequestThread:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def ProcessCandleBarRequestThread(self,wrapper):
        cbReq = MarketDataRequestConverter.ConvertCandleBarRequest(wrapper)
        try:

            if cbReq.TimeUnit != TimeUnit.Minute:
                raise Exception("Not valid time unit for candle bar request {}".format(cbReq.TimeUnit))

            self.CandleBarSubscriptionLock.acquire()
            if cbReq.SubscriptionRequestType == SubscriptionRequestType.Unsuscribe:

                raise Exception("Websocket ")
            else:
                self.DoLog("Bloomberg Order Router: Received Candle Bars Subscription Request for symbol:{}".format(
                    cbReq.Security.Symbol), MessageType.INFO)

                self.CandleBarSubscriptions[cbReq.Security.Symbol] = CandleBar(cbReq.Security)

                self.WaitForConnections()

                reqDto = WebSocketSubscribeMessage(Msg="Subscribe",
                                                   SubscriptionType=WebSocketSubscribeMessage._SUBSCRIPTION_TYPE_SUBSCRIBE(),
                                                   Service="CB",
                                                   ServiceKey=cbReq.Security.Symbol,
                                                   ReqId=str(uuid.uuid4()))

                for conn in self.Connections:
                    conn.DoSendAsync(reqDto)

                return CMState.BuildSuccess(self)


        except Exception as e:
            msg = "Critical error subscribing for candlebars for symbol {}:{}".format(cbReq.Security.Symbol, str(e))
            self.DoLog(msg, MessageType.ERROR)
            errorWrapper = ErrorWrapper(e)
            self.OnMarketData.ProcessIncoming(errorWrapper)

        finally:
            if self.CandleBarSubscriptionLock.locked():
                self.CandleBarSubscriptionLock.release()

    def ProcessMarketDataRequestThread(self,wrapper):

        try:
            self.WaitForConnections()

            reqDto=WebSocketSubscribeMessage(Msg="Subscribe",
                                             SubscriptionType=WebSocketSubscribeMessage._SUBSCRIPTION_TYPE_SUBSCRIBE(),
                                             Service="MD",
                                             ServiceKey=wrapper.GetField(MarketDataRequestField.Symbol),
                                             ReqId=wrapper.GetField(MarketDataRequestField.MDReqId))

            # reqDto=MarketDataRequestDTO(Symbol=wrapper.GetField(MarketDataRequestField.Symbol),
            #                             pSecurityType=wrapper.GetField(MarketDataRequestField.SecurityType),
            #                             Currency=wrapper.GetField(MarketDataRequestField.Currency),
            #                             SubscriptionRequestType=wrapper.GetField(MarketDataRequestField.SubscriptionRequestType),
            #                             MDReqId=wrapper.GetField(MarketDataRequestField.MDReqId))

            for conn in self.Connections:
                conn.DoSendAsync(reqDto)

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessMarketDataRequestThread:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessOrderMassStatusRequest(self,wrapper):
        try:
            threading.Thread(target=self.OrderMassStatusRequestThread, args=(wrapper,)).start()

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.OrderMassStatusRequest:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessMarketDataRequest(self,wrapper):
        try:
            threading.Thread(target=self.ProcessMarketDataRequestThread, args=(wrapper,)).start()

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessMarketDataRequest:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def ProcessCandleBarRequest(self,wrapper):
        try:
            threading.Thread(target=self.ProcessCandleBarRequestThread, args=(wrapper,)).start()

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessCandleBarRequest:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessCancelOrder(self,wrapper):
        try:

            clOrdId = wrapper.GetField(OrderField.ClOrdID)
            orderId = wrapper.GetField(OrderField.OrderId)

            cxlOrderReq = CancelOrderReq( OrigClOrderId=clOrdId, ClOrderId=clOrdId,OrderId=orderId)

            for conn in self.Connections:
                conn.DoSendAsync(cxlOrderReq)

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessCancelOrder:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessUpdateOrder(self,wrapper):
        try:

            symbol = wrapper.GetField(OrderField.Symbol)
            origClOrdId =  wrapper.GetField(OrderField.OrigClOrdID)
            clOrdId =  wrapper.GetField(OrderField.ClOrdID)
            price = float( wrapper.GetField(OrderField.Price))
            ordType = wrapper.GetField(OrderField.OrdType)
            side = wrapper.GetField(OrderField.Side)
            tif = wrapper.GetField(OrderField.TimeInForce)
            ordQty = int( wrapper.GetField(OrderField.OrderQty))


            updOrderReq = UpdateOrderReq(Msg="UpdOrderReq",OrigClOrdId= origClOrdId,ClOrdId= clOrdId,pPrice=price,
                                         pSymbol=symbol,pOrdType=ordType,pSide=side,pTimeInforce=tif,pOrdQty=ordQty)

            self.DoUpdateOrder(updOrderReq)

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("Exception @WebsocketModule.ProcessUpdateOrder:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessNewOrder(self,wrapper):
        try:

            newOrder = OrderConverter.ConvertNewOrder(self,wrapper)

            self.DoSendOrder(newOrder)

            return CMState.BuildSuccess(self)
        except Exception as e:
            self.DoLog("ERROR-Exception @WebsocketModule.ProcessNewOrder:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def DoSendExecutionReportThread(self,execReport):

        try:
            self.OnExecutionReport.ProcessOutgoing(execReport)
        except Exception as e:
            self.DoLog("Error sending execution report:{}".format(str(e)), MessageType.ERROR)

    def SendMockFilledExecutionReportsThread(self,newOrder):
        try:

            newOrder.OrderId = int(time.time())
            newOrder.MarketArrivalTime = datetime.datetime.now()
            self.ActiveOrders[newOrder.OrderId] = newOrder

            newWrapper = NewExecutionReportWrapper(newOrder)
            self.DoSendExecutionReportThread(newWrapper)
            time.sleep(self.Configuration.SecondsToSleepOnTradeForMock)


            mdDto=None
            if newOrder.Security.Symbol in  self.MarketDataSubscriptions:
               mdDto = self.MarketDataSubscriptions[newOrder.Security.Symbol]

            executionPrice = newOrder.Price if newOrder.Price is not None else \
                            (mdDto.BestAskPx if newOrder.Side==Side.Buy or Side.BuyToClose else mdDto.BestBidPx)

            filledWrapper = FilledExecutionReportWrapper(newOrder,executionPrice)
            self.DoSendExecutionReportThread(filledWrapper)
        except Exception as e:
            msg = "Critical error @SendMockFilledExecutionReportsThread:{}".format(str(e))
            self.DoLog(msg, MessageType.ERROR)
            errorWrapper = ErrorWrapper(e)
            self.OnMarketData.ProcessIncoming(errorWrapper)

    def ProcessNewOrderMock(self,wrapper):

        newOrder = OrderConverter.ConvertNewOrder(self, wrapper)

        threading.Thread(target=self.SendMockFilledExecutionReportsThread, args=(newOrder,)).start()

    #endregion

    #region ICommunicationModule methods

    def SetOutgoingModule(self,outgoingModule):
        self.OnExecutionReport = outgoingModule

    def SetIncomingModule(self,incomingModule):
        self.OnMarketData = incomingModule

    def ProcessMessage(self, wrapper):
        try:
            if wrapper.GetAction() == Actions.NEW_ORDER:
                if (self.Configuration.ImplementMock):
                    self.ProcessNewOrderMock(wrapper)
                else:
                    return self.ProcessNewOrder(wrapper)
            elif wrapper.GetAction() == Actions.UPDATE_ORDER:
                return self.ProcessUpdateOrder(wrapper)
            elif wrapper.GetAction() == Actions.CANCEL_ORDER:
                return self.ProcessCancelOrder(wrapper)
            elif wrapper.GetAction() == Actions.MARKET_DATA_REQUEST:
                return self.ProcessMarketDataRequest(wrapper)
            elif wrapper.GetAction() == Actions.CANDLE_BAR_REQUEST:
                self.ProcessCandleBarRequest(wrapper)
            elif wrapper.GetAction() == Actions.ORDER_MASS_STATUS_REQUEST:
                return self.ProcessOrderMassStatusRequest(wrapper)
            else:
                raise Exception("ProcessMessage: Not prepared to process message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @WebsocketModule.ProcessMessage: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def ProcessOutgoing(self, wrapper):
        try:
            if wrapper.GetAction() == Actions.EXECUTION_REPORT:
                return self.ProcessExecutionReport(wrapper)
            else:
                raise Exception("ProcessOutgoing: Not prepared to process message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @WebsocketModule.ProcessOutgoing: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def ProcessIncoming(self, wrapper):
        try:
            if wrapper.GetAction() == Actions.MARKET_DATA:
                return self.ProcessMarketData(wrapper)
            elif wrapper.GetAction() == Actions.CANDLE_BAR_DATA:
                return self.ProcessCandlebar(wrapper)
            else:
                raise Exception("ProcessIncoming: Not prepared to process message {}".format(wrapper.GetAction()))
        except Exception as e:
            self.DoLog("Critical error @WebsocketModule.ProcessIncoming: " + str(e), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    def Initialize(self, pInvokingModule, pConfigFile):

        if not self.Initialized:
            self.ModuleConfigFile = pConfigFile
            self.InvokingModule = pInvokingModule
            self.DoLog("WebSocketModule  Initializing", MessageType.INFO)

            if self.LoadConfig():

                if self.Configuration.Mode=="SERVER":
                    threading.Thread(target=self.OpenWebsocketServer, args=()).start()
                elif self.Configuration.Mode=="CLIENT":
                    threading.Thread(target=self.OpenWebsocketClient, args=()).start()
                else:
                    raise Exception("Invalid websocket mode:{}".format(self.Configuration.Mode))

                self.DoLog("DayTrader Successfully initialized", MessageType.INFO)
                self.CandleBarSubscriptions={}
                self.Initialized=True
                return CMState.BuildSuccess(self)

            else:
                msg = "Error initializing config file for WebSocketModule"
                self.DoLog(msg, MessageType.ERROR)
                return CMState.BuildFailure(self,errorMsg=msg)
        else:
            return CMState.BuildSuccess(self)

    # endregion

