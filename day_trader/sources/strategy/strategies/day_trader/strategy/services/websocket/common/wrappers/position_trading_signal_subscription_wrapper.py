from sources.framework.common.wrappers.wrapper import Wrapper
from sources.framework.common.enums.Actions import *
from sources.framework.common.enums.fields.position_trading_signal_subscription_field import *

class PositionTradingSignalSubscriptionWrapper(Wrapper):
    def __init__(self, portfPosId,pSubscribe):
        self.PortfPosId =portfPosId
        self.Subscribe=pSubscribe

    # region Public Methods

    def GetAction(self):
        return Actions.POSITION_TRADING_SIGNAL_SUBSCRIPTION

    def GetField(self, field):
        if field == PositionTradingSignalSubscriptionField.PositionId :
            return int( self.PortfPosId)
        if field == PositionTradingSignalSubscriptionField.Subscribe:
            return self.Subscribe
        else:
            return None

    # endregion