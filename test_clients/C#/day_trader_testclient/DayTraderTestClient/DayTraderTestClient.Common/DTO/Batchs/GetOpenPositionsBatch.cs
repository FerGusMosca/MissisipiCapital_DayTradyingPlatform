using DayTraderTestClient.Common.DTO.positions;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DayTraderTestClient.Common.DTO.batchs
{
    public class GetOpenPositionsBatch : WebSocketMessage
    {
        public PositionDTO[] Positions { get; set; }
    }
}
