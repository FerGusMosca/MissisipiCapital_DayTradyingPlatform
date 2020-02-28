from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.position_field import *
from sources.framework.common.enums.QuantityType import *
from sources.framework.common.enums.PriceType import *
from sources.framework.common.enums.Side import *
from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.PositionsStatus import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


class PositionUpdateReqWrapper(Wrapper):
    def __init__(self, pPosUpdateReq):
        self.PosUpdateReq=pPosUpdateReq



    #region Public Methods

    def GetAction(self):
        return Actions.DAY_TRADING_POSITION_UPDATE_REQUEST

    def GetField(self, field):
        if field is None:
            return None

        if field == PositionField.PosId:
            return self.PosUpdateReq.PosId
        elif field == PositionField.QuantityType:
            return QuantityType.SHARES
        elif field == PositionField.Qty:
            return self.PosUpdateReq.SharesQuantity
        elif field == PositionField.PosStatus:
            return self.PosUpdateReq.Active
        elif field == PositionField.TradingMode:
            return self.PosUpdateReq.TradingMode
        elif field == PositionField.Depurate:
            return self.PosUpdateReq.Depurate
        else:
            return None

    #endregion

