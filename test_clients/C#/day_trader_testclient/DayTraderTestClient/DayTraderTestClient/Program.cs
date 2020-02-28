using DayTraderTestClient.Common.DTO;
using DayTraderTestClient.Common.DTO.batchs;
using DayTraderTestClient.Common.DTO.Config;
using DayTraderTestClient.Common.DTO.Market_Data;
using DayTraderTestClient.Common.DTO.Order_Routing;
using DayTraderTestClient.Common.DTO.Positions;
using DayTraderTestClient.Common.DTO.Subscription;
using DayTraderTestClient.DataAccessLayer;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient
{
    class Program
    {
        #region Protected Static Attributes

        protected static WebSocketClient WebSocketClient { get; set; }

        protected static string UUID { get; set; }

        #endregion

       


        #region Protected Methods

        private static void DoLog(string message)
        {
            Console.WriteLine(message);
        }

        private static void DoSend<T>(T obj)
        {
            string strMsg = JsonConvert.SerializeObject(obj, Newtonsoft.Json.Formatting.None,
                                                    new JsonSerializerSettings
                                                    {
                                                        NullValueHandling = NullValueHandling.Ignore
                                                    });


            DoLog(string.Format(">>{0}", strMsg));
            WebSocketClient.Send(strMsg);
        }

        private static void ProcessJsonMessage<T>(T msg)
        {

            string strMessage = JsonConvert.SerializeObject(msg, Newtonsoft.Json.Formatting.None,
                                              new JsonSerializerSettings
                                              {
                                                  NullValueHandling = NullValueHandling.Ignore
                                              });
            DoLog(string.Format("<<{0}", strMessage));

        }

        private static void ShowCommands()
        {
            Console.WriteLine();
            Console.WriteLine("-------------- Enter Commands to Invoke -------------- ");
            //Console.WriteLine("LoginClient <userId> <UUID> <Password>");
            //Console.WriteLine("LogoutClient (Cxt credentials will be used)");
            Console.WriteLine("Subscribe <Service> <ServiceKey>");
            Console.WriteLine("RouteSymbolReq <symbol> <side> <qty> <account> <price>");
            Console.WriteLine("RoutePositionReq <posId> <side> <qty> <account>  <price>");
            Console.WriteLine("RoutePositionReqExt <posId> <side> <qty> <account>  <price> <stopLoss> <takeProfit> <CloseEndOfDay>");
            Console.WriteLine("MarketDataReq <symbol>");
            Console.WriteLine("HistoricalPricesReq <symbol>");
            Console.WriteLine("CancelPos <posId>");
            Console.WriteLine("CancelAll");
            Console.WriteLine("ModelParamReq <key> <symbol>");
            Console.WriteLine("PositionNewReq <symbol> <secType> <exchange>");
            Console.WriteLine("PositionUpdateReq <posId> <qty> <active>");
            Console.WriteLine("PositionUpdateReqTradingMode <posId> <tradingMode>");
            Console.WriteLine("DepuratePosition <posId>");
            Console.WriteLine("UpdateModelParamReq <key> <symbol> <intValue> <stringValue> <floatValue>");
            Console.WriteLine("CreateModelParamReq <key> <symbol> <intValue> <stringValue> <floatValue>");
            Console.WriteLine("Unsubscribe <Service> <ServiceKey>");
            Console.WriteLine("-CLEAR");
            Console.WriteLine();

        }

        #endregion

        private static void ProcessSubscribe(string[] param)
        {

            if (param.Length <= 3)
            {
                WebSocketSubscribeMessage subscribe = new WebSocketSubscribeMessage()
                {
                    Msg = "Subscribe",
                    SubscriptionType = WebSocketSubscribeMessage._SUSBSCRIPTION_TYPE_SUBSCRIBE,
                    //JsonWebToken = Token,
                    Service = param[1],
                    ServiceKey = param.Length == 3 ? param[2] : "*",
                    UUID = UUID

                };

                DoSend<WebSocketSubscribeMessage>(subscribe);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for subscription message"));

        }

        private static void ProcessDepuratePosition(string[] param)
        {

            if (param.Length == 2)
            {
                PositionUpdateReq posUpdReq = new PositionUpdateReq()
                {
                    Msg = "PositionUpdateReq",
                    PosId = Convert.ToInt32(param[1]),
                    Depurate = true,
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                };

                DoSend<PositionUpdateReq>(posUpdReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for ProcessDepuratePosition message"));
        }

        private static void ProcessPositionNewReq(string[] param)
        {
            if (param.Length == 4)
            {
                PositionNewReq posNewReq = new PositionNewReq()
                {
                    Msg = "PositionNewReq",
                    Symbol = param[1],
                    SecurityType = param[2],
                    Exchange = param[3],
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                };

                DoSend<PositionNewReq>(posNewReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for PositionNewReq message"));

        }

        private static void ProcessPositionUpdateReqTradingMode(string[] param)
        {
            if (param.Length == 3)
            {
                PositionUpdateReq posUpdReq = new PositionUpdateReq()
                {
                    Msg = "PositionUpdateReq",
                    PosId = Convert.ToInt32(param[1]),
                    TradingMode = param[2],
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                };

                DoSend<PositionUpdateReq>(posUpdReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for ProcessPositionUpdateReqTradingMode message"));
        
        }

        private static void ProcessPositionUpdateReq(string[] param)
        {
            if (param.Length == 4)
            {
                PositionUpdateReq posUpdReq = new PositionUpdateReq()
                {
                    Msg = "PositionUpdateReq",
                    PosId = Convert.ToInt32(param[1]),
                    SharesQuantity = param[2] != "*" ? (int?)Convert.ToInt32(param[2]) : null,
                    Active = param[3] != "*" ? (bool?)Convert.ToBoolean(param[3]) : null,
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                };

                DoSend<PositionUpdateReq>(posUpdReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for PositionUpdateReq message"));
        
        }

        private static void ProcessMarketDataReq(string[] param)
        {
            if (param.Length == 2)
            {
                MarketDataReq marketDataReq = new MarketDataReq()
                {
                    Msg = "MarketDataReq",
                    Symbol = param[1],
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                };

                DoSend<MarketDataReq>(marketDataReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for MarketDataReq message"));
        }

        private static void ProcessHistoricalPricesReq(string[] param)
        {
            if (param.Length == 2)
            {
                HistoricalPricesReq histPricesReq = new HistoricalPricesReq()
                {
                    Msg = "HistoricalPricesReq",
                    Symbol = param[1],
                    To=DateTime.Now.Date,
                    From = DateTime.Now.Date.AddDays(-7),
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                };

                DoSend<HistoricalPricesReq>(histPricesReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for HistoricalPricesReq message"));

        
        }

        private static void ProcessCancelPos(string[] param)
        {

            if (param.Length == 2)
            {
                CancelPositionReq routePos = new CancelPositionReq()
                {
                    Msg = "CancelPositionReq",
                    PosId = Convert.ToInt32(param[1]),
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                };

                DoSend<CancelPositionReq>(routePos);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for CancelPositionReq message"));

        }

        private static void ProcessCancelAll(string[] param)
        {

            if (param.Length == 1)
            {
                CancelAllPositionReq cancelAllReq = new CancelAllPositionReq()
                {
                    Msg = "CancelAllPositionReq",
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                };

                DoSend<CancelAllPositionReq>(cancelAllReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for CancelAllPositionReq message"));

        }

        private static void ProcessModelParamReq(string[] param)
        {
            if (param.Length == 3)
            {
                ModelParamReq paramReq = new ModelParamReq()
                {
                    Msg = "ModelParamReq",
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                    Key = param[1],
                    Symbol = param[2] != "*" ? param[2] : null,
                };

                DoSend<ModelParamReq>(paramReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for ModelParamReq message"));
        
        }

        //
        private static void ProcessCreateModelParamReq(string[] param)
        {

            if (param.Length == 6)
            {
                CreateModelParamReq createParamReq = new CreateModelParamReq()
                {
                    Msg = "CreateModelParamReq",
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                    Key = param[1],
                    Symbol = param[2] != "*" ? param[2] : null,
                    IntValue = param[3] != "*" ? (int?)Convert.ToInt32(param[3]) : null,
                    StringValue = param[4] != "*" ? param[4] : null,
                    FloatValue = param[5] != "*" ? (decimal?)Convert.ToDecimal(param[5]) : null
                };

                DoSend<CreateModelParamReq>(createParamReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for CreateModelParamReq message"));

        }

        private static void ProcessUpdateModelParamReq(string[] param)
        {

            if (param.Length == 6)
            {
                UpdateModelParamReq updParamReq = new UpdateModelParamReq()
                {
                    Msg = "UpdateModelParamReq",
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                    Key = param[1],
                    Symbol = param[2] != "*" ? param[2] : null,
                    IntValue = param[3] != "*" ? (int?)Convert.ToInt32(param[3]) : null,
                    StringValue = param[4] != "*" ? param[4] : null,
                    FloatValue = param[5] != "*" ? (decimal?)Convert.ToDecimal(param[5]) : null
                };

                DoSend<UpdateModelParamReq>(updParamReq);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for UpdateModelParamReq message"));
        
        }

        private static void ProcessRouteSymbolReq(string[] param)
        {
            if (param.Length == 6)
            {
                RoutePositionReq routePos = new RoutePositionReq()
                {
                    Msg = "RouteSymbolReq",
                    Symbol = param[1],
                    Side = param[2],
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                    Qty = Convert.ToInt32(param[3]),
                    Account = param[4],
                    Price = param[5] != "*" ? (decimal?)Convert.ToDecimal(param[5]) : null
                };

                DoSend<RoutePositionReq>(routePos);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for RoutePositionReq message"));
        
        }

        private static void ProcessRoutePositionReqExt(string[] param)
        {
            if (param.Length == 9)
            {
                RoutePositionReq routePos = new RoutePositionReq()
                {
                    Msg = "RoutePositionReq",
                    PosId = Convert.ToInt32(param[1]),
                    Side = param[2],
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                    Qty = Convert.ToInt32(param[3]),
                    Account = param[4],
                    Price = param[5] != "*" ? (decimal?)Convert.ToDecimal(param[5]) : null,
                    StopLoss= Convert.ToDecimal(param[6]),
                    TakeProfit = Convert.ToDecimal(param[7]),
                    CloseEndOfDay=Convert.ToBoolean(param[8]),
                };

                DoSend<RoutePositionReq>(routePos);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for ProcessRoutePositionReqExt message"));

        }

        private static void ProcessRoutePositionReq(string[] param)
        {
            if (param.Length == 6)
            {
                RoutePositionReq routePos = new RoutePositionReq()
                {
                    Msg = "RoutePositionReq",
                    PosId = Convert.ToInt32(param[1]),
                    Side = param[2],
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                    Qty = Convert.ToInt32(param[3]),
                    Account = param[4],
                    Price = param[5] != "*" ? (decimal?)Convert.ToDecimal(param[5]) : null
                };

                DoSend<RoutePositionReq>(routePos);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for RoutePositionReq message"));

        }

        private static void ProcessUnsubscribe(string[] param)
        {
            if (param.Length <= 3)
            {
                WebSocketSubscribeMessage subscribe = new WebSocketSubscribeMessage()
                {
                    Msg = "Subscribe",
                    SubscriptionType = WebSocketSubscribeMessage._SUSBSCRIPTION_TYPE_UNSUBSCRIBE,
                    //JsonWebToken = Token,
                    Service = param[1],
                    ServiceKey = param.Length == 3 ? param[2] : "*",
                    UUID = UUID

                };

                DoSend<WebSocketSubscribeMessage>(subscribe);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for subscription message"));

        }

        private static void ProcessCommand(string cmd)
        {

            string[] param = cmd.Split(new string[] { " " }, StringSplitOptions.RemoveEmptyEntries);

            string mainCmd = param[0];

            if (mainCmd == "Subscribe")
            {
                ProcessSubscribe(param);
            }
            else if (mainCmd == "RouteSymbolReq")
            {
                ProcessRouteSymbolReq(param);
            }
            else if (mainCmd == "ModelParamReq")
            {
                ProcessModelParamReq(param);
            }
            else if (mainCmd == "UpdateModelParamReq")
            {
                ProcessUpdateModelParamReq(param);
            }
            else if (mainCmd == "CreateModelParamReq")
            {
                ProcessCreateModelParamReq(param);
            }
            else if (mainCmd == "RoutePositionReq")
            {
                ProcessRoutePositionReq(param);
            }
            else if (mainCmd == "RoutePositionReqExt")
            {
                ProcessRoutePositionReqExt(param);
            }
            else if (mainCmd == "CancelAll")
            {
                ProcessCancelAll(param);
            }
            else if (mainCmd == "CancelPos")
            {
                ProcessCancelPos(param);
            }
            else if (mainCmd == "HistoricalPricesReq")
            {
                ProcessHistoricalPricesReq(param);
            }
            else if (mainCmd == "MarketDataReq")
            {
                ProcessMarketDataReq(param);
            }
            else if (mainCmd == "PositionUpdateReq")
            {
                ProcessPositionUpdateReq(param);
            }
            else if (mainCmd == "PositionUpdateReqTradingMode")
            {
                ProcessPositionUpdateReqTradingMode(param);
            }
            else if (mainCmd == "PositionNewReq")
            {
                ProcessPositionNewReq(param);
            }
            else if (mainCmd == "DepuratePosition")
            {
                ProcessDepuratePosition(param);
            }
            else if (mainCmd == "Unsubscribe")
            {
                ProcessUnsubscribe(param);
            }
            else if (mainCmd.ToUpper() == "CLEAR")
            {
                Console.Clear();
                ShowCommands();
            }
            else
                DoLog(string.Format("Unknown command {0}", mainCmd));
        }

        private static void ProcessEvent(WebSocketMessage msg)
        {


            if (msg is SubscriptionResponse)
                ProcessJsonMessage<SubscriptionResponse>((SubscriptionResponse)msg);
            else if (msg is GetOpenPositionsBatch)
                ProcessJsonMessage<GetOpenPositionsBatch>((GetOpenPositionsBatch)msg);
            else if (msg is UnknownMessage)
            {
                UnknownMessage unknownMsg = (UnknownMessage)msg;

                DoLog(string.Format("<<<{0}", unknownMsg.Resp));

            }
            else if (msg is ErrorMessage)
            {
                ErrorMessage errorMsg = (ErrorMessage)msg;

                DoLog(string.Format("<<error {0}", errorMsg.Error));

            }
            else
                DoLog(string.Format("<<Unknown message type {0}", msg.ToString()));

            Console.WriteLine();

        }

        static void Main(string[] args)
        {
            try
            {
                string WebSocketURL = ConfigurationManager.AppSettings["WebSocketURL"];

                WebSocketClient = new WebSocketClient(WebSocketURL, ProcessEvent);

                DoLog(string.Format("Connecting to URL {0}", WebSocketURL));
                WebSocketClient.Connect();
                DoLog("Successfully connected");

                ShowCommands();

                while (true)
                {
                    string cmd = Console.ReadLine();
                    ProcessCommand(cmd);
                    Console.WriteLine();
                }
            }
            catch (Exception ex)
            {
                DoLog(string.Format("Critical Error: {0}", ex.Message));
                Console.ReadKey();

            }

        }
    }
}
