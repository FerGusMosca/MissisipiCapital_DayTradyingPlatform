from sources.framework.common.logger.message_type import *
class LogHelper:

    @staticmethod
    def LogPositionUpdate(logger,status,summary,execReport):
        logger.DoLog(
            "{}: TradeId={} PosId={} Symbol={} Side={} Final Status={} OrdQty={} CumQty={} LvsQty={} "
            "AvgPx={} Text={} "
                .format(status,
                        summary.GetTradeId(),
                        summary.Position.PosId,
                        summary.Position.Security.Symbol,
                        summary.Position.Side,
                        summary.Position.PosStatus,
                        summary.Position.Qty if summary.Position.Qty is not None else summary.Position.CashQty,
                        summary.CumQty,
                        summary.LeavesQty,
                        summary.AvgPx,
                        execReport.Text), MessageType.INFO)

