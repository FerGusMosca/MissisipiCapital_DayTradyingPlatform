import threading
from sources.framework.common.abstract.base_communication_module import BaseCommunicationModule
from sources.framework.common.enums.QuantityType import QuantityType
from sources.framework.common.enums.fields.market_data_field import MarketDataField
from sources.framework.common.interfaces.icommunication_module import ICommunicationModule
from sources.framework.common.logger.message_type import MessageType
from sources.generic_orderrouter.market_order_router.common.wrappers.update_order_wrapper import UpdateOrderWrapper
from sources.generic_orderrouter.market_order_router.router.market_order_router import MarketOrderRouter, Side, \
    PositionConverter, NewOrderWrapper, Order, SettlType, OrdType, TimeInForce, OrdStatus, Actions, CMState, uuid, \
    ExecutionReportConverter
import time
from time import mktime

class MarketDataDTO:
    def __init__(self):
        self.Symbol=None
        self.BestBidPx=None
        self.BestAskPx=None


class PassiveAggrOrderRouter(MarketOrderRouter):

    _UPDATE_ORD_PACING_SEC=1

    def __init__(self):
        super().__init__()

        self.Name = "Passive Aggr. Order Router"
        self.LastMarketData={}


    #region Private Methods

    def GetOrderQty(self,pos,price):

        if pos.QuantityType==QuantityType.CURRENCY:
            return pos.CashQty//price #FLOOR!
        elif pos.QuantityType==QuantityType.SHARES or pos.QuantityType==QuantityType.BONDS\
             or pos.QuantityType==QuantityType.CONTRACTS or pos.QuantityType==QuantityType.CRYPTOCURRENCY:
            return pos.Qty
        else:
            raise Exception("New position for symbol {} : Invalid Quantity Type!:{}".format(pos.Security.Symbol,pos.QuantityType))


    def GetOrderPrice(self,symbol, side, orderPrice):

        if symbol in self.LastMarketData:

            if(self.LastMarketData[symbol].BestAskPx is None or self.LastMarketData[symbol].BestBidPx is None):
                return orderPrice

            if side==Side.Buy or side==Side.BuyToClose:
                return self.LastMarketData[symbol].BestBidPx-30#DBG-Price Manip
            elif side==Side.Sell or side==Side.SellShort:
                return self.LastMarketData[symbol].BestAskPx+30#DBG-Price Manip
            else:
                raise Exception("{} - Unrecognized side {}".format(self.Name,side))
        else:
            raise Exception("{} - Received order routing for not tracked symbol!:{}".format(self.Name,symbol))


    def ProcessMarketData(self,wrapper):
        try:
            self.PositionsLock.acquire(blocking=True)
            dto = MarketDataDTO()
            dto.BestAskPx=wrapper.GetField(MarketDataField.BestAskPrice)
            dto.BestBidPx=wrapper.GetField(MarketDataField.BestBidPrice)
            dto.Symbol=wrapper.GetField(MarketDataField.Symbol)

            self.DoLog("Passive Aggr Order Router= Recv Market Data? symbol {} : Best Bid={} Best Ask={}"
                       .format(dto.Symbol, dto.BestBidPx, dto.BestAskPx), MessageType.INFO)

            if(dto.Symbol is not None):
                self.DoLog("{}r= Saving Market Data for symbol {} : Best Bid={} Best Ask={}"
                           .format(self.Name,dto.Symbol,dto.BestBidPx,dto.BestAskPx),MessageType.INFO)
                self.LastMarketData[dto.Symbol]=dto
        except Exception as e:
            self.DoLog("CRITICAL ERROR updating market data @{}} module:{}".format(self.Name,str(e)), MessageType.ERROR)
        finally:
            if self.PositionsLock.locked():
                self.PositionsLock.release()

    def ProcessExecutionReport(self,wrapper):
        try:

            self.PositionsLock.acquire(blocking=True)
            execReport = ExecutionReportConverter.ConvertExecutionReport(wrapper)

            pos = next(filter(lambda x: x.GetLastOrder() is not None and x.GetLastOrder().ClOrdId == execReport.ClOrdId,
                       self.Positions.values()), None)

            if(pos is not None):
                pos.SetPositionStatusFromExecution(execReport)

            if self.PositionsLock.locked():
                self.PositionsLock.release()

            super().ProcessExecutionReport(wrapper)

        except Exception as e:
            self.DoLog("CRITICAL ERROR at ProcessExecutionReport @{}} module:{}".format(self.Name, str(e)),
                       MessageType.ERROR)
        finally:
            if self.PositionsLock.locked():
                self.PositionsLock.release()

    def UpdatePositionThread(self):

        while True:
            try:
                time.sleep(PassiveAggrOrderRouter._UPDATE_ORD_PACING_SEC)
                self.PositionsLock.acquire(blocking=True)

                for pos in self.Positions.values():
                    if pos.IsOpenPosition():
                        lastPrice = self.GetOrderPrice(pos.Security.Symbol,pos.Side,pos.OrderPrice)
                        if pos.OrderPrice!= lastPrice :
                            self.DoLog("Updating Price for PosId {} (Symbol={}) {}-->{}".format(pos.PosId,pos.Security.Symbol,pos.OrderPrice,lastPrice),MessageType.INFO)

                            lastOrder =pos.GetLastOrder()
                            if lastOrder is not None:
                                newOrder = lastOrder.Clone()
                                newOrder.OrigClOrdId=lastOrder.ClOrdId
                                newOrder.OrderId=lastOrder.OrderId
                                newOrder.ClOrdId=pos.LoadUpdateOrdNewClOrdId()
                                newOrder.Price=lastPrice

                                updWrapper = UpdateOrderWrapper(pos.Security.Symbol,newOrder.OrigClOrdId,newOrder.ClOrdId,newOrder.OrderId,
                                                                newOrder.Side,newOrder.OrdType,newOrder.Price,newOrder.OrderQty)

                                pos.AppendOrder(newOrder)
                                pos.OrderPrice=lastPrice
                                if self.PositionsLock.locked():
                                    self.PositionsLock.release()
                                self.OutgoingModule.ProcessMessage(updWrapper)
                            else:
                                self.DoLog("No last Order for Pos {} with Pos Status {}. Potential conflict".format(pos.PosId,pos.PosStatus),MessageType.INFO)


            except Exception as e:
                self.DoLog("CRITICAL ERROR at UpdatePositionThread @{}} module:{}".format(self.Name, str(e)),
                           MessageType.ERROR)
            finally:
                if self.PositionsLock.locked():
                    self.PositionsLock.release()

    def ProcessNewPosition(self, wrapper):
        try:

            self.PositionsLock.acquire(blocking=True)
            new_pos = PositionConverter.ConvertPosition(self, wrapper)
            # In this Generic Order Router ClOrdID=PosId
            self.Positions[new_pos.PosId] = new_pos
            orderPrice=self.GetOrderPrice(new_pos.Security.Symbol,new_pos.Side, new_pos.OrderPrice)
            orderQty = self.GetOrderQty(new_pos,orderPrice)

            new_pos.OrderPrice=orderPrice
            new_pos.Qty=orderQty

            clOrdId=new_pos.LoadNextClOrdId()
            order_wrapper = NewOrderWrapper(new_pos.Security.Symbol, orderQty, clOrdId,
                                            new_pos.Security.Currency,new_pos.Security.SecurityType,new_pos.Security.Exchange,
                                            new_pos.Side, new_pos.Account, new_pos.Broker,
                                            new_pos.Strategy, new_pos.OrderType, new_pos.OrderPrice)
            new_pos.Orders.append(Order(ClOrdId=clOrdId,Security=new_pos.Security,SettlType=SettlType.Regular,
                                        Side=new_pos.Side,Exchange=new_pos.Exchange,OrdType=OrdType.Limit,
                                        QuantityType=QuantityType.SHARES,OrderQty=orderQty,PriceType=new_pos.PriceType,
                                        Price=None,StopPx=None,Currency=new_pos.Security.Currency,
                                        TimeInForce=TimeInForce.Day,Account=new_pos.Account,
                                        OrdStatus=OrdStatus.PendingNew,Broker=new_pos.Broker,Strategy=new_pos.Strategy))

            self.DoLog("{}= Sending order to market for symbol {} : Side={} Qty={} Price={}"
                       .format(self.Name,new_pos.Security.Symbol,new_pos.Side,new_pos.Qty,new_pos.OrderPrice), MessageType.INFO)
            if self.PositionsLock.locked():
                self.PositionsLock.release()
            return self.OutgoingModule.ProcessMessage(order_wrapper)
        except Exception as e:
            self.DoLog("CRITICAL ERROR sending order to  market @{} module:{}".format(self.Name,str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self,Exception=e)
        finally:
            if self.PositionsLock.locked():
                self.PositionsLock.release()

    #endregion

    #region Module Methods

    def ProcessIncoming(self, wrapper):
        try:

           if wrapper.GetAction() == Actions.MARKET_DATA:
                self.ProcessMarketData(wrapper)
                return CMState.BuildSuccess(self)
           if wrapper.GetAction() == Actions.EXECUTION_REPORT:
                self.ProcessExecutionReport(wrapper)
                return CMState.BuildSuccess(self)
           elif wrapper.GetAction() == Actions.CANDLE_BAR_DATA:
                return CMState.BuildSuccess(self)
           else:
               self.DoLog("WARNING-Not recognized Action @{}:{}".format(self.Name,wrapper.GetAction()),MessageType.DEBUG)
               return CMState.BuildSuccess(self)

        except Exception as e:
            self.DoLog("CRITICAL ERROR @ProcessIncoming @{} :{}".format(self.Name, str(e)),MessageType.ERROR)
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
            elif wrapper.GetAction() == Actions.MARKET_DATA:
                self.ProcessMarketData(wrapper)
                return CMState.BuildSuccess(self)
            else:
                raise Exception("Generic Aggr Order Router not prepared for routing message {}".format(wrapper.GetAction()))

        except Exception as e:
            self.DoLog("CRITICAL ERROR @ProcessMessage @{} :{}".format(self.Name, str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def Initialize(self, pInvokingModule, pConfigFile):
        self.InvokingModule = pInvokingModule
        self.ModuleConfigFile = pConfigFile

        try:
            self.DoLog("Initializing {}".format(self.Name), MessageType.INFO)
            if self.LoadConfig():
                self.OutgoingModule = self.InitializeModule(self.Configuration.OutgoingModule,self.Configuration.OutgoingConfigFile)

                threading.Thread(target=self.UpdatePositionThread, args=()).start()
                self.DoLog("{} Initialized".format(self.Name), MessageType.INFO)
                return CMState.BuildSuccess(self)
            else:
                raise Exception("Unknown error initializing config file for {}".format(self.Name))

        except Exception as e:

            self.DoLog("Error Loading {}} module:{}".format(self.Name,str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)

    #endregion