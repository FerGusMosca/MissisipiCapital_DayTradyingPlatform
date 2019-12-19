from sources.framework.business_entities.market_data.market_data import *
from sources.framework.business_entities.securities.security import *
from sources.framework.business_entities.market_data.candle_bar import *
from sources.framework.common.enums.fields.market_data_field import *
from sources.framework.common.enums.fields.candle_bar_field import *
from sources.framework.common.enums.fields.historical_prices_field import *

class MarketDataConverter:

    @staticmethod
    def ValidateHistoricalPrices(wrapper):
        try:
            if wrapper.GetField(HistoricalPricesField.Security) == None:
                raise Exception("Missing parameter {} for historical prices".format(HistoricalPricesField.Security))
            elif wrapper.GetField(HistoricalPricesField.MarketDataArray) == None:
                raise Exception("Missing parameter {} for historical prices".format(HistoricalPricesField.MarketDataArray))
        except Exception as e:
            raise Exception("Error processing market data msg:{}".format(str(e)))

    @staticmethod
    def ValidateMarketData(wrapper):
        try:
            if wrapper.GetField(MarketDataField.Symbol) == None:
                raise Exception("Missing parameter {} for market data".format(MarketDataField.Symbol))
        except Exception as e:
            raise Exception("Error processing market data msg:{}".format(str(e)))

    @staticmethod
    def ValidateCandlebar(wrapper):
        try:
            if wrapper.GetField(CandleBarField.Security) == None:
                raise Exception("Missing parameter {} for candle bar".format(CandleBarField.Security))
        except Exception as e:
            raise Exception("Error processing candle bar msg:{}".format(str(e)))

    @staticmethod
    def BuildSecurity(wrapper):
        sec = Security()
        sec.Symbol=wrapper.GetField(MarketDataField.Symbol)
        sec.SecurityType = wrapper.GetField(MarketDataField.SecurityType)
        sec.Currency = wrapper.GetField(MarketDataField.Currency)
        sec.Exchange = wrapper.GetField(MarketDataField.MDMkt)
        return sec

    @staticmethod
    def ConvertHistoricalPrices(wrapper):
        MarketDataConverter.ValidateHistoricalPrices(wrapper)

        sec = wrapper.GetField(HistoricalPricesField.Security)
        marketDataArr =wrapper.GetField(HistoricalPricesField.MarketDataArray)

        for md in marketDataArr:
            sec.MarketDataArr [ md.MDEntryDate]=md

        return sec


    @staticmethod
    def ConvertMarketData(wrapper):
        MarketDataConverter.ValidateMarketData(wrapper)

        md = MarketData()
        md.Security = MarketDataConverter.BuildSecurity(wrapper)

        md.TradingSessionHighPrice = wrapper.GetField(MarketDataField.TradingSessionHighPrice)
        md.TradingSessionLowPrice = wrapper.GetField(MarketDataField.TradingSessionLowPrice)
        md.OpeningPrice = wrapper.GetField(MarketDataField.OpeningPrice)
        md.Imbalance = wrapper.GetField(MarketDataField.Imbalance)
        md.Trade = wrapper.GetField(MarketDataField.Trade)
        md.OpeningPrice = wrapper.GetField(MarketDataField.OpeningPrice)
        md.ClosingPrice = wrapper.GetField(MarketDataField.ClosingPrice)
        md.BestBidPrice = wrapper.GetField(MarketDataField.BestBidPrice)
        md.BestAskPrice = wrapper.GetField(MarketDataField.BestAskPrice)
        md.BestBidSize = wrapper.GetField(MarketDataField.BestBidSize)
        md.BestAskSize = wrapper.GetField(MarketDataField.BestAskSize)
        md.BestBidCashSize = wrapper.GetField(MarketDataField.BestBidCashSize)
        md.BestAskCashSize = wrapper.GetField(MarketDataField.BestAskCashSize)
        md.TradeVolume = wrapper.GetField(MarketDataField.TradeVolume)
        md.MDTradeSize = wrapper.GetField(MarketDataField.MDTradeSize)
        md.BestAskExch = wrapper.GetField(MarketDataField.BestAskExch)
        md.BestBidExch = wrapper.GetField(MarketDataField.BestBidExch)
        md.Change = wrapper.GetField(MarketDataField.Change)
        md.StdDev = wrapper.GetField(MarketDataField.StdDev)


        return md

    @staticmethod
    def ConvertCandlebar(wrapper):
        MarketDataConverter.ValidateCandlebar(wrapper)

        cb = CandleBar(wrapper.GetField(CandleBarField.Security))
        cb.DateTime = wrapper.GetField(CandleBarField.DateTime)
        cb.Volume = wrapper.GetField(CandleBarField.Volume)
        cb.Value = wrapper.GetField(CandleBarField.Value)
        cb.NumberOfTicks = wrapper.GetField(CandleBarField.NumberOfTicks)
        cb.Low = wrapper.GetField(CandleBarField.Low)
        cb.High = wrapper.GetField(CandleBarField.High)
        cb.Time = wrapper.GetField(CandleBarField.Time)
        cb.Close = wrapper.GetField(CandleBarField.Close)
        cb.Open = wrapper.GetField(CandleBarField.Open)

        return cb

