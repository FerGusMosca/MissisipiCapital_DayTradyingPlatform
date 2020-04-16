from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.trading_signal_field  import *

from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.PositionsStatus import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


class TradingSignalWrapper(Wrapper):
    def __init__(self,pTradingSignal):
        self.TradingSignal = pTradingSignal

    #region Public Methods

    def GetAction(self):
        return Actions.TRADING_SIGNAL

    def GetField(self, field):
        if field == TradingSignalField.Symbol:
            return self.TradingSignal.Security.Symbol
        elif field == TradingSignalField.Signal:
            return self.TradingSignal.Signal
        elif field == TradingSignalField.Recommendation:
            return self.TradingSignal.Recommendation
        else:
            return None

    #endregion
