using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.Subscription
{
    public class WebSocketSubscribeMessage:WebSocketMessage
    {
        #region Public Static Consts

        public static string _SUSBSCRIPTION_TYPE_SUBSCRIBE = "S";

        public static string _SUSBSCRIPTION_TYPE_UNSUBSCRIBE = "U";

        #endregion

        #region Public Attributes

        public string SubscriptionType { get; set; }

        public string UUID { get; set; }

        public string Service { get; set; }

        public string ServiceKey { get; set; }

        #endregion
    }
}
