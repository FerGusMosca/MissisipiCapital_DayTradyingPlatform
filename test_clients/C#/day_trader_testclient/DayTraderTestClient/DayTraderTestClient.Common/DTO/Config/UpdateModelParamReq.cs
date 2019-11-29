using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.Config
{
    public class UpdateModelParamReq : WebSocketMessage
    {
        #region Public Attributes

        public string UUID { get; set; }

        public string ReqId { get; set; }

        public string Symbol { get; set; }

        public string Key { get; set; }

        public int? IntValue { get; set; }

        public string StringValue { get; set; }

        public decimal? FloatValue { get; set; }

        #endregion
    }
}
