from sources.framework.common.enums.Side import *

_BUY="BUY"
_BUY_TO_CLOSE="BUY_TO_CLOSE"
_SELL="SELL"
_SELL_SHORT="SELL_SHORT"
class SideConverter:

    @staticmethod
    def ConvertSideToString(side):
        if side==Side.Buy:
            return _BUY
        elif side==Side.BuyToClose:
            return _BUY_TO_CLOSE
        elif side==Side.Sell:
            return _SELL
        elif side==Side.SellShort:
            return _SELL_SHORT
        else:
            return ""

