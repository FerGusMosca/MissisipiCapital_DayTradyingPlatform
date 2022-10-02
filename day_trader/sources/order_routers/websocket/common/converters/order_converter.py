from sources.framework.business_entities.orders.order import *
from sources.framework.common.enums.fields.order_field import *
from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.OrdType import *
from sources.framework.common.enums.Side import *

class OrderConverter:

    def _SIDE_BUY(self):
        return "BUY"

    def _SIDE_SELL(self):
        return "SELL"

    def _ORD_TYPE_LIMIT(self):
        return "LMT"

    def _ORD_TYPE_MARKET(self):
        return "MKT"

    @staticmethod
    def ValidateNewOrder(self, wrapper):

        if wrapper.GetField(OrderField.OrdType) == None:
            raise Exception("Missing parameter {} for order".format(OrderField.OrdType))

        if wrapper.GetField(OrderField.Side) == None:
            raise Exception("Missing parameter {} for order".format(OrderField.Side))

        if wrapper.GetField(OrderField.Symbol) == None:
            raise Exception("Missing parameter {} for order".format(OrderField.Symbol))

        if wrapper.GetField(OrderField.OrderQty) == None:
            raise Exception("Missing parameter {} for order".format(OrderField.OrderQty))

    @staticmethod
    def ConvertNewOrder(self, wrapper):
        OrderConverter.ValidateNewOrder(self, wrapper)

        order = Order()
        order.Security = Security()

        order.Security.Symbol = wrapper.GetField(OrderField.Symbol)
        order.Security.SecurityType = wrapper.GetField(OrderField.SecurityType)
        order.Security.Exchange = wrapper.GetField(OrderField.Exchange)

        order.OrderQty = wrapper.GetField(OrderField.OrderQty)
        order.OrdType = wrapper.GetField(OrderField.OrdType)
        order.Side = wrapper.GetField(OrderField.Side)
        order.TimeInForce = wrapper.GetField(OrderField.TimeInForce)
        order.SettlType = wrapper.GetField(OrderField.SettlType)
        order.Account = wrapper.GetField(OrderField.Account)
        order.Price = wrapper.GetField(OrderField.Price)
        order.StopPx = wrapper.GetField(OrderField.StopPx)
        order.OrigClOrdId = wrapper.GetField(OrderField.OrigClOrdID)
        order.ClOrdId = wrapper.GetField(OrderField.ClOrdID)
        order.Currency = wrapper.GetField(OrderField.Currency)
        order.PriceType = wrapper.GetField(OrderField.PriceType)
        order.Account = wrapper.GetField(OrderField.Account)
        order.Broker = wrapper.GetField(OrderField.Broker)
        order.Strategy = wrapper.GetField(OrderField.Strategy)

        return order

