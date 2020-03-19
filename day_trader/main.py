
from sources.framework.common.logger.logger import *
from sources.framework.common.logger.message_type import MessageType
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.execution_report_field import *
from sources.framework.common.enums.fields.market_data_field import *
from sources.strategy.strategies.day_trader.strategy.day_trader import DayTrader


class MainApp:

    def __init__(self):#test
        self.processor = None
        self.logger = Logger()
        self.logger.use_timed_rotating_file_handler()

    def DoLog(self, msg, message_type):
        """ Log every message from strategy and other modules

        Args:
            msg (String): Message to log.
            message_type (:obj:`Enum`): MessageType (DEBUG, INFO, WARNING, ..).
        """
        self.logger.print(msg, message_type)

    def ProcessOutgoing(self, wrapper):
        """ To Process Order Routing Module messages.

        Args:
            wrapper (:obj:`Wrapper`): Generic wrapper to communicate strategy with other modules.
        """
        if wrapper.GetAction() == Actions.EXECUTION_REPORT:
            symbol = wrapper.GetField(ExecutionReportField.Symbol)
            ord_status = wrapper.GetField(ExecutionReportField.OrdStatus)
            self.DoLog("MainApp: Received Exec Report {} for symbol {}".format(ord_status, symbol), MessageType.INFO)
        elif wrapper.GetAction() == Actions.MARKET_DATA:
            symbol = wrapper.GetField(MarketDataField.Symbol)
            last = wrapper.GetField(MarketDataField.Trade)
            self.DoLog("MainApp: Received Market Data Trade {} for symbol {}".format(last, symbol), MessageType.INFO)
        else:
            self.DoLog("MainApp: Not prepared for routing message {}".format(wrapper.GetAction()), MessageType.INFO)

    def run(self):
        """Create new Simple CSV Processor object strategy, then initialize

        """
        self.processor = DayTrader()
        self.processor.Initialize(self, "configs/day_trader.ini")


if __name__ == '__main__':
    app = MainApp()
    app.run()
    input()

