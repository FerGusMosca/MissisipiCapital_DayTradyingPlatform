from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.position_field import *
from sources.framework.common.enums.QuantityType import *
from sources.framework.common.enums.PriceType import *
from sources.framework.common.enums.Side import *
from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.PositionsStatus import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


class PositionNewReqWrapper(Wrapper):
    def __init__(self, pPosNewReq):
        self.PosNewReq=pPosNewReq



    #region Public Methods

    def GetAction(self):
        return Actions.DAY_TRADING_POSITION_NEW_REQUEST

    def GetField(self, field):
        if field is None:
            return None

        if field == PositionField.Symbol:
            return self.PosNewReq.Symbol
        elif field == PositionField.SecurityType:
            return self.PosNewReq.SecurityType
        elif field == PositionField.Exchange:
            return self.PosNewReq.Exchange
        else:
            return None

    #endregion

