class StrategyBacktestDto:

    def __init__(self,pReferenceDate,pSecurity,pCandleBarDict,pMarketDataDict,pParamDict):
        self.Security=pSecurity
        self.ReferenceDate=pReferenceDate
        self.CandleBarDict = pCandleBarDict
        self.MarketDataDict = pMarketDataDict
        self.ParmDict = pParamDict
