using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.Market_Data
{
    public class HistoricalPricesReq : WebSocketMessage
    {

        #region Public Attributes

        public string UUID { get; set; }

        public string ReqId { get; set; }

        public string Symbol { get; set; }

        public DateTime From { get; set; }

        public DateTime To { get; set; }


        #endregion
    }
}
