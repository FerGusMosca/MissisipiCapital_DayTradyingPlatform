using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MarketDataPerformanceTester.Common
{
    public class MarketDataEvent
    {
        #region Public Static Consts

        public static string _MARKET_DATA_EVENT = "MARKET_DATA_EVENT";

        public static string _CANDLEBAR_EVENT = "CANDLEBAR_EVENT";

        #endregion


        #region Public Attributes

        public string Type { get; set; }

        public DateTime? MarketTime { get; set; }

        public DateTime EventTime { get; set; }


        #endregion
    }
}
