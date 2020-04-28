using DayTraderTestClient.Common.DTO;
using DayTraderTestClient.Common.DTO.batchs;
using DayTraderTestClient.Common.DTO.Subscription;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace DayTraderTestClient.DataAccessLayer
{
    public delegate void ProcessEvent(WebSocketMessage msg);

    public class WebSocketClient
    {
        #region Protected Attributes

        protected  StreamWriter Writer { get; set; }

        protected string WebSocketURL { get; set; }

        protected ProcessEvent OnEvent { get; set; }

        protected ClientWebSocket SubscriptionWebSocket { get; set; }

        #endregion

        #region Constructors

        public WebSocketClient(string pWebSocketURL, ProcessEvent pOnEvent)
        {
            WebSocketURL = pWebSocketURL;
            OnEvent = pOnEvent;
            Writer = new StreamWriter("log.txt");
            DoLog("Starting DayTraderTestClient...");
        
        }


        #endregion

        #region Protected Methods

        private  void DoLog(string txt)
        {
            if (Writer != null)
            {
                Writer.WriteLine(txt);
                Writer.Flush();
            }
        }

        #endregion

        #region Public Methods

        public async Task<bool> Connect()
        {

            SubscriptionWebSocket = new ClientWebSocket();
            await SubscriptionWebSocket.ConnectAsync(new Uri(WebSocketURL), CancellationToken.None);

            Thread respThread = new Thread(ReadResponses);
            respThread.Start(new object[] { });
            return true;
        }

        public virtual async void ReadResponses(object param)
        {
            while (true)
            {
                try
                {
                    string resp = "";
                    WebSocketReceiveResult webSocketResp;
                    if (SubscriptionWebSocket.State == WebSocketState.Open)
                    {
                        do
                        {
                            ArraySegment<byte> bytesReceived = new ArraySegment<byte>(new byte[1000]);
                            webSocketResp = await SubscriptionWebSocket.ReceiveAsync(bytesReceived, CancellationToken.None);
                            resp += Encoding.ASCII.GetString(bytesReceived.Array, 0, webSocketResp.Count);
                        }
                        while (!webSocketResp.EndOfMessage);

                        DoLog(string.Format("@{0}:{1}", DateTime.Now, resp));
                        DoLog("");


                        if (resp != "")
                        {
                            WebSocketMessage wsResp = JsonConvert.DeserializeObject<WebSocketMessage>(resp);

                            if (wsResp.Msg == "SubscriptionResponse")
                            {
                                SubscriptionResponse subscrResponse = JsonConvert.DeserializeObject<SubscriptionResponse>(resp);
                                OnEvent(subscrResponse);
                            }
                            else if (wsResp.Msg == "GetOpenPositionsBatch")
                            {
                                GetOpenPositionsBatch getOpenPositionsBatch = JsonConvert.DeserializeObject<GetOpenPositionsBatch>(resp);
                                OnEvent(getOpenPositionsBatch);

                            }//
                           
                            else
                            {

                                UnknownMessage unknownMsg = new UnknownMessage()
                                {
                                    Msg = "UnknownMsg",
                                    Resp = resp,
                                    Reason = string.Format("Unknown message: {0}", resp)
                                };
                                OnEvent(unknownMsg);
                            }
                        }
                    }
                    else
                        Thread.Sleep(100);
                }
                catch (Exception ex)
                {
                    ErrorMessage errorMsg = new ErrorMessage() { Msg = "ErrorMsg", Error = ex.Message };
                    OnEvent(errorMsg);
                }
            }
        }

        public async void Send(string strMsg)
        {
            byte[] msgArray = Encoding.ASCII.GetBytes(strMsg);

            ArraySegment<byte> bytesToSend = new ArraySegment<byte>(msgArray);

            await SubscriptionWebSocket.SendAsync(bytesToSend, WebSocketMessageType.Text, true,
                                                          CancellationToken.None);

        }

        #endregion
    }
}
