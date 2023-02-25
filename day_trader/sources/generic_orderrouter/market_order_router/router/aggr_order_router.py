from sources.framework.common.logger.message_type import MessageType
from sources.generic_orderrouter.market_order_router.router.market_order_router import MarketOrderRouter, CMState, \
    Actions, PositionConverter, NewOrderWrapper, Order, SettlType, OrdType, TimeInForce, OrdStatus, Side
from sources.strategy.strategies.day_trader.common.converters.market_data_converter import MarketDataConverter, \
    MarketDataField


class MarketDataDTO:
    def __init__(self):
        self.Symbol=None
        self.BestBidPx=None
        self.BestAskPx=None


class AggrOrderRouter(MarketOrderRouter):

    def __init__(self):
        super().__init__()

        self.Name = "Aggr Order Router"
        self.LastMarketData={}


    def GetOrderPrice(self,symbol, side, orderPrice):

        if symbol in self.LastMarketData:

            if(self.LastMarketData[symbol].BestAskPx is None or self.LastMarketData[symbol].BestBidPx is None):
                return orderPrice

            if side==Side.Buy or side==Side.BuyToClose:
                return self.LastMarketData[symbol].BestAskPx
            elif side==Side.Sell or side==Side.SellShort:
                return self.LastMarketData[symbol].BestBidPx
            else:
                raise Exception("{} - Unrecognized side {}".format(self.Name,side))
        else:
            raise Exception("{} - Received order routing for not tracked symbol!:{}".format(self.Name,symbol))


    def ProcessMarketData(self,wrapper):

        dto = MarketDataDTO()
        dto.BestAskPx=wrapper.GetField(MarketDataField.BestAskPrice)
        dto.BestBidPx=wrapper.GetField(MarketDataField.BestBidPrice)
        dto.Symbol=wrapper.GetField(MarketDataField.Symbol)

        if(dto.Symbol is not None):
            self.LastMarketData[dto.Symbol]=dto


    def ProcessNewPosition(self, wrapper):
        try:

            self.PositionsLock.acquire()
            new_pos = PositionConverter.ConvertPosition(self, wrapper)
            # In this Generic Order Router ClOrdID=PosId
            self.Positions[new_pos.PosId] = new_pos
            orderPrice=self.GetOrderPrice(new_pos.Security.Symbol,new_pos.Side, new_pos.OrderPrice)
            new_pos.OrderPrice=orderPrice
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

    def ProcessIncoming(self, wrapper):
        try:

           if wrapper.GetAction() == Actions.MARKET_DATA:
                self.ProcessMarketData(wrapper)
                return CMState.BuildSuccess(self)
           elif wrapper.GetAction() == Actions.CANDLE_BAR_DATA:
                return CMState.BuildSuccess(self)
           else:
               return super().ProcessIncoming(wrapper)

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
            elif wrapper.GetAction() == Actions.MARKET_DATA:
                self.ProcessMarketData(wrapper)
                return CMState.BuildSuccess(self)
            else:
                raise Exception("Generic Aggr Order Router not prepared for routing message {}".format(wrapper.GetAction()))

        except Exception as e:
            self.DoLog("Error running ProcessMessage @OrderRouter.IB module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)


    def Initialize(self, pInvokingModule, pConfigFile):
        self.InvokingModule = pInvokingModule
        self.ModuleConfigFile = pConfigFile

        try:
            self.DoLog("Initializing Aggr Market Order Router", MessageType.INFO)
            if self.LoadConfig():
                self.OutgoingModule = self.InitializeModule(self.Configuration.OutgoingModule,self.Configuration.OutgoingConfigFile)
                self.DoLog("Generic Market Order Router Initialized", MessageType.INFO)
                return CMState.BuildSuccess(self)
            else:
                raise Exception("Unknown error initializing config file for Aggr Order Router")

        except Exception as e:

            self.DoLog("Error Loading Generic Aggr Order Router module:{}".format(str(e)), MessageType.ERROR)
            return CMState.BuildFailure(self, Exception=e)