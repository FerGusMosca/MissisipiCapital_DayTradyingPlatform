using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO
{
    public class UnknownMessage: WebSocketMessage
    {
        public string Resp { get; set; }

        public string Reason { get; set; }
    }
}
