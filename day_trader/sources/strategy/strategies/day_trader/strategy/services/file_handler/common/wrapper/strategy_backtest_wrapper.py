from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.strategy_backtest_field import *
from sources.strategy.strategies.day_trader.strategy.services.file_handler.common.dto.strategy_backtest_dto import *



class StrategyBacktestWrapper(Wrapper):
    def __init__(self,pStrategyBacktestDTO):
        self.StrategyBacktestDTO = pStrategyBacktestDTO

    #region Public Methods

    def GetAction(self):
        return Actions.STRATEGY_BACKTEST

    def GetField(self, field):
        if field == StrategyBacktestField.Symbol:
            return self.StrategyBacktestDTO.Security.Symbol
        elif field == StrategyBacktestField.ReferenceDate:
            return self.StrategyBacktestDTO.ReferenceDate
        elif field == StrategyBacktestField.CandleBarDict:
            return self.StrategyBacktestDTO.CandleBarDict
        elif field == StrategyBacktestField.MarketDataDict:
            return self.StrategyBacktestDTO.MarketDataDict
        elif field == StrategyBacktestField.ModelParametersDict:
            return self.StrategyBacktestDTO.ParmDict
        else:
            return None

    #endregion

