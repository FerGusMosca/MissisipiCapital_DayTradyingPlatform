class CSVConstants:

    #region Column Consts

    def _SIMPLE_SYMBOL(self):
        return 0

    def _SIMPLE_QTY(self):
        return 1


    def _EXTENDED_SYMBOL(self):
        return 0

    def _EXTENDED_EXCHANGE(self):
        return 1

    def _EXTENDED_SIDE(self):
        return 2

    def _EXTENDED_QTY(self):
        return 3

    def _EXTENDED_ACCOUNT(self):
        return 4

    def _EXTENDED_ORDER_TYPE(self):
        return 5

    def _EXTENDED_LIMIT_PRICE(self):
        return 6

    def _EXTENDED_BROKER(self):
        return 7

    def _EXTENDED_STRATEGY(self):
        return 8

    #endregion

    #region CSV Side Values

    def _SIDE_BUY(self):
        return "B"

    def _SIDE_SELL_CLOSE(self):
        return "S"

    def _SIDE_SELL_SHORT(self):
        return "SS"

    def _SIDE_BUY_TO_CLOSE(self):
        return "BS"

    #endregion

    # region CSV Order Type Values

    def _ORD_TYPE_MARKET(self):
        return "MKT"

    def _ORD_TYPE_LIMIT(self):
        return "LMT"

    # endregion

    # region CSV Time In Force Values

    def _TIF_DAY(self):
        return "DAY"

    # endregion

    # region CSV Ord Status Values

    def _ORD_STATUS_NEW(self):
        return "NEW"

    def _ORD_STATUS_PARTIALLY_FILLED(self):
        return "PARTIALLY_FILLED"

    def _ORD_STATUS_FILLED(self):
        return "FILLED"

    def _ORD_STATUS_DONE_FOR_DAY(self):
        return "DONE_FOR_DAY"

    def _ORD_STATUS_CANCELED(self):
        return "CANCELED"

    def _ORD_STATUS_PENDING_CANCEL(self):
        return "PENDING_CANCEL"

    def _ORD_STATUS_STOPPED(self):
        return "STOPPED"

    def _ORD_STATUS_REJECTED(self):
        return "REJECTED"

    def _ORD_STATUS_SUSPENDED(self):
        return "SUSPENDED"

    def _ORD_STATUS_PENDING_NEW(self):
        return "PENDING_NEW"

    def _ORD_STATUS_CALCULATED(self):
        return "CALCULATED"

    def _ORD_STATUS_EXPIRED(self):
        return "EXPIRED"

    def _ORD_STATUS_ACCEPTED_FOR_BIDDING(self):
        return "ACCEPTED_FOR_BIDDING"

    def _ORD_STATUS_PENDING_REPLACE(self):
        return "PENDING_REPLACE"

    def _ORD_STATUS_REPLACED(self):
        return "REPLACED"

    def _ORD_STATUS_UNDEFINED(self):
        return "UNDEFINED"

    # endregion