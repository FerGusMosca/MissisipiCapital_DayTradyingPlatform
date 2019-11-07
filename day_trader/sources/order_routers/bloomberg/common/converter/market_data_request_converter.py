
from sources.framework.common.enums.fields.market_data_request_field import *
from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.OrdType import *
from sources.framework.common.enums.Side import *
from sources.framework.business_entities.market_data.market_data_request import *
from sources.framework.business_entities.market_data.candle_bar_request import *
from sources.framework.common.enums.fields.candle_bar_request_field import *
from sources.framework.business_entities.securities.security import *

class MarketDataRequestConverter:

    @staticmethod
    def ValidateCandleBarRequest(self, wrapper):

        if wrapper.GetField(CandleBarRequestField.Security) == None:
            raise Exception("Missing parameter {} for candle bar request".format(CandleBarRequestField.Security))

        if wrapper.GetField(CandleBarRequestField.SubscriptionRequestType) == None:
            raise Exception("Missing parameter {} for candle bar request".format(CandleBarRequestField.SubscriptionRequestType))

    @staticmethod
    def ValidateMarketDataRequest(self, wrapper):

        if wrapper.GetField(MarketDataRequestField.Symbol) == None:
            raise Exception("Missing parameter {} for market data request".format(MarketDataRequestField.Symbol))

        if wrapper.GetField(MarketDataRequestField.SubscriptionRequestType) == None:
            raise Exception("Missing parameter {} for market data request".format(MarketDataRequestField.SubscriptionRequestType))

    @staticmethod
    def ConvertMarketDataRequest(self, wrapper):
        MarketDataRequestConverter.ValidateMarketDataRequest(self, wrapper)

        mdRequest = MarketDataRequest()
        mdRequest.Security= Security(
                                        Symbol=wrapper.GetField(MarketDataRequestField.Symbol),
                                        Currency = wrapper.GetField(MarketDataRequestField.Currency),
                                        SecType=  wrapper.GetField(MarketDataRequestField.SecurityType)
                                    )

        mdRequest.SubscriptionRequestType = wrapper.GetField(MarketDataRequestField.SubscriptionRequestType)

        return mdRequest

    @staticmethod
    def ConvertCandleBarRequest(self, wrapper):
        MarketDataRequestConverter.ValidateCandleBarRequest(self, wrapper)

        cbRequest = CandleBarRequest()
        cbRequest.Security=wrapper.GetField(CandleBarRequestField.Security)
        cbRequest.TimeUnit = wrapper.GetField(CandleBarRequestField.TimeUnit)
        cbRequest.Time = wrapper.GetField(CandleBarRequestField.Time)
        cbRequest.SubscriptionRequestType = wrapper.GetField(CandleBarRequestField.SubscriptionRequestType)

        return cbRequest