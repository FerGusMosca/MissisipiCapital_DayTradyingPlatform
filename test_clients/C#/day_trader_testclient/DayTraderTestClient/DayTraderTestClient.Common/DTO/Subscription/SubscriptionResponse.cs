using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.Subscription
{
    public class SubscriptionResponse : WebSocketMessage
    {
        public string Service { get; set; }

        public string UUID { get; set; }

        public string ServiceKey { get; set; }

        public bool Success { get; set; }

        public string Message { get; set; }
    }
}
