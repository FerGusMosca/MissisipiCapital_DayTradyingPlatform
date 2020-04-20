from sources.framework.common.logger.message_type import *
import datetime
class LogHelper:

    @staticmethod
    def LogPublishMarketDataOnSecurity(sender,logger,symbol,sec):
        logger.DoLog("At {}: {}-Publishing market data for symbol {}: MDEntryDate={} Timestamp={} Last={} Bid={} Ask={} Mid={}".format(
            sender,
            datetime.datetime.now(),
            symbol,
            sec.MarketData.MDEntryDate if sec.MarketData.MDEntryDate is not None else "?",
            sec.MarketData.Timestamp if sec.MarketData.Timestamp is not None else "?",
            sec.MarketData.Trade if sec.MarketData.Trade is not None else "-",
            sec.MarketData.BestBidPrice if sec.MarketData.BestBidPrice is not None else "-",
            sec.MarketData.BestAskPrice if sec.MarketData.BestAskPrice is not None else "-",
            sec.MarketData.MidPrice if sec.MarketData.MidPrice is not None else "-"),
            MessageType.DEBUG)

    @staticmethod
    def LogPublishCandleBarOnSecurity(sender,logger,symbol,cb):
        logger.DoLog("At {}: {}-Publishing candle bar  for symbol {}: Time={} DateTime={} Timestamp={} Open={} High={} Low={} Last={}".format(
            sender,
            datetime.datetime.now(),
            symbol,
            cb.Time if cb.Time is not None else "-",
            cb.DateTime if cb.DateTime is not None else "-",
            cb.Timestamp if cb.Timestamp is not None else "-",
            cb.Open if cb.Open is not None else "-",
            cb.High if cb.High is not None else "-",
            cb.Low if cb.Low is not None else "-",
            cb.Close if cb.Close is not None else "-" ),
            MessageType.DEBUG)


    @staticmethod
    def LogNewOrder(logger,newOrder):
        logger.DoLog("Placing Order On Market: ClOrdId {} Symbol {} secType {} orderType {} totalQty {} "
                    .format(newOrder.ClOrdId, newOrder.Security.Symbol,
                            newOrder.Security.SecurityType,
                            newOrder.OrdType, newOrder.OrderQty), MessageType.INFO)