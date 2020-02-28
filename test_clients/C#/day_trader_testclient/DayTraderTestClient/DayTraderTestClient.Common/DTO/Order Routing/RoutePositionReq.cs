using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.Order_Routing
{
    public class RoutePositionReq : WebSocketMessage
    {
        #region Public Attributes

        public string UUID { get; set; }

        public string ReqId { get; set; }

        public string Symbol { get; set; }

        public int? PosId { get; set; }

        public string Side { get; set; }

        public int Qty { get; set; }

        public string Account { get; set; }

        public decimal? Price { get; set; }

        public decimal? StopLoss { get; set; }

        public decimal? TakeProfit { get; set; }

        public bool? CloseEndOfDay { get; set; }

        #endregion
    }
}
