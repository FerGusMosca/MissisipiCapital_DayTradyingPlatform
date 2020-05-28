class BacktestDTO:
    def __init__(self, pSymbol,pDate,pTime,pShares,pCurrentProfit):
        self.Symbol=pSymbol
        self.Date=pDate
        self.Time=pTime
        self.Shares=pShares
        self.CurrentProfit=pCurrentProfit