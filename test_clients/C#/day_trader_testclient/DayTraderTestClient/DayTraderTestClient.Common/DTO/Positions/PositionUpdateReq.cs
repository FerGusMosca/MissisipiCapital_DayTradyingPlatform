using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.Positions
{
    public class PositionUpdateReq : WebSocketMessage
    {
        #region Public Attributes

        public string UUID { get; set; }

        public string ReqId { get; set; }

        public int PosId { get; set; }

        public int? SharesQuantity { get; set; }

        public bool? Active { get; set; }

        public bool? Depurate { get; set; }

        public string TradingMode { get; set; }

        public bool? CleanStopLoss { get; set; }

        public bool? CleanTakeProfit { get; set; }

        public bool? CleanEndOfDay { get; set; }

        #endregion
    }
}
