import tornado.websocket
import json
import time
import asyncio
import threading
from sources.strategy.strategies.day_trader.strategy.services.websocket.websocket_module.websocket_module import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.subscriptions.websocket_subscribe_message import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.cancel_position_req import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.market_data.historical_prices_req import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.market_data.historical_prices_ack import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.cancel_position_ack import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.config.update_model_param_req import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.config.update_model_param_ack import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_ack import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.cancel_all_position_ack import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.subscriptions.subscription_reponse import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.batchs.get_open_positions_batch import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.batchs.get_historical_prices_batch import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.batchs.get_position_execution_summaries_batch import *
from sources.framework.common.wrappers.portfolio_position_list_request_wrapper import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.error_message import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.positions.position_dto import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.market_data.historical_price_dto import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.positions.execution_summary_dto import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.wrappers.position_req_wrapper import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.wrappers.cancel_all_position_wrapper import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.wrappers.update_model_parameter_req_wrapper import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.wrappers.cancel_position_wrapper import *
from sources.framework.common.wrappers.portfolio_position_trade_list_request_wrapper import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.wrappers.historical_prices_req_wrapper import *


_OPEN_POSITIONS_SERVICE = "OP"
_POSITION_EXECUTIONS_SERVICE="PE"


class WSHandler(tornado.websocket.WebSocketHandler):
  #region Private Methods

  def DoLog(self,msg,type):
    if(self.InvokingModule is not None):
      self.InvokingModule.DoLog(msg,type)

  async def WriteMessage(self,obj):
    self.write_message(obj.toJSON())

  def DoSendAsync(self,obj):
    routine = self.WriteMessage(obj)
    asyncio.run(routine)

  def DoSendResponse(self,obj):
    self.write_message(obj.toJSON())

  #endregion

  #endregion IncomingMethods

  def PublishOpenPositions(self,positions):
    if self.IsSubscribed(_OPEN_POSITIONS_SERVICE,None):
      posDTOArr = []

      for pos in positions:
        posDTO = PositionDTO(pos)
        posDTOArr.append(posDTO)

      posBatch = GetOpenPositionsBatch("GetOpenPositionsBatch",posDTOArr)
      self.DoSendAsync(posBatch)

  def PublishOpenPosition(self, dayTradingPos):
    if self.IsSubscribed(_OPEN_POSITIONS_SERVICE, None):
      posDTO = PositionDTO(dayTradingPos)
      self.DoSendAsync(posDTO)


  def PublishExecutionSummaries(self,executionSummaries,dayTradingPosId):
    if self.IsSubscribed(_POSITION_EXECUTIONS_SERVICE, dayTradingPosId):
      executionsDTOArr = []

      for summary in executionSummaries:
        summaryDTO = ExecutionSummaryDTO(summary,dayTradingPosId)
        executionsDTOArr.append(summaryDTO)

      summariesBatch = GetPositionExecutionSummariesBatch("GetPositionExecutionSummariesBatch",executionsDTOArr)
      self.DoSendAsync(summariesBatch)


  def PublishHistoricalPrices(self,symbol,marketDataArr):
    try:

      HistPriceDTOArr = []

      for md in marketDataArr:
        histPriceDTO = HistoricalPriceDTO(md)
        HistPriceDTOArr.append(histPriceDTO)

      histBatch = GetHistoricalPricesBatch("GetHistoricalPricesBatch",symbol, HistPriceDTOArr)
      self.DoSendAsync(histBatch)

    except Exception as e:
      self.DoLog("Exception @WebsocketRaise.PublishHistoricalPrices:{}".format(str(e)), MessageType.ERROR)
      raise e

  def PublishExecutionSummary(self,summary,dayTradingPosId):
    if self.IsSubscribed(_POSITION_EXECUTIONS_SERVICE, dayTradingPosId):
      try:
        if summary.Position.GetLastOrder() is not None:
          summaryDTO = ExecutionSummaryDTO(summary,dayTradingPosId)
          self.DoSendAsync(summaryDTO)
      except Exception as e:
        self.DoLog("Exception @WebsocketRaise.ProcessExecutionSummary:{}".format(str(e)), MessageType.ERROR)
        raise e


  def PublishError(self,error):
    msg = ErrorMessage(error)
    self.DoSendAsync(msg)
  #endregion

  #region Protected Methods

  def IsSubscribed(self,service, serviceKey):
    if service in self.SubscribedServices:
      subscrMesage = self.SubscribedServices[service]
      return str(subscrMesage.ServiceKey)==str(serviceKey) or serviceKey is None
    else:
      return False

  def SubscribeService(self,subscrMsg):
    self.SubscribedServices[subscrMsg.Service]=subscrMsg

  def ProcessSubscriptionResponse(self,subscrMsg,success=True,message=None):
    resp = SubscriptionResponse(Msg="SubscriptionResponse",SubscriptionType= subscrMsg.SubscriptionType,
                                Service= subscrMsg.Service,ServiceKey= subscrMsg.ServiceKey,
                                Success= success,Message= message,UUID = subscrMsg.UUID )
    self.DoLog("SubscriptionResponse UUID:{} Service:{} ServiceKey:{} Success:{}"
               .format(subscrMsg.UUID,subscrMsg.Service,subscrMsg.ServiceKey,resp.Success), MessageType.INFO)
    self.DoSendResponse(resp)

  def ProcessPositionsExecutions(self,subscrMsg):
    self.SubscribeService(subscrMsg)

    wrapper = PortfolioPositionTradeListRequestWrapper(subscrMsg.ServiceKey)

    state=self.InvokingModule.ProcessIncoming(wrapper)

    self.ProcessSubscriptionResponse(subscrMsg, state.Success,str(state.Exception) if state.Exception is not None else None)

  def ProcessOpenPositions(self,subscrMsg):
    self.SubscribeService(subscrMsg)

    wrapper = PortfolioPositionListRequestWrapper()

    state = self.InvokingModule.ProcessIncoming(wrapper)

    self.ProcessSubscriptionResponse(subscrMsg, state.Success,str(state.Exception) if state.Exception is not None else None)


  def UnsubscribeService(self,subscrMsg):
    #Unsubscription don't have confirmation messages
    if subscrMsg.Service not in self.SubscribedServices:
      del self.SubscribedServices[subscrMsg.Service]


  def ProcessHistoricalPricesReq(self,histPricesReq):
    try:

      self.DoLog("Incoming Historical Prices Req from {} to {} for symbol {} ".format(histPricesReq.From,histPricesReq.To,histPricesReq.Symbol ), MessageType.INFO)
      wrapper = HistoricalPricesReqWrapper(histPricesReq.Symbol, histPricesReq.From,histPricesReq.To)

      state = self.InvokingModule.ProcessIncoming(wrapper)

      if state.Success:
        ack = HistoricalPricesAck(Msg="HistoricalPricesAck", UUID=histPricesReq.UUID,ReqId=histPricesReq.ReqId)
        self.DoSendResponse(ack)
        self.DoLog("Historical prices request sent for symbol {}...".format(histPricesReq.Symbol), MessageType.INFO)
      else:
        raise state.Exception
    except Exception as e:
      msg = "Critical ERROR for Historical Prices Req for Symbol {} From {} To {}. Error:{}".format(histPricesReq.Symbol,
                                                                                                    histPricesReq.From,
                                                                                                    histPricesReq.To,
                                                                                                    str(e))
      self.DoLog(msg, MessageType.ERROR)
      ack = HistoricalPricesAck(Msg="HistoricalPricesAck", UUID=histPricesReq.UUID, ReqId=histPricesReq.ReqId, Success=False, Error=msg)
      self.DoSendResponse(ack)

  def ProcessCancelPositionReq(self,cancelRouteReq):
    try:

      self.DoLog("Incoming Cancel Position Req for positionId {}".format(cancelRouteReq.PosId),MessageType.INFO)
      wrapper =  CancelPositionWrapper(cancelRouteReq.PosId)

      state=self.InvokingModule.ProcessIncoming(wrapper)

      if state.Success:
        ack = CancelPositionAck(Msg="CancelAllPositionAck", UUID=cancelRouteReq.UUID,
                                ReqId=cancelRouteReq.ReqId,PosId=cancelRouteReq.PosId)
        self.DoSendResponse(ack)
        self.DoLog("Cancel positions id {} sent...".format(cancelRouteReq.PosId),MessageType.INFO)
      else:
        raise state.Exception

    except Exception as e:
      msg = "Critical ERROR for Incoming Cancel Position Req for posId {}. Error:{}".format(cancelRouteReq.PosId,str(e))
      self.DoLog(msg, MessageType.ERROR)
      ack = CancelAllPositionAck(Msg="CancelAllPositionAck", UUID=cancelRouteReq.UUID, ReqId=cancelRouteReq.ReqId,
                                 PosId=cancelRouteReq.PosId,Success=False, Error=msg)
      self.DoSendResponse(ack)

  def ProcessUpdateModelParamReq(self, updateModelParamReq):
    try:

      self.DoLog("Incoming Model Param Upd Req ",MessageType.INFO)
      wrapper =  UpdateModelParamReqWrapper(updateModelParamReq)

      state=self.InvokingModule.ProcessIncoming(wrapper)

      if state.Success:
        ack = UpdateModelParamAck(Msg="UpdateModelParamAck", UUID=updateModelParamReq.UUID,symbol=updateModelParamReq.Symbol,
                                  key=updateModelParamReq.Key, ReqId=updateModelParamReq.ReqId)
        self.DoSendResponse(ack)
        self.DoLog("Model Param Upd Req sent...",MessageType.INFO)
      else:
        raise state.Exception

    except Exception as e:
      msg = "Critical ERROR for Model Param Upd Req . Error:{}".format(str(e))
      self.DoLog(msg, MessageType.ERROR)
      ack = UpdateModelParamAck(Msg="UpdateModelParamAck", UUID=updateModelParamReq.UUID,
                                symbol=updateModelParamReq.Symbol,key=updateModelParamReq.Key, ReqId=updateModelParamReq.ReqId,
                                Success=False, Error=msg)
      self.DoSendResponse(ack)

  def ProcessCancelAllPositionReq(self,cancelAllRouteReq):
    try:

      self.DoLog("Incoming Cancel All Positions Req ",MessageType.INFO)
      wrapper =  CancelAllPositionsWrapper()

      state=self.InvokingModule.ProcessIncoming(wrapper)

      if state.Success:
        ack = CancelAllPositionAck(Msg="CancelAllPositionAck", UUID=cancelAllRouteReq.UUID, ReqId=cancelAllRouteReq.ReqId)
        self.DoSendResponse(ack)
        self.DoLog("Cancel All positions sent...",MessageType.INFO)
      else:
        raise state.Exception

    except Exception as e:
      msg = "Critical ERROR for Incoming Cancel all Positions Req . Error:{}".format(str(e))
      self.DoLog(msg, MessageType.ERROR)
      ack = CancelAllPositionAck(Msg="CancelAllPositionAck", UUID=cancelAllRouteReq.UUID, ReqId=cancelAllRouteReq.ReqId, Success=False, Error=msg)
      self.DoSendResponse(ack)


  def ProcessRoutePositionReq(self,routePos):

    try:

      self.DoLog("Incoming Route Position Req for symbol {} PosId {} qty {} side {}".format(routePos.Symbol,routePos.PosId,routePos.Qty,routePos.Side),MessageType.INFO)

      wrapper = PositionReqWrapper(routePos)

      state = self.InvokingModule.ProcessIncoming(wrapper)

      if state.Success:
        ack = RoutePositionAck(Msg="RoutePositionAck", UUID=routePos.UUID, ReqId=routePos.ReqId)
        self.DoSendResponse(ack)
        self.DoLog("Incoming Route Position Req for symbol {} PosId {} qty {} side {} successfully processed".format(routePos.Symbol,routePos.PosId, routePos.Qty, routePos.Side),MessageType.INFO)
      else:
        raise state.Exception


    except Exception as e:
      msg="Critical ERROR for Incoming Route Position Req for symbol {} PosId {} qty {} side {}. Error:{}".format(routePos.Symbol, routePos.PosId, routePos.Qty, routePos.Side,str(e))
      self.DoLog(msg, MessageType.ERROR)
      ack = RoutePositionAck(Msg="RoutePositionAck", UUID=routePos.UUID, ReqId=routePos.ReqId,Success=False,Error=msg)
      self.DoSendResponse(ack)

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
    self.SubscribedServices = {}
    self.Lock = threading.Lock()


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
      #self.write_message("{'Msg': 'hola'}")
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
      elif "Msg" in fieldsDict and fieldsDict["Msg"]=="UpdateModelParamReq":
        updModelParamReq = UpdateModelParamReq(**json.loads(message))
        self.ProcessUpdateModelParamReq(updModelParamReq)
      elif "Msg" in fieldsDict and fieldsDict["Msg"]=="CancelPositionReq":
        cancelPos = CancelPositionReq(**json.loads(message))
        self.ProcessCancelPositionReq(cancelPos)
      elif "Msg" in fieldsDict and fieldsDict["Msg"] == "HistoricalPricesReq":
        histPricesReq = HistoricalPricesReq(**json.loads(message))
        self.ProcessHistoricalPricesReq(histPricesReq)
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