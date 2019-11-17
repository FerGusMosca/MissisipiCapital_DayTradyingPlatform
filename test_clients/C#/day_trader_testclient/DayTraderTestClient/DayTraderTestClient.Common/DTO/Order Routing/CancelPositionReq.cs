using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.Order_Routing
{
    public class CancelPositionReq : WebSocketMessage
    {
        #region Public Attributes

        public string UUID { get; set; }

        public string ReqId { get; set; }

        public int PosId { get; set; }

        #endregion
    }
}
