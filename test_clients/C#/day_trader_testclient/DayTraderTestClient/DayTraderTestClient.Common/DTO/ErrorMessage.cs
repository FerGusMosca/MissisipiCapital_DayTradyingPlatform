using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO
{
    public class ErrorMessage : WebSocketMessage
    {
        public string Error { get; set; }
    }
}
