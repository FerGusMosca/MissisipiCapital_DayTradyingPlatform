from enum import Enum


class Actions(Enum):
    MARKET_DATA = 1
    MARKET_DATA_REQUEST = 2
    ORDER_BOOK = 3
    OFFER = 4
    EXECUTION_REPORT = 5
    NEW_POSITION = 6
    SECURITY = 7
    NEW_POSITION_CANCELED = 8
    NEW_ORDER = 9
    UPDATE_ORDER = 10
    CANCEL_ORDER = 11
    CANCEL_POSITION = 12
    CANCEL_ALL_POSITIONS = 13
    SECURITY_LIST = 14
    SECURITY_LIST_REQUEST = 15
    ORDER_CANCEL_REJECT = 16
    BUSINESS_MESSAGE_REJECT = 17
    ORDER_LIST = 18
    ORDER_LIST_REQUEST = 19
    POSITION_LIST = 20
    POSITION_LIST_REQUEST=21
    EXECUTION_REPORT_LIST_REQUEST=22
    EXECUTION_REPORT_LIST = 23,
    CANDLE_BAR_REQUEST=24
    CANDLE_BAR_DATA = 25
    HISTORICAL_PRICES_REQUEST = 26
    HISTORICAL_PRICES = 27
    ERROR=99
