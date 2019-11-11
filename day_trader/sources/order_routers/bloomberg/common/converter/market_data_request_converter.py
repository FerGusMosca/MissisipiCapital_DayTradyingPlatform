
from sources.framework.common.enums.fields.market_data_request_field import *
from sources.framework.common.enums.SecurityType import *
from sources.framework.common.enums.OrdType import *
from sources.framework.common.enums.Side import *
from sources.framework.business_entities.market_data.market_data_request import *
from sources.framework.business_entities.market_data.candle_bar_request import *
from sources.framework.business_entities.market_data.candle_bar_request import *
from sources.framework.common.enums.fields.candle_bar_request_field import *
from sources.framework.common.enums.fields.historical_prices_request_field import *
from sources.framework.business_entities.securities.security import *

class MarketDataRequestConverter:

    @staticmethod
    def ValidatHistoricalPricesRequest(wrapper):
        if wrapper.GetField(HistoricalPricesRequestField.Security) == None:
            raise Exception("Missing parameter {} for historical prices request".format(HistoricalPricesRequestField.Security))

        if wrapper.GetField(HistoricalPricesRequestField.SubscriptionRequestType) == None:
            raise Exception("Missing parameter {} for historical prices request".format(HistoricalPricesRequestField.SubscriptionRequestType))

        if wrapper.GetField(HistoricalPricesRequestField.TimeUnit) == None:
            raise Exception("Missing parameter {} for historical prices request".format(HistoricalPricesRequestField.TimeUnit))

        if wrapper.GetField(HistoricalPricesRequestField.Time) == None:
            raise Exception("Missing parameter {} for historical prices request".format(HistoricalPricesRequestField.Time))

    @staticmethod
    def ValidateCandleBarRequest(wrapper):

        if wrapper.GetField(CandleBarRequestField.Security) == None:
            raise Exception("Missing parameter {} for candle bar request".format(CandleBarRequestField.Security))

        if wrapper.GetField(CandleBarRequestField.SubscriptionRequestType) == None:
            raise Exception("Missing parameter {} for candle bar request".format(CandleBarRequestField.SubscriptionRequestType))

    @staticmethod
    def ValidateMarketDataRequest( wrapper):

        if wrapper.GetField(MarketDataRequestField.Symbol) == None:
            raise Exception("Missing parameter {} for market data request".format(MarketDataRequestField.Symbol))

        if wrapper.GetField(MarketDataRequestField.SubscriptionRequestType) == None:
            raise Exception("Missing parameter {} for market data request".format(MarketDataRequestField.SubscriptionRequestType))

    @staticmethod
    def ConvertMarketDataRequest(wrapper):
        MarketDataRequestConverter.ValidateMarketDataRequest(wrapper)

        mdRequest = MarketDataRequest()
        mdRequest.Security= Security(
                                        Symbol=wrapper.GetField(MarketDataRequestField.Symbol),
                                        Currency = wrapper.GetField(MarketDataRequestField.Currency),
                                        SecType=  wrapper.GetField(MarketDataRequestField.SecurityType)
                                    )

        mdRequest.SubscriptionRequestType = wrapper.GetField(MarketDataRequestField.SubscriptionRequestType)

        return mdRequest

    @staticmethod
    def ConvertHistoricalPricesRequest( wrapper):
        MarketDataRequestConverter.ValidatHistoricalPricesRequest( wrapper)

        hpRequest = CandleBarRequest()
        hpRequest.Security = wrapper.GetField(HistoricalPricesRequestField.Security)
        hpRequest.TimeUnit = wrapper.GetField(HistoricalPricesRequestField.TimeUnit)
        hpRequest.Time = wrapper.GetField(HistoricalPricesRequestField.Time)
        hpRequest.SubscriptionRequestType = wrapper.GetField(HistoricalPricesRequestField.SubscriptionRequestType)

        return hpRequest

    @staticmethod
    def ConvertCandleBarRequest( wrapper):
        MarketDataRequestConverter.ValidateCandleBarRequest(wrapper)

        cbRequest = CandleBarRequest()
        cbRequest.Security=wrapper.GetField(CandleBarRequestField.Security)
        cbRequest.TimeUnit = wrapper.GetField(CandleBarRequestField.TimeUnit)
        cbRequest.Time = wrapper.GetField(CandleBarRequestField.Time)
        cbRequest.SubscriptionRequestType = wrapper.GetField(CandleBarRequestField.SubscriptionRequestType)

        return cbRequest