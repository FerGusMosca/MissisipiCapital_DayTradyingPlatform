from sources.framework.common.enums.Side import *
from sources.framework.common.enums.OrdType import *
from sources.framework.common.enums.TimeInForce import *
from sources.framework.common.enums.OrdStatus import *
from sources.strategy.strategies.day_trader.common.util.csv_constants import *


class CSVConverters:

    @staticmethod
    def ConvertStringSide(self, side):
        """
        Args:
            side ():

        Returns:

        """
        # B - Buy, S - Sell close, SS - Sell short, BS - Buy to close,
        if side == Side.Buy :
            return CSVConstants._SIDE_BUY(self)
        elif side == Side.Sell :
            return CSVConstants._SIDE_SELL_CLOSE(self)
        elif side == Side.SellShort :
            return CSVConstants._SIDE_SELL_SHORT(self)
        elif side == Side.BuyToClose :
            return CSVConstants._SIDE_BUY_TO_CLOSE(self)
        else:
            raise Exception("Unknown side {}".format(side))

    @staticmethod
    def ConvertSide(self, csvSide):
        """

        Args:
            csvSide ():

        Returns:

        """
        # B - Buy, S - Sell close, SS - Sell short, BS - Buy to close,
        if csvSide == CSVConstants._SIDE_BUY(self):
            return Side.Buy
        elif csvSide == CSVConstants._SIDE_SELL_CLOSE(self):
            return Side.Sell
        elif csvSide == CSVConstants._SIDE_SELL_SHORT(self):
            return Side.SellShort
        elif csvSide == CSVConstants._SIDE_BUY_TO_CLOSE(self):
            return Side.BuyToClose
        else:
            raise Exception("Unknown csv side {}".format(csvSide))

    @staticmethod
    def ConvertStringOrdType(self, ordType):
        """
        Args:
            ordType ():

        Returns:

        """
        if ordType == OrdType.Limit:
            return CSVConstants._ORD_TYPE_LIMIT(self)
        elif ordType == OrdType.Market:
            return CSVConstants._ORD_TYPE_MARKET(self)
        else:
            return "OTH"

    @staticmethod
    def ConvertStringTimeInForce(self, tif):
        """
        Args:
            tif ():

        Returns:

        """
        if tif == TimeInForce.Day:
            return CSVConstants._TIF_DAY(self)
        else:
            return "OTH"

    @staticmethod
    def ConvertStringOrdStatus(self, status):
        """
        Args:
            tif ():

        Returns:

        """
        if status == OrdStatus.New:
            return CSVConstants._ORD_STATUS_NEW(self)
        elif status == OrdStatus.PartiallyFilled:
            return CSVConstants._ORD_STATUS_PARTIALLY_FILLED(self)
        elif status == OrdStatus.Filled:
            return CSVConstants._ORD_STATUS_FILLED(self)
        elif status == OrdStatus.DoneForDay:
            return CSVConstants._ORD_STATUS_DONE_FOR_DAY(self)
        elif status == OrdStatus.Canceled:
            return CSVConstants._ORD_STATUS_CANCELED(self)
        elif status == OrdStatus.PendingCancel:
            return CSVConstants._ORD_STATUS_PENDING_CANCEL(self)
        elif status == OrdStatus.Stopped:
            return CSVConstants._ORD_STATUS_STOPPED(self)
        elif status == OrdStatus.Rejected:
            return CSVConstants._ORD_STATUS_REJECTED(self)
        elif status == OrdStatus.Suspended:
            return CSVConstants._ORD_STATUS_SUSPENDED(self)
        elif status == OrdStatus.PendingNew:
            return CSVConstants._ORD_STATUS_PENDING_NEW(self)
        elif status == OrdStatus.Calculated:
            return CSVConstants._ORD_STATUS_CALCULATED(self)
        elif status == OrdStatus.Expired:
            return CSVConstants._ORD_STATUS_EXPIRED(self)
        elif status == OrdStatus.AcceptedForBidding:
            return CSVConstants._ORD_STATUS_ACCEPTED_FOR_BIDDING(self)
        elif status == OrdStatus.PendingReplace:
            return CSVConstants._ORD_STATUS_PENDING_REPLACE(self)
        elif status == OrdStatus.Replaced:
            return CSVConstants._ORD_STATUS_REPLACED(self)
        elif status == OrdStatus.Undefined:
            return CSVConstants._ORD_STATUS_UNDEFINED(self)
        else:
            return CSVConstants._ORD_STATUS_UNDEFINED(self)


    @staticmethod
    def ConvertOrdType(self, csvOrdType):
        """

        Args:
            csvOrdType ():

        Returns:

        """
        # MKT= Market, LMT - Limit
        if csvOrdType == CSVConstants._ORD_TYPE_MARKET(self):
            return OrdType.Market
        elif csvOrdType == CSVConstants._ORD_TYPE_LIMIT(self):
            return OrdType.Limit
        else:
            raise Exception("Unknown or not implemented order type {}".format(csvOrdType))

    @staticmethod
    def ConvertLimitPrice(self, csvLimitPrice):
        """

        Args:
            csvLimitPrice ():

        Returns:

        """
        if csvLimitPrice is not None and csvLimitPrice.strip() != "":
            try:
                return float(csvLimitPrice)
            except Exception as e:
                raise Exception("Invalid Limit Price: {}".format(csvLimitPrice))
