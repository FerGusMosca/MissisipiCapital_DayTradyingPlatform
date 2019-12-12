using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.positions
{
    public class PositionDTO
    {
        public string Symbol { get; set; }

        public int PositionSize { get; set; }

        public bool IsRouting { get; set; }

        public bool LongSignal { get; set; }

        public bool ShortSignal { get; set; }

        public string SignalType { get; set; }

        public string SignalDesc { get; set; }

        public string IsOpen { get; set; }

        public decimal? CurrentMarketPrice { get; set; }

        public decimal? CurrentProfit { get; set; }

        public decimal? CurrentProfitMonetary { get; set; }

        public decimal? CurrentProfitLastTrade { get; set; }

        public decimal? CurrentProfitMonetaryLastTrade { get; set; }

        public decimal? IncreaseDecrease { get; set; }

        public decimal? MaxProxit { get; set; }

        public decimal? MaxLoss { get; set; }

        public int NetShares { get; set; }

        public string Direction { get; set; }

        public string Msg { get; set; }

    }
}
