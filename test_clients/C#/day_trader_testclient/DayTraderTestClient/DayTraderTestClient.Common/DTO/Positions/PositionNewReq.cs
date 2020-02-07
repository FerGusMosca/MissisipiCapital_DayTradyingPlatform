using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.Positions
{
    public class PositionNewReq : WebSocketMessage
    {
        #region Public Attributes

        public string UUID { get; set; }

        public string ReqId { get; set; }

        public string Symbol { get; set; }

        public string SecurityType { get; set; }

        public string Exchange { get; set; }


        #endregion
    }
}
