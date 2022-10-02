from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.market_data_request_field import *
from sources.framework.common.enums.SubscriptionRequestType import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


_CURRENCY="USD"
_EXCHANGE="US"

class MarketDataReqWrapper(Wrapper):
    def __init__(self, pSymbol):
        self.Symbol=pSymbol



    #region Public Methods

    def GetAction(self):
        return Actions.MARKET_DATA_REQUEST

    def GetField(self, field):
        if field is None:
            return None

        if field == MarketDataRequestField.Symbol:
            return self.Symbol
        elif field == MarketDataRequestField.Currency:
            return _CURRENCY
        elif field == MarketDataRequestField.Exchange:
            return _EXCHANGE
        elif field == MarketDataRequestField.SecurityType:
            return SecurityType.CS
        elif field == MarketDataRequestField.SubscriptionRequestType:
            return SubscriptionRequestType.Snapshot
        else:
            return None

    #endregion

