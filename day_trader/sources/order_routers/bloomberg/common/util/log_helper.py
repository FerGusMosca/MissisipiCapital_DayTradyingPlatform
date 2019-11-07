from sources.framework.common.logger.message_type import *
class LogHelper:

    @staticmethod
    def LogPublishMarketDataOnSecurity(logger,symbol,sec):
        logger.DoLog("Publishing market data for symbol {}: Last={} Bid={} Ask={} Mid={}".format(
            symbol,
            sec.MarketData.Trade if sec.MarketData.Trade is not None else "-",
            sec.MarketData.BestBidPrice if sec.MarketData.BestBidPrice is not None else "-",
            sec.MarketData.BestAskPrice if sec.MarketData.BestAskPrice is not None else "-",
            sec.MarketData.MidPrice if sec.MarketData.MidPrice is not None else "-"),
            MessageType.DEBUG)

    @staticmethod
    def LogPublishCandleBarOnSecurity(logger,symbol,cb):
        logger.DoLog("Publishing candle bar  for symbol {}: Time={} Open={} High={} Low={} Last={}".format(
            symbol,
            cb.Time if cb.Time is not None else "-",
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