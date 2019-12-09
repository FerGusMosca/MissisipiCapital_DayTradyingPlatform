from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.historical_prices_request_field import *
from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.PositionsStatus import *
from sources.strategy.strategies.day_trader.strategy.services.websocket.common.DTO.order_routing.route_position_req import *


class HistoricalPricesReqWrapper(Wrapper):
    def __init__(self,symbol,fromDate,toDate):
        self.Symbol = symbol
        self.From=fromDate
        self.To=toDate

    #region Public Methods

    def GetAction(self):
        return Actions.HISTORICAL_PRICES_REQUEST

    def GetField(self, field):
        if field == HistoricalPricesRequestField.Security:
            return self.Symbol
        elif field == HistoricalPricesRequestField.From:
            return self.From
        elif field == HistoricalPricesRequestField.To:
            return self.To
        else:
            return None

    #endregion
