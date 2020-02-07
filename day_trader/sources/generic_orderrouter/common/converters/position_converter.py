from sources.framework.business_entities.market_data.market_data import *
from sources.framework.business_entities.positions.position import *
from sources.framework.business_entities.securities.security import *
from sources.framework.common.enums.fields.position_field import *


class PositionConverter:

    @staticmethod
    def ValidatePosition(self, wrapper):
        if wrapper.GetField(PositionField.PosId) is None:
            raise Exception("Missing parameter {} for position".format(PositionField.PosId))

        if wrapper.GetField(PositionField.Symbol) is None:
            raise Exception("Missing parameter {} for position".format(PositionField.Symbol))

        if wrapper.GetField(PositionField.QuantityType) is None:
            raise Exception("Missing parameter {} for position".format(PositionField.QuantityType))

        if wrapper.GetField(PositionField.Side) is None:
            raise Exception("Missing parameter {} for position".format(PositionField.Side))

        qt = wrapper.GetField(PositionField.QuantityType)
        if qt == QuantityType.SHARES or qt == QuantityType.BONDS or qt == QuantityType.CONTRACTS:
            if wrapper.GetField(PositionField.Qty) is None:
                raise Exception("Missing position quantity for quantity type".format(PositionField.QuantityType))

        if qt == QuantityType.CURRENCY:
            if wrapper.GetField(PositionField.CashQty) is None:
                raise Exception(
                    "Missing position cash quantity for quantity type {}".format(PositionField.QuantityType))

    @staticmethod
    def ConvertPosition(self, wrapper):
        PositionConverter.ValidatePosition(self, wrapper)

        pos = Position()
        pos.Security = Security()

        pos.Security.Symbol = wrapper.GetField(PositionField.Symbol)
        pos.Security.SecurityType = wrapper.GetField(PositionField.SecurityType)
        pos.Security.Currency = wrapper.GetField(PositionField.Currency)
        pos.Security.Exchange = wrapper.GetField(PositionField.Exchange)

        pos.OrderQty = wrapper.GetField(PositionField.Qty)
        pos.PosId = wrapper.GetField(PositionField.PosId)

        pos.Exchange = wrapper.GetField(PositionField.Exchange)
        pos.QuantityType = wrapper.GetField(PositionField.QuantityType)
        pos.PriceType = wrapper.GetField(PositionField.PriceType)
        pos.CashQty = wrapper.GetField(PositionField.CashQty)
        pos.Percent = wrapper.GetField(PositionField.Percent)
        pos.ExecutionReports = wrapper.GetField(PositionField.ExecutionReports)
        pos.Side = wrapper.GetField(PositionField.Side)
        pos.PositionRejectReason = wrapper.GetField(PositionField.PositionRejectReason)
        pos.PositionRejectText = wrapper.GetField(PositionField.PositionRejectText)
        pos.PosStatus = wrapper.GetField(PositionField.PosStatus)
        pos.Account = wrapper.GetField(PositionField.Account)
        pos.Broker = wrapper.GetField(PositionField.Broker)
        pos.Strategy = wrapper.GetField(PositionField.Strategy)
        pos.OrderType = wrapper.GetField(PositionField.OrderType)
        pos.OrderPrice = wrapper.GetField(PositionField.OrderPrice)

        return pos
