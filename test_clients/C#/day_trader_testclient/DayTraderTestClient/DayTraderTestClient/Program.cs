using DayTraderTestClient.Common.DTO;
using DayTraderTestClient.Common.DTO.batchs;
using DayTraderTestClient.Common.DTO.Config;
using DayTraderTestClient.Common.DTO.Market_Data;
using DayTraderTestClient.Common.DTO.Order_Routing;
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
            Console.WriteLine("RouteSymbolReq <symbol> <side> <qty> <account>");
            Console.WriteLine("RoutePositionReq <posId> <side> <qty> <account>");
            Console.WriteLine("HistoricalPricesReq <symbol>");
            Console.WriteLine("CancelPos <posId>");
            Console.WriteLine("CancelAll");
            Console.WriteLine("UpdateModelParamReq <key> <symbol> <intValue> <stringValue> <floatValue>");
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

        private static void ProcessHistoricalPricesReq(string[] param)
        {
            if (param.Length == 2)
            {
                HistoricalPricesReq histPricesReq = new HistoricalPricesReq()
                {
                    Msg = "HistoricalPricesReq",
                    Symbol = param[1],
                    To=DateTime.Now.Date,
                    From = DateTime.Now.Date.AddDays(-5),
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
            if (param.Length == 5)
            {
                RoutePositionReq routePos = new RoutePositionReq()
                {
                    Msg = "RouteSymbolReq",
                    Symbol = param[1],
                    Side = param[2],
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                    Qty = Convert.ToInt32(param[3]),
                    Account = param[4]
                };

                DoSend<RoutePositionReq>(routePos);
            }
            else
                DoLog(string.Format("Missing mandatory parameters for RoutePositionReq message"));
        
        }

        private static void ProcessRoutePositionReq(string[] param)
        {
            if (param.Length == 5)
            {
                RoutePositionReq routePos = new RoutePositionReq()
                {
                    Msg = "RoutePositionReq",
                    PosId = Convert.ToInt32(param[1]),
                    Side = param[2],
                    UUID = UUID,
                    ReqId = Guid.NewGuid().ToString(),
                    Qty = Convert.ToInt32(param[3]),
                    Account = param[4]
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
            else if (mainCmd == "UpdateModelParamReq")
            {
                ProcessUpdateModelParamReq(param);
            }
            else if (mainCmd == "RoutePositionReq")
            {
                ProcessRoutePositionReq(param);
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
