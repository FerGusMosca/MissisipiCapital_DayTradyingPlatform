import tornado.websocket
import json
import asyncio
from sources.strategy.strategies.day_trader.strategy.services.websocket.websocket_module.websocket_module import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.subscriptions.websocket_subscribe_message import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.cancel_position_req import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.cancel_position_ack import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_ack import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.cancel_all_position_ack import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.subscriptions.subscription_reponse import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.batchs.get_open_positions_batch import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.batchs.get_position_execution_summaries_batch import *
from sources.framework.common.wrappers.portfolio_position_list_request_wrapper import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.error_message import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.positions.position_dto import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.positions.execution_summary_dto import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.wrappers.position_req_wrapper import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.wrappers.cancel_all_position_wrapper import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.wrappers.cancel_position_wrapper import *
from sources.framework.common.wrappers.portfolio_position_trade_list_request_wrapper import *

_OPEN_POSITIONS_SERVICE = "OP"
_POSITION_EXECUTIONS_SERVICE="PE"


class WSHandler(tornado.websocket.WebSocketHandler):
  #region Private Methods

  def DoLog(self,msg,type):
    if(self.InvokingModule is not None):
      self.InvokingModule.DoLog(msg,type)

  def DoSend(self,obj):
    asyncio.set_event_loop(asyncio.new_event_loop())
    self.write_message(obj.toJSON())
  #endregion

  #endregion IncomingMethods

  def PublishOpenPositions(self,positions):
    if _OPEN_POSITIONS_SERVICE in self.SubscribedServices:

      posDTOArr = []

      for pos in positions:
        posDTO = PositionDTO(pos)
        posDTOArr.append(posDTO)

      posBatch = GetOpenPositionsBatch("GetOpenPositionsBatch",posDTOArr)
      self.DoSend(posBatch)

  def PublishOpenPosition(self, dayTradingPos):
    if _OPEN_POSITIONS_SERVICE in self.SubscribedServices:
      posDTO = PositionDTO(dayTradingPos)
      self.DoSend(posDTO)


  def PublishExecutionSummaries(self,executionSummaries,dayTradingPosId):
    if _POSITION_EXECUTIONS_SERVICE in self.SubscribedServices:

      executionsDTOArr = []

      for summary in executionSummaries:
        summaryDTO = ExecutionSummaryDTO(summary,dayTradingPosId)
        executionsDTOArr.append(summaryDTO)

      summariesBatch = GetPositionExecutionSummariesBatch("GetPositionExecutionSummariesBatch",executionsDTOArr)
      self.DoSend(summariesBatch)


  def PublishExecutionSummary(self,summary,dayTradingPosId):
    if _POSITION_EXECUTIONS_SERVICE in self.SubscribedServices:
      summaryDTO = ExecutionSummaryDTO(summary,dayTradingPosId)
      self.DoSend(summaryDTO)


  def PublishError(self,error):
    msg = ErrorMessage(error)
    self.DoSend(msg)
  #endregion

  #region Protected Methods

  def SubscribeService(self,service):
    if service not in self.SubscribedServices:
      self.SubscribedServices.append(service)

  def ProcessSubscriptionResponse(self,subscrMsg,success=True,message=None):
    resp = SubscriptionResponse(Msg="SubscriptionResponse",SubscriptionType= subscrMsg.SubscriptionType,
                                Service= subscrMsg.Service,ServiceKey= subscrMsg.ServiceKey,
                                Success= success,Message= message,UUID = subscrMsg.UUID )
    self.DoLog("SubscriptionResponse UUID:{} Service:{} ServiceKey:{} Success:{}"
               .format(subscrMsg.UUID,subscrMsg.Service,subscrMsg.ServiceKey,resp.Success), MessageType.INFO)
    self.DoSend(resp)

  def ProcessPositionsExecutions(self,subscrMsg):
    self.SubscribeService(subscrMsg.Service)

    wrapper = PortfolioPositionTradeListRequestWrapper(subscrMsg.ServiceKey)

    self.InvokingModule.ProcessIncoming(wrapper)

    self.ProcessSubscriptionResponse(subscrMsg)

  def ProcessOpenPositions(self,subscrMsg):
    self.SubscribeService(subscrMsg.Service)

    wrapper = PortfolioPositionListRequestWrapper()

    self.InvokingModule.ProcessIncoming(wrapper)

    self.ProcessSubscriptionResponse(subscrMsg)


  def UnsubscribeService(self,subscrMsg):
    #Unsubscription don't have confirmation messages
    if subscrMsg.Service not in self.SubscribedServices:
      del self.SubscribedServices[subscrMsg.Service]


  def ProcessCancelPositionReq(self,cancelRouteReq):
    try:

      self.DoLog("Incoming Cancel Position Req for positionId {}".format(cancelRouteReq.PosId),MessageType.INFO)
      wrapper =  CancelPositionWrapper(cancelRouteReq.PosId)

      state=self.InvokingModule.ProcessIncoming(wrapper)

      if state.Success:
        ack = CancelPositionAck(Msg="CancelAllPositionAck", UUID=cancelRouteReq.UUID,
                                ReqId=cancelRouteReq.ReqId,PosId=cancelRouteReq.PosId)
        self.DoSend(ack)
        self.DoLog("Cancel positions id {} sent...".format(cancelRouteReq.PosId),MessageType.INFO)
      else:
        raise state.Exception


    except Exception as e:
      msg = "Critical ERROR for Incoming Cancel Position Req for posId {}. Error:{}".format(cancelRouteReq.PosId,str(e))
      self.DoLog(msg, MessageType.ERROR)
      ack = CancelAllPositionAck(Msg="CancelAllPositionAck", UUID=cancelRouteReq.UUID, ReqId=cancelRouteReq.ReqId,
                                 PosId=cancelRouteReq.PosId,Success=False, Error=msg)
      self.DoSend(ack)

  def ProcessCancelAllPositionReq(self,cancelAllRouteReq):
    try:

      self.DoLog("Incoming Cancel All Positions Req ",MessageType.INFO)
      wrapper =  CancelAllPositionsWrapper()

      state=self.InvokingModule.ProcessIncoming(wrapper)

      if state.Success:
        ack = CancelAllPositionAck(Msg="CancelAllPositionAck", UUID=cancelAllRouteReq.UUID, ReqId=cancelAllRouteReq.ReqId)
        self.DoSend(ack)
        self.DoLog("Cancel All positions sent...",MessageType.INFO)
      else:
        raise state.Exception


    except Exception as e:
      msg = "Critical ERROR for Incoming Cancel all Positions Req . Error:{}".format(str(e))
      self.DoLog(msg, MessageType.ERROR)
      ack = CancelAllPositionAck(Msg="CancelAllPositionAck", UUID=cancelAllRouteReq.UUID, ReqId=cancelAllRouteReq.ReqId, Success=False, Error=msg)
      self.DoSend(ack)


  def ProcessRoutePositionReq(self,routePos):

    try:

      self.DoLog("Incoming Route Position Req for symbol {} qty {} side {}".format(routePos.Symbol,routePos.Qty,routePos.Side),MessageType.INFO)

      wrapper = PositionReqWrapper(routePos)

      state = self.InvokingModule.ProcessIncoming(wrapper)

      if state.Success:
        ack = RoutePositionAck(Msg="RoutePositionAck", UUID=routePos.UUID, ReqId=routePos.ReqId)
        self.DoSend(ack)
        self.DoLog("Incoming Route Position Req for symbol {} qty {} side {} successfully processed".format(routePos.Symbol, routePos.Qty, routePos.Side),MessageType.INFO)
      else:
        raise state.Exception


    except Exception as e:
      msg="Critical ERROR for Incoming Route Position Req for symbol {} qty {} side {}. Error:{}".format(routePos.Symbol, routePos.Qty, routePos.Side,str(e))
      self.DoLog(msg, MessageType.ERROR)
      ack = RoutePositionAck(Msg="RoutePositionAck", UUID=routePos.UUID, ReqId=routePos.ReqId,Success=False,Error=msg)
      self.DoSend(ack)

  def ProcessSubscriptions(self,subscrMsg):

    if subscrMsg.SubscriptionType == WebSocketSubscribeMessage._SUBSCRIPTION_TYPE_SUBSCRIBE():
      self.DoLog("Incoming subscription for service {} - ServiceKey:{} ".format(subscrMsg.Service, subscrMsg.ServiceKey),MessageType.INFO)

      if subscrMsg.Service == _OPEN_POSITIONS_SERVICE:
        self.ProcessOpenPositions(subscrMsg)
      elif subscrMsg.Service == _POSITION_EXECUTIONS_SERVICE:
        self.ProcessPositionsExecutions(subscrMsg)
      else:
        self.DoLog("Not processed service {} for subscription".format(subscrMsg.Service),MessageType.ERROR)

    elif subscrMsg.SubscriptionType == WebSocketSubscribeMessage._SUBSCRIPTION_TYPE_UNSUBSCRIBE():
      self.UnsubscribeService(subscrMsg)
    else:
      self.DoLog("Not processed subscription type {} for subscription".format(subscrMsg.SubscriptionType), MessageType.ERROR)


  #endregion

  #region WS Handler Methods

  def initialize(self, pInvokingModule):
    self.InvokingModule = pInvokingModule
    self.SubscribedServices = []

  def open(self):

    #self.write_message("The server says: 'Hello'. Connection was accepted.")

    try:
      self.InvokingModule.CreateConnection(self)
      self.DoLog("Client succesfully connected ", MessageType.INFO)
    except Exception as e:
      self.DoLog("Critical error opening websocket @WSHandler: " + str(e), MessageType.ERROR)
    finally:
      pass

  def on_message(self, message):


    try:
      fieldsDict=json.loads(message)

      if "Msg" in fieldsDict and fieldsDict["Msg"]=="Subscribe":
        subscrMsg = WebSocketSubscribeMessage(**json.loads(message))
        self.ProcessSubscriptions(subscrMsg)
      elif "Msg" in fieldsDict and fieldsDict["Msg"]=="RoutePositionReq":
        routePos = RoutePositionReq(**json.loads(message))
        self.ProcessRoutePositionReq(routePos)
      elif "Msg" in fieldsDict and fieldsDict["Msg"] == "RouteSymbolReq":
        routePos = RoutePositionReq(**json.loads(message))
        self.ProcessRoutePositionReq(routePos)
      elif "Msg" in fieldsDict and fieldsDict["Msg"]=="CancelAllPositionReq":
        cancelAllPos = CancelPositionReq(**json.loads(message))
        self.ProcessCancelAllPositionReq(cancelAllPos)
      elif "Msg" in fieldsDict and fieldsDict["Msg"]=="CancelPositionReq":
        cancelPos = CancelPositionReq(**json.loads(message))
        self.ProcessCancelPositionReq(cancelPos)
      else:
        self.DoLog("Unknown message :{}".format(message),MessageType.ERROR)

    except Exception as e:
      self.DoLog("Critical error @on_message @WSHandler: " + str(e), MessageType.ERROR)

  def on_close(self):
    try:
      self.InvokingModule.RemoveConnection(self)
      self.DoLog("Client succesfully disconnected ", MessageType.INFO)
    except Exception as e:
      self.DoLog("Critical error closing  websocket @WSHandler: " + str(e), MessageType.ERROR)
    finally:
      pass


  #endregion