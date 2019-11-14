from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.position_field import *
from sources.framework.common.enums.QuantityType import *
from sources.framework.common.enums.PriceType import *
from sources.framework.common.enums.Side import *
from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.PositionsStatus import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


class PositionReqWrapper(Wrapper):
    def __init__(self, pRoutePositionReq):
        self.RoutePositionReq = pRoutePositionReq

    #region Private Methods

    def GetSide(self):
        if self.RoutePositionReq.Side == RoutePositionReq._BUY():
            return Side.Buy
        elif self.RoutePositionReq.Side == RoutePositionReq._SELL():
            return Side.Sell
        else:
            return Side.Unknown

    #endregion


    #region Public Methods

    def GetAction(self):
        return Actions.NEW_POSITION

    def GetField(self, field):
        if field is None:
            return None

        if field == PositionField.Symbol:
            return self.RoutePositionReq.Symbol
        elif field == PositionField.QuantityType:
            return QuantityType.SHARES
        elif field == PositionField.PriceType:
            return PriceType.FixedAmount
        elif field == PositionField.Qty:
            return self.RoutePositionReq.Qty
        elif field == PositionField.Side:
            return self.GetSide()
        elif field == PositionField.PosStatus:
            return PositionStatus.PendingNew
        elif field == PositionField.Error:
            return SecurityType.CS
        elif field == PositionField.Account:
            return self.RoutePositionReq.Account
        else:
            return None

    #endregion

