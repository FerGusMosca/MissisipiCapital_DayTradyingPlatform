from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.position_field import *


class PositionWrapper(Wrapper):
    def __init__(self, pPosition):
        self.Position = pPosition

    def GetAction(self):
        return Actions.NEW_POSITION

    def GetField(self, field):
        if field is None:
            return None

        if field == PositionField.Symbol:
            return self.Position.Security.Symbol
        elif field == PositionField.PosId:
            return self.Position.PosId
        elif field == PositionField.Exchange:
            return self.Position.Security.Exchange
        elif field == PositionField.QuantityType:
            return self.Position.QuantityType
        elif field == PositionField.PriceType:
            return self.Position.PriceType
        elif field == PositionField.Qty:
            return self.Position.Qty
        elif field == PositionField.CashQty:
            return self.Position.CashQty
        elif field == PositionField.Percent:
            return self.Position.Percent
        elif field == PositionField.ExecutionReports:
            return self.Position.ExecutionReports
        elif field == PositionField.Orders:
            return self.Position.Orders
        elif field == PositionField.Side:
            return self.Position.Side
        elif field == PositionField.PosStatus:
            return self.Position.PosStatus
        # elif field == PositionField.Security: #TODO Impl SecurityWrapper
        # return self.Position.Security
        elif field == PositionField.Currency:
            return self.Position.Security.Currency
        elif field == PositionField.SecurityType:
            return self.Position.Security.SecurityType
        elif field == PositionField.Account:
            return self.Position.Account
        elif field == PositionField.Broker:
            return self.Position.Broker
        elif field == PositionField.Strategy:
            return self.Position.Strategy
        elif field == PositionField.OrderType:
            return self.Position.OrderType
        elif field == PositionField.OrderPrice:
            return self.Position.OrderPrice
        else:
            return None

