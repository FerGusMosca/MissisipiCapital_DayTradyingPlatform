import psycopg2
from psycopg2 import pool
import threading
import datetime
from sources.framework.common.logger.message_type import MessageType
from sources.framework.business_entities.positions.execution_summary import *
from sources.strategy.strategies.day_trader.common.converters.csv_converter import *


class ExecutionReportDataAccessLayer:

    # region Constructors
    def __init__(self, host, port, database, user, password):
      pass

    # endregion

    # region Private Methods

    def PersistOrder(self,order):
        pass

    def PersistExecutionSummary(self,fillId, executionSummary):
        pass

    # endregion

    # region Public Methods

    # endregion
