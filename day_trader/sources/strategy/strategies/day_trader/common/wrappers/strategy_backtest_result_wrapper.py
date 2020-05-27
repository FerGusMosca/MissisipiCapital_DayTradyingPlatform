from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.strategy_backtest_result_field  import *


class StrategyBacktestResultWrapper(Wrapper):
    def __init__(self,pSymbol,pBacktestResultDtoArr):
        self.Symbol = pSymbol
        self.BacktestResultDtoArr = pBacktestResultDtoArr

    #region Public Methods

    def GetAction(self):
        return Actions.STRATEGY_BACKTEST_RESULT

    def GetField(self, field):
        if field == StrategyBacktestResultField.Symbol:
            return self.Symbol
        elif field == StrategyBacktestResultField.Results:
            return self.BacktestResultDtoArr
        else:
            return None

    #endregion
