import blpapi
from blpapi import SessionOptions, Session
from sources.framework.business_entities.orders.order import *
from sources.framework.common.enums.TimeInForce import *
from sources.framework.common.enums.OrdType import *
from sources.framework.common.enums.ExecType import *
from sources.framework.common.enums.OrdStatus import *
from sources.framework.common.enums.SecurityType import *
from sources.framework.common.logger.message_type import MessageType
import datetime
from datetime import timedelta

_NEW_STATUS = "NEW"
_SENT_STATUS = "SENT"
_WORKING_STATUS = "WORKING"
_PARTFILL_STATUS = "PARTFILL"
_FILLED_STATUS = "FILLED"
_CANCEL_REQ_STATUS = "CXLREQ"
_CANCEL_PEND_STATUS = "CXLPEN"
_CANCEL_STATUS = "CANCEL"
_MODIFY_REQ_STATUS = "CXLRPRQ"
_MODIFY_PEND_REQ_STATUS = "REPPEN"
_MODIFY_STATUS = "MODIFIED"
_REJECTED_STATUS = "REJECTED"
_COMPLETED_STATUS = "COMPLETED"
_EXPIRED_STATUS = "EXPIRED"
_ASSIGN_STATUS = "ASSIGN"
_CXL_PEND_STATUS = "CXL-PEND"
_MOD_PEND_STATUS = "MOD-PEND"
_PARTFILLED_STATUS = "PARTFILLED"
_CANCEL_REJECTED = "CXLREJ"
_REPLACED = "CXLREP"
_CANCEL_REPLACE_REJECTED = "CXLRPRJ"
_ROUTE_ERR_STATUS = "ROUTE-ERR"

_SIDE_BUY="BUY"
_SIDE_BUY_TO_CLOSE="COVR"
_SIDE_SELL="SELL"
_SIDE_SELL_SHORT="SHRT"
_ORD_TYPE_MKT="MKT"
_ORD_TYPE_LMT="LMT"
_TIF_DAY="DAY"
_BLOOMBERG_FILLS_PREFIX = "EMSX_FILL_"

_DEFAULT_EXCHANGE = "US"
_CS_SECURITY_TYPE="Equity"

_TIME_ZONE=0

class BloombergTranslationHelper:

    @staticmethod
    def Init(pTimeZone=None):
        global _TIME_ZONE
        if pTimeZone is not None:
            _TIME_ZONE=pTimeZone


    @staticmethod
    def GetFillId(self, msg):

        try:
            if (msg.hasElement("EMSX_FILL_ID") and msg.getElementAsString("EMSX_FILL_ID")!="0"):
                now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                fillId = _BLOOMBERG_FILLS_PREFIX + now.strftime("%m/%d/%Y") + "_" + msg.getElementAsString("EMSX_FILL_ID")
                return fillId
            else:
                return None
        except Exception as e:
            self.DoLog("Received empty fill id", MessageType.DEBUG)
            return None

    @staticmethod
    def GetTimeFromDate(self, msg,keyDate,keyTime):

        if (BloombergTranslationHelper.GetSafeInt(self,msg,keyDate,0)!=0 \
            and BloombergTranslationHelper.GetSafeInt(self,msg,keyTime,0)!=0 ):
            try:
                intDate = msg.getElementAsInteger(keyDate)
                strYear =  str(intDate)[:4]
                strMonth = str ( intDate)[4:-2]
                strDay = str(intDate)[6:]
                date = datetime.datetime(year=int(strYear),month=int(strMonth),day=int(strDay))

                secondsFromDate = msg.getElementAsInteger(keyTime)
                timestamp = date + timedelta(seconds=secondsFromDate)
                return timestamp
            except Exception as e:
                self.DoLog("Invalid format for date:{}".format(strDay), MessageType.ERROR)
                return None
        else:
            return None


    @staticmethod
    def GetTimeFromEpoch(self, msg, key):

        secondsFromToday = msg.getElementAsInteger(key)
        now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        timestamp = now + timedelta(seconds=secondsFromToday)
        return timestamp

    @staticmethod
    def GetCleanSymbol(logger, msg):
        try:
            EMSX_TICKER = msg.getElementAsString("EMSX_TICKER")

            symbolFields = EMSX_TICKER.split(" ")

            if (len(symbolFields)>0):
                return symbolFields[0]
            else:
                return ""
        except Exception as e:
            return ""

    @staticmethod
    def GetSide(self,msg):

        try:

            EMSX_SIDE= msg.getElementAsString("EMSX_SIDE")

            if EMSX_SIDE==_SIDE_BUY:
                return Side.Buy
            elif EMSX_SIDE==_SIDE_SELL:
                return  Side.Sell
            elif EMSX_SIDE==_SIDE_BUY_TO_CLOSE:
                return  Side.BuyToClose
            elif EMSX_SIDE==_SIDE_SELL_SHORT:
                return  Side.SellShort
            else:
                self.DoLog("Received unknown side:{}".format(EMSX_SIDE), MessageType.DEBUG)
                return Side.Unknown
        except Exception as e:
            self.DoLog("Received empty side", MessageType.DEBUG)
            return Side.Unknown

    @staticmethod
    def GetBloombergOrdType(self, ordType):

        if ordType == OrdType.Limit:
            return _ORD_TYPE_LMT
        elif ordType == OrdType.Market:
            return _ORD_TYPE_MKT
        else:

            raise Exception("Bloomberg order type not supported:{}".format(ordType))

    @staticmethod
    def GetBloombergSide(self, side):

        if side == Side.Buy:
            return _SIDE_BUY
        elif side == Side.BuyToClose:
            return _SIDE_BUY_TO_CLOSE
        elif side == Side.Sell:
            return _SIDE_SELL
        elif side == Side.SellShort:
            return _SIDE_SELL_SHORT
        else:
            raise Exception("Bloomberg side not suppoerted:{}".format(side))

    @staticmethod
    def GetOrdType(self, msg):

        try:
            EMSX_ORDER_TYPE = msg.getElementAsString("EMSX_ORDER_TYPE")

            if EMSX_ORDER_TYPE == _ORD_TYPE_MKT:
                return OrdType.Market
            elif EMSX_ORDER_TYPE == _ORD_TYPE_LMT:
                return OrdType.Limit
            else:
                self.DoLog("Received unknown order type from Bloomberg:{}".format(EMSX_ORDER_TYPE), MessageType.DEBUG)
                return OrdType.Market
        except Exception as e:
            self.DoLog("Received empty order type from Bloomberg", MessageType.DEBUG)
            return OrdType.Market

    @staticmethod
    def GetTIF(self, msg):

        EMSX_TIF=None
        try:

            EMSX_TIF = msg.getElementAsString("EMSX_TIF")

            if EMSX_TIF == _TIF_DAY:
                return TimeInForce.Day
            else:
                self.DoLog("Received unknown time in force from Bloomberg:{}".format(EMSX_TIF),MessageType.DEBUG)
                return TimeInForce.Day
        except Exception as e:
            self.DoLog("Received unknown time in force from Bloomberg:{}".format(EMSX_TIF), MessageType.DEBUG)
            return TimeInForce.Day


    @staticmethod
    def GetExecType(self,msg):

        EMSX_STATUS=None
        try:

            if not msg.hasElement("EMSX_STATUS"):
                return ExecType.Unknown

            EMSX_STATUS = msg.getElementAsString("EMSX_STATUS")

            if EMSX_STATUS == _SENT_STATUS:
                return ExecType.PendingNew
            elif EMSX_STATUS == _NEW_STATUS:
                return ExecType.New
            elif EMSX_STATUS == _WORKING_STATUS:
                return ExecType.New
            elif EMSX_STATUS == _PARTFILL_STATUS:
                return ExecType.Trade
            elif EMSX_STATUS == _FILLED_STATUS:
                return ExecType.Trade
            elif EMSX_STATUS == _PARTFILLED_STATUS:
                return ExecType.Trade
            elif EMSX_STATUS == _CANCEL_REQ_STATUS:
                return ExecType.PendingCancel
            elif EMSX_STATUS == _CANCEL_PEND_STATUS:
                return ExecType.PendingCancel
            elif EMSX_STATUS == _CANCEL_STATUS:
                return ExecType.Canceled
            elif EMSX_STATUS == _ASSIGN_STATUS:
                return ExecType.Canceled
            elif EMSX_STATUS == _MODIFY_REQ_STATUS:
                return ExecType.PendingReplace
            elif EMSX_STATUS == _MODIFY_PEND_REQ_STATUS:
                return ExecType.PendingReplace
            elif EMSX_STATUS == _MODIFY_STATUS:
                return ExecType.Replaced
            elif EMSX_STATUS == _REJECTED_STATUS:
                return ExecType.Rejected
            elif EMSX_STATUS == _COMPLETED_STATUS:
                return ExecType.Trade
            elif EMSX_STATUS == _EXPIRED_STATUS:
                return ExecType.Expired
            elif EMSX_STATUS == _CXL_PEND_STATUS:
                return ExecType.PendingCancel
            elif EMSX_STATUS == _MOD_PEND_STATUS:
                return ExecType.PendingReplace
            elif EMSX_STATUS == _CANCEL_REJECTED:
                return ExecType.Rejected
            elif EMSX_STATUS == _CANCEL_REPLACE_REJECTED:
                return ExecType.Rejected
            elif EMSX_STATUS == _REPLACED:
                return ExecType.Replaced
            elif EMSX_STATUS == _ROUTE_ERR_STATUS:
                return ExecType.Rejected

            else:
                self.DoLog("Received unknown status from Bloomberg:{}".format(EMSX_STATUS if EMSX_STATUS is not None else "?"),MessageType.DEBUG)
                return ExecType.Unknown
                #raise Exception("Bloomberg Execution Report. Unknown EMSX_STATUS {}".format(EMSX_STATUS))
        except Exception as e:
            self.DoLog("Received unknown status from Bloomberg:{}".format(EMSX_STATUS if EMSX_STATUS is not None else "?"), MessageType.DEBUG)
            return ExecType.Unknown

    @staticmethod
    def GetSafeFloat(self,msg,key ,default):

        try:
            if msg.hasElement(key):
                return  msg.getElementAsFloat(key)
            else:
                return default

        except Exception as e:
            self.DoLog("GetSafeFloat from Bloomberg error:{}".format(str(e)), MessageType.DEBUG)
            return default

    @staticmethod
    def GetSafeInt(self, msg, key, default):

        try:
            if msg.hasElement(key):
                return msg.getElementAsInteger(key)
            else:
                return default

        except Exception as e:
            self.DoLog("GetSafeInt from Bloomberg error:{}".format(str(e)), MessageType.DEBUG)
            return default

    @staticmethod
    def GetSafeString(self, msg, key, default):

        try:
            if msg.hasElement(key):
                return msg.getElementAsString(key)
            else:
                return default

        except Exception as e:
            self.DoLog("GetSafeString from Bloomberg error:{}".format(str(e)), MessageType.DEBUG)
            return default

    @staticmethod
    def GetSafeDateTime(self, msg, key, default,implTimeZone=True):

        try:
            if msg.hasElement(key):
                dateTime=msg.getElementAsDatetime(key)
                if implTimeZone:

                    dateTime = dateTime + timedelta(hours=_TIME_ZONE if _TIME_ZONE is not None else 0)

                return dateTime
            else:
                return default

        except Exception as e:
            self.DoLog("GetSafeDateTime from Bloomberg error:{}".format(str(e)), MessageType.DEBUG)
            return default


    @staticmethod
    def GetOrdStatus(self,msg):

        EMSX_STATUS=None
        try:

            if not msg.hasElement("EMSX_STATUS"):
                return OrdStatus.Undefined

            EMSX_STATUS= msg.getElementAsString("EMSX_STATUS")

            if EMSX_STATUS == _SENT_STATUS:
                return OrdStatus.PendingNew
            elif EMSX_STATUS == _NEW_STATUS:
                return OrdStatus.New
            elif EMSX_STATUS == _WORKING_STATUS:
                return OrdStatus.New
            elif EMSX_STATUS == _PARTFILL_STATUS:
                return OrdStatus.PartiallyFilled
            elif EMSX_STATUS == _PARTFILLED_STATUS:
                return OrdStatus.PartiallyFilled
            elif EMSX_STATUS == _FILLED_STATUS:
                return OrdStatus.Filled
            elif EMSX_STATUS == _CANCEL_REQ_STATUS:
                return OrdStatus.PendingCancel
            elif EMSX_STATUS == _CANCEL_PEND_STATUS:
                return OrdStatus.PendingCancel
            elif EMSX_STATUS == _CANCEL_STATUS:
                return OrdStatus.Canceled
            elif EMSX_STATUS == _ASSIGN_STATUS:
                return OrdStatus.Canceled
            elif EMSX_STATUS == _MODIFY_REQ_STATUS:
                return OrdStatus.PendingReplace
            elif EMSX_STATUS == _MODIFY_PEND_REQ_STATUS:
                return OrdStatus.PendingReplace
            elif EMSX_STATUS == _MODIFY_STATUS:
                return OrdStatus.Replaced
            elif EMSX_STATUS == _REJECTED_STATUS:
                return OrdStatus.Rejected
            elif EMSX_STATUS == _COMPLETED_STATUS:
                return OrdStatus.Filled
            elif EMSX_STATUS == _EXPIRED_STATUS:
                return OrdStatus.Expired
            elif EMSX_STATUS == _CXL_PEND_STATUS:
                return OrdStatus.PendingCancel
            elif EMSX_STATUS == _MOD_PEND_STATUS:
                return OrdStatus.PendingReplace
            elif EMSX_STATUS == _CANCEL_REJECTED:
                return OrdStatus.Undefined
            elif EMSX_STATUS == _CANCEL_REPLACE_REJECTED:
                return OrdStatus.Undefined
            elif EMSX_STATUS == _REPLACED:
                return OrdStatus.Replaced
            elif EMSX_STATUS == _ROUTE_ERR_STATUS:
                return OrdStatus.Rejected
            else:
                self.DoLog("Received unknown status from Bloomberg:{}".format(EMSX_STATUS if EMSX_STATUS is not None else "?"),MessageType.DEBUG)
                return OrdStatus.Undefined
                #raise Exception("Bloomberg Execution Report. Unknown EMSX_STATUS {}".format(EMSX_STATUS))
        except Exception as e:
            self.DoLog("Received unknown status from Bloomberg:{}".format(EMSX_STATUS if EMSX_STATUS is not None else "?"), MessageType.DEBUG)
            return OrdStatus.Undefined

    @staticmethod
    def GetCleanStrSymbol(logger, dirtySymbol):

        symbolFields = dirtySymbol.split(" ")

        if (len(symbolFields) == 3):
            return symbolFields[0]
        else:
            return ""

    @staticmethod
    def GetCleanSecType(logger,dirtySymbol):

        symbolFields = dirtySymbol.split(" ")

        if (len(symbolFields) ==3 ):
            return symbolFields[2]
        else:
            return ""

    @staticmethod
    def GetCleanExchange(logger,dirtySymbol):

        symbolFields = dirtySymbol.split(" ")

        if (len(symbolFields) == 3):
            return symbolFields[1]
        else:
            return ""


    @staticmethod
    def GetBloombergExchange(exch):
        if exch is not None:
            return exch
        else:
            return _DEFAULT_EXCHANGE

    @staticmethod
    def GetBloombergSecType(secType):
        if secType == SecurityType.CS:
            return _CS_SECURITY_TYPE
        else:
            raise Exception("Bloomberg Translation not implemented for sec type {}".format(secType))

    @staticmethod
    def GetSecType(blSecType):
        if blSecType == _CS_SECURITY_TYPE:
            return  SecurityType.CS
        else:
            SecurityType.OTH


