import blpapi
from blpapi import SessionOptions, Session
from sources.order_routers.bloomberg.common.util.bloomberg_translation_helper import *
from sources.framework.business_entities.orders.order import *
from sources.framework.business_entities.orders.execution_report import *
from sources.framework.common.enums.TimeInForce import *
from sources.framework.common.enums.OrdType import *

orderSubscriptionID=blpapi.CorrelationId(98)
routeSubscriptionID=blpapi.CorrelationId(99)


class SubscriptionHelper:

    @staticmethod
    def CreateOrderSubscription(self, service, session):

        # orderTopic = d_service + "/order;team=TKTEAM?fields="
        orderTopic = service + "/order?fields="
        orderTopic = orderTopic + "API_SEQ_NUM,"
        orderTopic = orderTopic + "EMSX_ACCOUNT,"
        orderTopic = orderTopic + "EMSX_AMOUNT,"
        orderTopic = orderTopic + "EMSX_ARRIVAL_PRICE,"
        orderTopic = orderTopic + "EMSX_ASSET_CLASS,"
        orderTopic = orderTopic + "EMSX_ASSIGNED_TRADER,"
        orderTopic = orderTopic + "EMSX_AVG_PRICE,"
        orderTopic = orderTopic + "EMSX_BASKET_NAME,"
        orderTopic = orderTopic + "EMSX_BASKET_NUM,"
        orderTopic = orderTopic + "EMSX_BLOCK_ID,"
        orderTopic = orderTopic + "EMSX_BROKER,"
        orderTopic = orderTopic + "EMSX_BROKER_COMM,"
        orderTopic = orderTopic + "EMSX_BSE_AVG_PRICE,"
        orderTopic = orderTopic + "EMSX_BSE_FILLED,"
        orderTopic = orderTopic + "EMSX_BUYSIDE_LEI,"
        orderTopic = orderTopic + "EMSX_CFD_FLAG,"
        orderTopic = orderTopic + "EMSX_CLIENT_IDENTIFICATION,"
        orderTopic = orderTopic + "EMSX_COMM_DIFF_FLAG,"
        orderTopic = orderTopic + "EMSX_COMM_RATE,"
        orderTopic = orderTopic + "EMSX_CUSTOM_NOTE1,"
        orderTopic = orderTopic + "EMSX_CUSTOM_NOTE2,"
        orderTopic = orderTopic + "EMSX_CUSTOM_NOTE3,"
        orderTopic = orderTopic + "EMSX_CUSTOM_NOTE4,"
        orderTopic = orderTopic + "EMSX_CUSTOM_NOTE5,"
        orderTopic = orderTopic + "EMSX_CURRENCY_PAIR,"
        orderTopic = orderTopic + "EMSX_DATE,"
        orderTopic = orderTopic + "EMSX_DAY_AVG_PRICE,"
        orderTopic = orderTopic + "EMSX_DAY_FILL,"
        orderTopic = orderTopic + "EMSX_DIR_BROKER_FLAG,"
        orderTopic = orderTopic + "EMSX_EXCHANGE,"
        orderTopic = orderTopic + "EMSX_EXCHANGE_DESTINATION,"
        orderTopic = orderTopic + "EMSX_EXEC_INSTRUCTION,"
        orderTopic = orderTopic + "EMSX_FILL_ID,"
        orderTopic = orderTopic + "EMSX_FILLED,"
        orderTopic = orderTopic + "EMSX_GPI,"
        orderTopic = orderTopic + "EMSX_GTD_DATE,"
        orderTopic = orderTopic + "EMSX_HAND_INSTRUCTION,"
        orderTopic = orderTopic + "EMSX_IDLE_AMOUNT,"
        orderTopic = orderTopic + "EMSX_INVESTOR_ID,"
        orderTopic = orderTopic + "EMSX_ISIN,"
        orderTopic = orderTopic + "EMSX_LIMIT_PRICE,"
        orderTopic = orderTopic + "EMSX_MIFID_II_INSTRUCTION,"
        orderTopic = orderTopic + "EMSX_MOD_PEND_STATUS,"
        orderTopic = orderTopic + "EMSX_NOTES,"
        orderTopic = orderTopic + "EMSX_NSE_AVG_PRICE,"
        orderTopic = orderTopic + "EMSX_NSE_FILLED,"
        orderTopic = orderTopic + "EMSX_ORD_REF_ID,"
        orderTopic = orderTopic + "EMSX_ORDER_AS_OF_DATE,"
        orderTopic = orderTopic + "EMSX_ORDER_AS_OF_TIME_MICROSEC,"
        orderTopic = orderTopic + "EMSX_ORDER_TYPE,"
        orderTopic = orderTopic + "EMSX_ORIGINATE_TRADER,"
        orderTopic = orderTopic + "EMSX_ORIGINATE_TRADER_FIRM,"
        orderTopic = orderTopic + "EMSX_PERCENT_REMAIN,"
        orderTopic = orderTopic + "EMSX_PM_UUID,"
        orderTopic = orderTopic + "EMSX_PORT_MGR,"
        orderTopic = orderTopic + "EMSX_PORT_NAME,"
        orderTopic = orderTopic + "EMSX_PORT_NUM,"
        orderTopic = orderTopic + "EMSX_POSITION,"
        orderTopic = orderTopic + "EMSX_PRINCIPAL,"
        orderTopic = orderTopic + "EMSX_PRODUCT,"
        orderTopic = orderTopic + "EMSX_QUEUED_DATE,"
        orderTopic = orderTopic + "EMSX_QUEUED_TIME,"
        orderTopic = orderTopic + "EMSX_QUEUED_TIME_MICROSEC,"
        orderTopic = orderTopic + "EMSX_REASON_CODE,"
        orderTopic = orderTopic + "EMSX_REASON_DESC,"
        orderTopic = orderTopic + "EMSX_REMAIN_BALANCE,"
        orderTopic = orderTopic + "EMSX_ROUTE_ID,"
        orderTopic = orderTopic + "EMSX_ROUTE_PRICE,"
        orderTopic = orderTopic + "EMSX_SEC_NAME,"
        orderTopic = orderTopic + "EMSX_SEDOL,"
        orderTopic = orderTopic + "EMSX_SEQUENCE,"
        orderTopic = orderTopic + "EMSX_SETTLE_AMOUNT,"
        orderTopic = orderTopic + "EMSX_SETTLE_DATE,"
        orderTopic = orderTopic + "EMSX_SI,"
        orderTopic = orderTopic + "EMSX_SIDE,"
        orderTopic = orderTopic + "EMSX_START_AMOUNT,"
        orderTopic = orderTopic + "EMSX_STATUS,"
        orderTopic = orderTopic + "EMSX_STEP_OUT_BROKER,"
        orderTopic = orderTopic + "EMSX_STOP_PRICE,"
        orderTopic = orderTopic + "EMSX_STRATEGY_END_TIME,"
        orderTopic = orderTopic + "EMSX_STRATEGY_PART_RATE1,"
        orderTopic = orderTopic + "EMSX_STRATEGY_PART_RATE2,"
        orderTopic = orderTopic + "EMSX_STRATEGY_START_TIME,"
        orderTopic = orderTopic + "EMSX_STRATEGY_STYLE,"
        orderTopic = orderTopic + "EMSX_STRATEGY_TYPE,"
        orderTopic = orderTopic + "EMSX_TICKER,"
        orderTopic = orderTopic + "EMSX_TIF,"
        orderTopic = orderTopic + "EMSX_TIME_STAMP,"
        orderTopic = orderTopic + "EMSX_TIME_STAMP_MICROSEC,"
        orderTopic = orderTopic + "EMSX_TRAD_UUID,"
        orderTopic = orderTopic + "EMSX_TRADE_DESK,"
        orderTopic = orderTopic + "EMSX_TRADER,"
        orderTopic = orderTopic + "EMSX_TRADER_NOTES,"
        orderTopic = orderTopic + "EMSX_TS_ORDNUM,"
        orderTopic = orderTopic + "EMSX_TYPE,"
        orderTopic = orderTopic + "EMSX_UNDERLYING_TICKER,"
        orderTopic = orderTopic + "EMSX_USER_COMM_AMOUNT,"
        orderTopic = orderTopic + "EMSX_USER_COMM_RATE,"
        orderTopic = orderTopic + "EMSX_USER_FEES,"
        orderTopic = orderTopic + "EMSX_USER_NET_MONEY,"
        orderTopic = orderTopic + "EMSX_WORK_PRICE,"
        orderTopic = orderTopic + "EMSX_WORKING,"
        orderTopic = orderTopic + "EMSX_YELLOW_KEY"

        subscriptions = blpapi.SubscriptionList()

        subscriptions.add(topic=orderTopic, correlationId=orderSubscriptionID)

        session.subscribe(subscriptions)

    @staticmethod
    def CreateRouteSubscription(self, service ,session):

        # routeTopic = d_service + "/route;team=EMSX_API?fields="
        routeTopic = service + "/route?fields="
        routeTopic = routeTopic + "API_SEQ_NUM,"
        routeTopic = routeTopic + "EMSX_AMOUNT,"
        routeTopic = routeTopic + "EMSX_APA_MIC,"
        routeTopic = routeTopic + "EMSX_AVG_PRICE,"
        routeTopic = routeTopic + "EMSX_BROKER,"
        routeTopic = routeTopic + "EMSX_BROKER_COMM,"
        routeTopic = routeTopic + "EMSX_BROKER_LEI,"
        routeTopic = routeTopic + "EMSX_BROKER_SI,"
        routeTopic = routeTopic + "EMSX_BSE_AVG_PRICE,"
        routeTopic = routeTopic + "EMSX_BSE_FILLED,"
        routeTopic = routeTopic + "EMSX_BROKER_STATUS,"
        routeTopic = routeTopic + "EMSX_BUYSIDE_LEI,"
        routeTopic = routeTopic + "EMSX_CLEARING_ACCOUNT,"
        routeTopic = routeTopic + "EMSX_CLEARING_FIRM,"
        routeTopic = routeTopic + "EMSX_CLIENT_IDENTIFICATION,"
        routeTopic = routeTopic + "EMSX_COMM_DIFF_FLAG,"
        routeTopic = routeTopic + "EMSX_COMM_RATE,"
        routeTopic = routeTopic + "EMSX_CURRENCY_PAIR,"
        routeTopic = routeTopic + "EMSX_CUSTOM_ACCOUNT,"
        routeTopic = routeTopic + "EMSX_DAY_AVG_PRICE,"
        routeTopic = routeTopic + "EMSX_DAY_FILL,"
        routeTopic = routeTopic + "EMSX_EXCHANGE_DESTINATION,"
        routeTopic = routeTopic + "EMSX_EXEC_INSTRUCTION,"
        routeTopic = routeTopic + "EMSX_EXECUTE_BROKER,"
        routeTopic = routeTopic + "EMSX_FILL_ID,"
        routeTopic = routeTopic + "EMSX_FILLED,"
        routeTopic = routeTopic + "EMSX_GPI,"
        routeTopic = routeTopic + "EMSX_GTD_DATE,"
        routeTopic = routeTopic + "EMSX_HAND_INSTRUCTION,"
        routeTopic = routeTopic + "EMSX_IS_MANUAL_ROUTE,"
        routeTopic = routeTopic + "EMSX_LAST_CAPACITY,"
        routeTopic = routeTopic + "EMSX_LAST_FILL_DATE,"
        routeTopic = routeTopic + "EMSX_LAST_FILL_TIME,"
        routeTopic = routeTopic + "EMSX_LAST_FILL_TIME_MICROSEC,"
        routeTopic = routeTopic + "EMSX_LAST_MARKET,"
        routeTopic = routeTopic + "EMSX_LAST_PRICE,"
        routeTopic = routeTopic + "EMSX_LAST_SHARES,"
        routeTopic = routeTopic + "EMSX_LEG_FILL_DATE_ADDED,"
        routeTopic = routeTopic + "EMSX_LEG_FILL_PRICE,"
        routeTopic = routeTopic + "EMSX_LEG_FILL_SEQ_NO,"
        routeTopic = routeTopic + "EMSX_LEG_FILL_SHARES,"
        routeTopic = routeTopic + "EMSX_LEG_FILL_SIDE,"
        routeTopic = routeTopic + "EMSX_LEG_FILL_TICKER,"
        routeTopic = routeTopic + "EMSX_LEG_FILL_TIME_ADDED,"
        routeTopic = routeTopic + "EMSX_LIMIT_PRICE,"
        routeTopic = routeTopic + "EMSX_MIFID_II_INSTRUCTION,"
        routeTopic = routeTopic + "EMSX_MISC_FEES,"
        routeTopic = routeTopic + "EMSX_ML_ID,"
        routeTopic = routeTopic + "EMSX_ML_LEG_QUANTITY,"
        routeTopic = routeTopic + "EMSX_ML_NUM_LEGS,"
        routeTopic = routeTopic + "EMSX_ML_PERCENT_FILLED,"
        routeTopic = routeTopic + "EMSX_ML_RATIO,"
        routeTopic = routeTopic + "EMSX_ML_REMAIN_BALANCE,"
        routeTopic = routeTopic + "EMSX_ML_STRATEGY,"
        routeTopic = routeTopic + "EMSX_ML_TOTAL_QUANTITY,"
        routeTopic = routeTopic + "EMSX_NOTES,"
        routeTopic = routeTopic + "EMSX_NSE_AVG_PRICE,"
        routeTopic = routeTopic + "EMSX_NSE_FILLED,"
        routeTopic = routeTopic + "EMSX_ORDER_TYPE,"
        routeTopic = routeTopic + "EMSX_OTC_FLAG,"
        routeTopic = routeTopic + "EMSX_P_A,"
        routeTopic = routeTopic + "EMSX_PERCENT_REMAIN,"
        routeTopic = routeTopic + "EMSX_PRINCIPAL,"
        routeTopic = routeTopic + "EMSX_QUEUED_DATE,"
        routeTopic = routeTopic + "EMSX_QUEUED_TIME,"
        routeTopic = routeTopic + "EMSX_QUEUED_TIME_MICROSEC,"
        routeTopic = routeTopic + "EMSX_REASON_CODE,"
        routeTopic = routeTopic + "EMSX_REASON_DESC,"
        routeTopic = routeTopic + "EMSX_REMAIN_BALANCE,"
        routeTopic = routeTopic + "EMSX_ROUTE_AS_OF_DATE,"
        routeTopic = routeTopic + "EMSX_ROUTE_AS_OF_TIME_MICROSEC,"
        routeTopic = routeTopic + "EMSX_ROUTE_CREATE_DATE,"
        routeTopic = routeTopic + "EMSX_ROUTE_CREATE_TIME,"
        routeTopic = routeTopic + "EMSX_ROUTE_CREATE_TIME_MICROSEC,"
        routeTopic = routeTopic + "EMSX_ROUTE_ID,"
        routeTopic = routeTopic + "EMSX_ROUTE_LAST_UPDATE_TIME,"
        routeTopic = routeTopic + "EMSX_ROUTE_LAST_UPDATE_TIME_MICROSEC,"
        routeTopic = routeTopic + "EMSX_ROUTE_PRICE,"
        routeTopic = routeTopic + "EMSX_ROUTE_REF_ID,"
        routeTopic = routeTopic + "EMSX_SEQUENCE,"
        routeTopic = routeTopic + "EMSX_SETTLE_AMOUNT,"
        routeTopic = routeTopic + "EMSX_SETTLE_DATE,"
        routeTopic = routeTopic + "EMSX_STATUS,"
        routeTopic = routeTopic + "EMSX_STOP_PRICE,"
        routeTopic = routeTopic + "EMSX_STRATEGY_END_TIME,"
        routeTopic = routeTopic + "EMSX_STRATEGY_PART_RATE1,"
        routeTopic = routeTopic + "EMSX_STRATEGY_PART_RATE2,"
        routeTopic = routeTopic + "EMSX_STRATEGY_START_TIME,"
        routeTopic = routeTopic + "EMSX_STRATEGY_STYLE,"
        routeTopic = routeTopic + "EMSX_STRATEGY_TYPE,"
        routeTopic = routeTopic + "EMSX_TIF,"
        routeTopic = routeTopic + "EMSX_TIME_STAMP,"
        routeTopic = routeTopic + "EMSX_TIME_STAMP_MICROSEC,"
        routeTopic = routeTopic + "EMSX_TRADE_REPORTING_INDICATOR,"
        routeTopic = routeTopic + "EMSX_TRANSACTION_REPORTING_MIC,"
        routeTopic = routeTopic + "EMSX_TYPE,"
        routeTopic = routeTopic + "EMSX_URGENCY_LEVEL,"
        routeTopic = routeTopic + "EMSX_USER_COMM_AMOUNT,"
        routeTopic = routeTopic + "EMSX_USER_COMM_RATE,"
        routeTopic = routeTopic + "EMSX_USER_FEES,"
        routeTopic = routeTopic + "EMSX_USER_NET_MONEY,"
        routeTopic = routeTopic + "EMSX_WAIVER_FLAG,"
        routeTopic = routeTopic + "EMSX_WORKING"

        subscriptions = blpapi.SubscriptionList()

        subscriptions.add(topic=routeTopic, correlationId=routeSubscriptionID)

        session.subscribe(subscriptions)

    @staticmethod
    def BuildOrder(self, msg):
        order = Order(ClOrdId="",
                      Security=Security(
                          Symbol=BloombergTranslationHelper.GetCleanSymbol(self,msg),
                          Exchange=BloombergTranslationHelper.GetSafeString(self, msg, "EMSX_EXCHANGE", None),
                          Currency=BloombergTranslationHelper.GetSafeString(self, msg, "EMSX_CURRENCY_PAIR", None),
                      ),
                      SettlType=SettlType.Regular,
                      Side=BloombergTranslationHelper.GetSide(self,msg),
                      Exchange=BloombergTranslationHelper.GetSafeString(self, msg, "EMSX_EXCHANGE", None),
                      OrdType=BloombergTranslationHelper.GetOrdType(self,msg),
                      QuantityType=QuantityType.SHARES,
                      OrderQty=BloombergTranslationHelper.GetSafeFloat(self, msg, "EMSX_AMOUNT", 0),
                      PriceType=PriceType.FixedAmount,
                      Price=BloombergTranslationHelper.GetSafeFloat(self, msg, "EMSX_LIMIT_PRICE", None),
                      StopPx=BloombergTranslationHelper.GetSafeFloat(self, msg, "EMSX_STOP_PRICE", None),
                      Currency=BloombergTranslationHelper.GetSafeString(self, msg, "EMSX_CURRENCY_PAIR", None),
                      TimeInForce=BloombergTranslationHelper.GetTIF(self,msg),
                      Account=BloombergTranslationHelper.GetSafeString(self, msg, "EMSX_ACCOUNT", None),
                      Broker=BloombergTranslationHelper.GetSafeString(self, msg, "EMSX_BROKER", None),
                      OrdStatus=BloombergTranslationHelper.GetOrdStatus(self,msg)
                      )

        order.OrderId=msg.getElementAsString("EMSX_SEQUENCE")
        return order

    @staticmethod
    def BuildExecutionReport(self, msg):

        execReport= ExecutionReport(
                        TransactTime=BloombergTranslationHelper.GetTimeFromEpoch(self, msg,"EMSX_ROUTE_LAST_UPDATE_TIME_MICROSEC"),
                        ExecType=BloombergTranslationHelper.GetExecType(self, msg),
                        ExecId=BloombergTranslationHelper.GetFillId(self, msg),
                        OrdStatus=BloombergTranslationHelper.GetOrdStatus(self, msg),
                        Order = Order(ClOrdId="",OrderQty= msg.getElementAsFloat("EMSX_AMOUNT")),
                        LastQty=BloombergTranslationHelper.GetSafeFloat(self,msg,"EMSX_LAST_SHARES",None),
                        LastPx=BloombergTranslationHelper.GetSafeFloat(self, msg, "EMSX_LAST_PRICE", None),
                        LastMkt=BloombergTranslationHelper.GetSafeString(self, msg, "EMSX_LAST_MARKET", None),
                        LeavesQty=None,
                        #LeavesQty=BloombergTranslationHelper.GetSafeFloat(self, msg, "LeavesQty", 0),
                        CumQty=BloombergTranslationHelper.GetSafeFloat(self, msg, "EMSX_FILLED", 0),
                        AvgPx=BloombergTranslationHelper.GetSafeFloat(self, msg, "EMSX_AVG_PRICE", None),
                        Commission=BloombergTranslationHelper.GetSafeFloat(self, msg, "EMSX_BROKER_COMM", None),
                        Text=BloombergTranslationHelper.GetSafeString(self, msg, "EMSX_REASON_DESC", None),
                        ArrivalPrice=BloombergTranslationHelper.GetSafeFloat(self, msg, "EMSX_ARRIVAL_PRICE", None)
        )

        execReport.LeavesQty= execReport.Order.OrderQty - execReport.CumQty

        execReport.Order.OrderId=BloombergTranslationHelper.GetSafeString(self,msg,"EMSX_SEQUENCE",None)

        return execReport