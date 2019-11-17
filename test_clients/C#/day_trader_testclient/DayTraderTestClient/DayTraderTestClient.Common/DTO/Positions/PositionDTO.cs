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

        public bool IsOpen { get; set; }

        public decimal? CurrentMarketPrice { get; set; }
    }
}
