from sources.framework.common.enums.SecurityType import SecurityType


class Security:
    def __init__(self, Symbol=None, Exchange=None,Currency=None):

        #region Attributes
        self.Symbol=Symbol
        self.SecurityDesc = Symbol
        self.Exchange= Exchange
        self.Currency=Currency
        self.SecurityType=SecurityType.CS
        #TODO implement market data entity

        #endregion