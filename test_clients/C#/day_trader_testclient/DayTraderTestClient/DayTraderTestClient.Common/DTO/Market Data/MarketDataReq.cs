using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.Market_Data
{
    public class MarketDataReq : WebSocketMessage
    {
        #region Public Attributes

        public string UUID { get; set; }

        public string ReqId { get; set; }

        public string Symbol { get; set; }

        #endregion
    }
}
