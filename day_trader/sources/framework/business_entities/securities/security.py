from sources.framework.common.enums.SecurityType import SecurityType
from sources.framework.business_entities.market_data.market_data import *


class Security:
    def __init__(self, Symbol=None, Exchange=None,Currency=None, SecType=None):

        #region Attributes
        self.Symbol=Symbol
        self.SecurityDesc = Symbol
        self.Exchange= Exchange
        self.Currency=Currency
        self.SecurityType=SecType
        self.MarketData = MarketData()

        #endregion