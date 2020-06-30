import importlib
import time
import threading
from sources.framework.common.abstract.base_communication_module import BaseCommunicationModule
from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.logger.message_type import MessageType
from sources.generic_orderrouter.market_order_router.common.configuration.configuration import *
from sources.framework.common.dto.cm_state import *
from sources.generic_orderrouter.common.converters.position_converter import *
from sources.framework.common.wrappers.cancel_order_wrapper import *
from sources.framework.common.wrappers.order_cancel_reject_wrapper import *
from sources.generic_orderrouter.market_order_router.common.wrappers.new_order_wrapper import *
from sources.generic_orderrouter.market_order_router.common.wrappers.execution_report_list_request_wrapper import *
from sources.generic_orderrouter.common.converters.execution_report_list_converter import *
from sources.framework.common.enums.CxlRejReason import *
from sources.framework.common.enums.CxlRejResponseTo import *
from sources.generic_orderrouter.common.wrappers.position_list_wrapper import *
from sources.generic_orderrouter.market_order_router.common.wrappers.execution_report_wrapper import \
    ExecutionReportWrapper as GenericERWrapper


class MarketOrderRouter(BaseCommunicationModule, ICommunicationModule):

    def __init__(self):
        self.Name = "Market Order Router"
        self.OutgoingModule = None
        self.Positions = {}
        self.PositionsLock = threading.Lock()

    def LoadConfig(self):
        self.Configuration = Configuration(self.ModuleConfigFile)
        return True

    def ProcessError(self,wrapper):
        self.InvokingModule.ProcessOutgoing(wrapper)
        return CMState.BuildSuccess(self)

    def ProcessOrderCancelRejectFromOutgoingModule(self,wrapper):
        self.InvokingModule.ProcessOutgoing(wrapper)
        return CMState.BuildSuccess(self)

    def ProcessExecutionReportList(self, wrapper):
        try:

            positions = ExecutionReportListConverter.GetPositionsFromExecutionReportList(self, wrapper)
            self.PositionsLock.acquire()
            for pos in positions:
                if pos.GetLastOrder() is not None:
                    pos.GetLastOrder().ClOrdId = pos.PosId
                    self.Positions[pos.PosId] = pos
                else:
                    self.DoLog("Could not find order for pre existing position on execution report initial load. PosId = {}".format(pos.PosId), MessageType.ERROR)

            if self.PositionsLock.locked():
                self.PositionsLock.release()

            pos_list_wrapper = PositionListWrapper(positions)
            self.InvokingModule.ProcessOutgoing(pos_list_wrapper)
            return CMState.BuildSuccess(self)
        except Exception as e:
            errWrapper = PositionListWrapper([],e)
            self.InvokingModule.ProcessOutgoing(errWrapper)
            self.DoLog("Error processing execution report list:{}".format(e), MessageType.ERROR)
            return CMState.BuildFailure(e)
        finally:
            if self.PositionsLock.locked():
                self.PositionsLock.release()

    def ProcessExecutionReport(self, wrapper):
        try:
            cl_ord_id = wrapper.GetField(ExecutionReportField.ClOrdID)
            order_id = wrapper.GetField(ExecutionReportField.OrderID)
            self.PositionsLock.acquire()
            pos = next(iter(list(filter(lambda x:x.GetLastOrder() is not None and  x.GetLastOrder().ClOrdId == cl_ord_id, self.Positions.values()))), None)

            if pos is not None:
                processed_exec_report = GenericERWrapper(pos.PosId, wrapper)
                if (self.PositionsLock.locked()):
                    self.PositionsLock.release()
                self.InvokingModule.ProcessOutgoing(processed_exec_report)
            elif next(iter(list(filter(lambda x: x.GetLastOrder() is not None and x.GetLastOrder().OrderId == order_id, self.Positions.values()))), None) is not None:
                pos = next(iter(list(filter(lambda x: x.GetLastOrder() is not None and x.GetLastOrder().OrderId == order_id, self.Positions.values()))), None)
                if (self.PositionsLock.locked()):
                    self.PositionsLock.release()
                processed_exec_report = GenericERWrapper(pos.PosId, wrapper)
                self.InvokingModule.ProcessOutgoing(processed_exec_report)
            else:
                #Execution report for unknown position. We create it and it will be the strategy that will decide what to do
                newPos = ExecutionReportListConverter.CreatePositionFromExecutionReport(self,wrapper)
                self.Positions[newPos.PosId]=newPos
                if (self.PositionsLock.locked()):
                    self.PositionsLock.release()
                newExecReport = GenericERWrapper(newPos.PosId, wrapper)
                self.InvokingModule.ProcessOutgoing(newExecReport)
                self.DoLog( "Received ExecutionReport for unknown ClOrdId ={} OrderId= {}. Sending as External trading".format(cl_ord_id, order_id),MessageType.INFO)
        except Exception as e:
            self.DoLog("Error processing execution report:{}".format(e), MessageType.ERROR)
        finally:
            if(self.PositionsLock.locked()):
                self.PositionsLock.release()

    def ProcessOrderCancelReject(self,wrapper,ex):
        try:

            posId = wrapper.GetField(PositionField.PosId)
            msg = "Error sending order cancel request: {} ".format(str(ex))

            if posId in self.Positions:
                posToCancel = self.Positions[posId]
                rejWrapper = OrderCancelRejectWrapper(pText=msg, pCxlRejResponseTo=CxlRejResponseTo.OrderCancelRequest,
                                                      pCxlRejReason=CxlRejReason.Other,
                                                      pOrder = None,pClOrdId=posToCancel.GetLastOrder().ClOrdId,
                                                      pOrigClOrdId=None, pOrderId=posToCancel.GetLastOrder().OrderId)

                self.InvokingModule.ProcessOutgoing(rejWrapper)
            else:
                rejWrapper = OrderCancelRejectWrapper(pText=msg, pCxlRejResponseTo=CxlRejResponseTo.OrderCancelRequest,
                                                      pCxlRejReason=CxlRejReason.Other,
                                                      pOrder=None, pClOrdId=None, pOrigClOrdId=None, pOrderId=None)
                self.InvokingModule.ProcessOutgoing(rejWrapper)
        except Exception as e:
            self.DoLog("Critical Error processing order cancel reject: {}".format(str(e)))

    def ProcessPositionCancelThread(self, wrapper):
        try:
            posId = wrapper.GetField(PositionField.PosId)

            if posId in self.Positions:
                posToCancel = self.Positions[posId]
                if(posToCancel.GetLastOrder() is not None):
                    cxlWrapper= CancelOrderWrapper(posToCancel.GetLastOrder().ClOrdId,posToCancel.GetLastOrder().OrderId)
                    self.OutgoingModule.ProcessMessage(cxlWrapper)
                else:
                    raise Exception("Received cancellation for position {} which doesn't have an order to cancel".format(posId))

            else:
                raise Exception("Received cancellation request for unknown position {}".format(posId))

        except Exception as e:
            self.ProcessOrderCancelReject(wrapper,e)

    def ProcessPositionCancel(self,wrapper):
        threading.Thread(target=self.ProcessPositionCancelThread, args=(wrapper,)).start()
        return CMState.BuildSuccess(self)

    def ProcessPositionListRequest(self, wrapper):
        exec_report_list_req_wrapper = ExecutionReportListRequestWrapper()
        return self.OutgoingModule.ProcessMessage(exec_report_list_req_wrapper)

    def ProcessNewPosition(self, wrapper):
        try:

            self.PositionsLock.acquire()
            new_pos = PositionConverter.ConvertPosition(self, wrapper)
            # In this Generic Order Router ClOrdID=PosId
            self.Positions[new_pos.PosId] = new_pos
            order_wrapper = NewOrderWrapper(new_pos.Security.Symbol, new_pos.OrderQty, new_pos.PosId,
                                            new_pos.Security.Currency,new_pos.Security.SecurityType,new_pos.Security.Exchange,
                                            new_pos.Side, new_pos.Account, new_pos.Broker,
                                            new_pos.Strategy, new_pos.OrderType, new_pos.OrderPrice)
            new_pos.Orders.append(Order(ClOrdId=new_pos.PosId,Security=new_pos.Security,SettlType=SettlType.Regular,
                                        Side=new_pos.Side,Exchange=new_pos.Exchange,OrdType=OrdType.Market,
                                        QuantityType=new_pos.QuantityType,OrderQty=new_pos.Qty,PriceType=new_pos.PriceType,
                                        Price=None,StopPx=None,Currency=new_pos.Security.Currency,
                                        TimeInForce=TimeInForce.Day,Account=new_pos.Account,
                                        OrdStatus=OrdStatus.PendingNew,Broker=new_pos.Broker,Strategy=new_pos.Strategy))
            if self.PositionsLock.locked():
                self.PositionsLock.release()
            return self.OutgoingModule.ProcessMessage(order_wrapper)
        except Exception as e:
            raise e
        finally:
            if self.PositionsLock.locked():
                self.PositionsLock.release()

    def ProcessCandleBar(self,wrapper):
        self.InvokingModule.ProcessIncoming(wrapper)

    def ProcessMarketData(self, wrapper):
        self.InvokingModule.ProcessIncoming(wrapper)

    def ProcessHistoricalPrices(self,wrapper):
        self.InvokingModule.ProcessIncoming(wrapper)

    def ProcessIncoming(self, wrapper):
        try:

            if wrapper.GetAction() == Actions.CANDLE_BAR_DATA:
                self.ProcessCandleBar(wrapper)
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.MARKET_DATA:
                self.ProcessMarketData(wrapper)
                return CMState.BuildSuccess(self)
            elif wrapper.GetAction() == Actions.HISTORICAL_PRICES:
                self.ProcessHistoricalPrices(wrapper)
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
                return self.ProcessOrderCancelRejectFromOutgoingModule(wrapper)
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
                return self.ProcessNewPosition(wrapper)
            elif wrapper.GetAction() == Actions.POSITION_LIST_REQUEST:
                return self.ProcessPositionListRequest(wrapper)
            elif wrapper.GetAction() == Actions.CANCEL_POSITION:
                return self.ProcessPositionCancel(wrapper)
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

