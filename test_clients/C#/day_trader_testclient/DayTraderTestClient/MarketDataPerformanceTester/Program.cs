using MarketDataPerformanceTester.Common;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MarketDataPerformanceTester
{
    class Program
    {

        #region Private Static Consts

        private static string _BLOOMBERG_PREFIX = "At Bloomberg Order Router";

        private static string _BLOOMBERG_CANDLEBAR_ENTRY = "Publishing candle bar";

        private static string _BLOOMBERG_MARKETDATA_ENTRY = "Publishing market data for symbol";

        private static string _DAYTRADER_INPUT_MARKET_DATA = "At DayTrader Recv MarketData";

        private static string _DAYTRADER_OUTPUT_MARKET_DATA = "At DayTrader Proc MarketData";

        private static string _DAYTRADER_INPUT_CANDLEBAR = "At DayTrader Recv Candlebar";

        private static string _DAYTRADER_OUTPUT_CANDLEBAR = "At DayTrader Processed Candlebar";

        

        #endregion

        #region Private Static Attributes

        protected static DateTime DateToProcess { get; set; }

        public static Queue<MarketDataEvent> BloombergEvents { get; set; }

        public static Queue<MarketDataEvent> DayTraderInputEvents { get; set; }

        public static Queue<MarketDataEvent> DayTraderOutputEvents { get; set; }

        #endregion


        #region Private Static Methods

        private static void DoLog(string message)
        {
            Console.WriteLine(message);
        }

        private static void Initialize()
        {
            BloombergEvents = new Queue<MarketDataEvent>();
            DayTraderInputEvents = new Queue<MarketDataEvent>();
            DayTraderOutputEvents = new Queue<MarketDataEvent>();
        
        }

        private static DateTime GetDateFromTime(DateTime baseDate,string time)
        {
            DateTime parsed = DateTime.Parse(time);
            int hour = int.Parse(parsed.ToString("HH"));
            int min = int.Parse(parsed.ToString("mm"));
            int sec = int.Parse(parsed.ToString("ss"));
           
            return new DateTime(baseDate.Year, baseDate.Month, baseDate.Day, hour, min,sec);
        }

        private static MarketDataEvent ExtractCandleBarEvent(string line)
        {
            string strEventTime = line.Substring(0, 19);
            string strCandleBarMarketTime = line.Substring(line.IndexOf("Time=") + "Time=".Length, 8);

            DateTime eventTime = DateTime.ParseExact(strEventTime, "yyyy-MM-dd HH:mm:ss",CultureInfo.InvariantCulture);
            DateTime candleBarMarketTime = GetDateFromTime(eventTime.Date, strCandleBarMarketTime);

            MarketDataEvent cbEvent = new MarketDataEvent() { Type = MarketDataEvent._CANDLEBAR_EVENT, EventTime = eventTime, MarketTime = candleBarMarketTime };

            if (DateTime.Compare(eventTime.Date, DateToProcess.Date) == 0)
                return cbEvent;
            else
                return null;
        
        }

        private static MarketDataEvent ExtractMarketDataEvent(string line)
        {
       

            string strEventTime = line.Substring(0, 19);
            DateTime eventTime = DateTime.ParseExact(strEventTime, "yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture);

            //ex: Timestamp=2020-04-23 17:07:58.030564
            string strMarketDataMarketTime = line.Substring(line.IndexOf("Timestamp=") + "Timestamp=".Length, 19);

            DateTime? marketDataMarketTime = null;

            if (!strMarketDataMarketTime.Contains("?"))
                 marketDataMarketTime = DateTime.ParseExact(strMarketDataMarketTime, "yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture);

            MarketDataEvent mdEvent = new MarketDataEvent()
            {
                Type = MarketDataEvent._MARKET_DATA_EVENT,
                EventTime = eventTime,
                MarketTime = marketDataMarketTime
            };


            if (DateTime.Compare(eventTime.Date, DateToProcess.Date) == 0)
                return mdEvent;
            else
                return null;

        }

        private static void ProcessLine(string line,string type)
        {
            if (line.Contains("DayTrader  Initializing"))
            {
                BloombergEvents.Clear();
                DayTraderInputEvents.Clear();
                DayTraderOutputEvents.Clear();

            }
            else if (line.Contains(_BLOOMBERG_PREFIX) && line.Contains(_BLOOMBERG_CANDLEBAR_ENTRY))
            {
                if (type == MarketDataEvent._CANDLEBAR_EVENT)
                {
                    MarketDataEvent ev = ExtractCandleBarEvent(line);
                    if (ev != null)
                        BloombergEvents.Enqueue(ev);
                }
            
            }
            else if (line.Contains(_BLOOMBERG_PREFIX) && line.Contains(_BLOOMBERG_MARKETDATA_ENTRY))
            {
                if (type == MarketDataEvent._MARKET_DATA_EVENT)
                {
                    MarketDataEvent ev = ExtractMarketDataEvent(line);
                    if(ev!=null)
                        BloombergEvents.Enqueue(ev);
                }
            }
            else if (line.Contains(_DAYTRADER_INPUT_MARKET_DATA))
            {
                if (type == MarketDataEvent._MARKET_DATA_EVENT)
                {
                    MarketDataEvent ev = ExtractMarketDataEvent(line);
                    if (ev != null)
                        DayTraderInputEvents.Enqueue(ev);
                }
            
            }
            else if (line.Contains(_DAYTRADER_INPUT_CANDLEBAR))
            {
                if (type == MarketDataEvent._CANDLEBAR_EVENT)
                {
                    MarketDataEvent ev = ExtractCandleBarEvent(line);
                    if (ev != null)
                        DayTraderInputEvents.Enqueue(ev);
                }
            }
            else if (line.Contains(_DAYTRADER_OUTPUT_MARKET_DATA))
            {
                if (type == MarketDataEvent._MARKET_DATA_EVENT)
                {
                    MarketDataEvent ev = ExtractMarketDataEvent(line);
                    if (ev != null)
                        DayTraderOutputEvents.Enqueue(ev);
                }
            }
            else if (line.Contains(_DAYTRADER_OUTPUT_CANDLEBAR))
            {
                if (type == MarketDataEvent._CANDLEBAR_EVENT)
                {
                    MarketDataEvent ev = ExtractCandleBarEvent(line);
                    if (ev != null)
                        DayTraderOutputEvents.Enqueue(ev);
                }
            }
        }

        private static void ImplementLogicDelayValidation(int procThreshold,MarketDataEvent bloombergEvent,
                                                          MarketDataEvent dayTraderInputEvent, MarketDataEvent dayTraderOutputEvent)
        {
            try
            {
                TimeSpan elapsed1 = dayTraderInputEvent.EventTime - bloombergEvent.EventTime;
                TimeSpan elapsed2 = dayTraderOutputEvent.EventTime - dayTraderInputEvent.EventTime;

                if (elapsed1.TotalMilliseconds > procThreshold)
                    DoLog(string.Format("Event processing time took more than {0} milliseconds between Bloomberg and DayTrader", elapsed1.TotalMilliseconds));

                if (elapsed2.TotalMilliseconds > procThreshold)
                    DoLog(string.Format("Event processing time  took more than {0} milliseconds between Daytrader in and DayTrader out", elapsed2.TotalMilliseconds));
            }
            catch (Exception ex)
            {
                DoLog(string.Format("Could not process event validation because of error:{0}", ex.Message));
            }
        }

        private static void ImplementMarketDelayValidation(int procThreshold, MarketDataEvent bloombergEvent)
        {
            try
            {

                if (bloombergEvent.MarketTime.HasValue)
                {
                    TimeSpan elapsed = bloombergEvent.EventTime - bloombergEvent.MarketTime.Value;

                    if (elapsed.TotalMilliseconds > procThreshold)
                        DoLog(string.Format("Market arrival time  took more than {0} milliseconds from Bloomberg platform", elapsed.TotalMilliseconds));
                }
            }
            catch (Exception ex)
            {
                DoLog(string.Format("Could not process event validation because of error:{0}", ex.Message));
            }
        }


        private static void ProcessResults(int procThreshold)
        {
            DoLog(string.Format("Starting to process {0} results... ", BloombergEvents.Count));
            while (BloombergEvents.Count > 0)
            {
                MarketDataEvent bloombergEvent = BloombergEvents.Dequeue();
                MarketDataEvent dayTraderInputEvent = DayTraderInputEvents.Dequeue();
                MarketDataEvent dayTraderOutputEvent = DayTraderOutputEvents.Dequeue();

                //Validation 1- One even cannot be processed in less than procThreshold
                ImplementLogicDelayValidation(procThreshold, bloombergEvent, dayTraderInputEvent, dayTraderOutputEvent);

                //Validation 2- Events cannot arrive later than marketDelaySpan
                ImplementMarketDelayValidation(procThreshold, bloombergEvent);
            }
            DoLog("Results Successfully Processed");
        }

        #endregion


        static void Main(string[] args)
        {

            string inputFile = ConfigurationManager.AppSettings["InputFile"];
            string type = ConfigurationManager.AppSettings["Type"];
            int procThreshold = Convert.ToInt32(ConfigurationManager.AppSettings["AlarmProcessThresholdInMillisec"]);
            DateToProcess = DateTime.ParseExact(ConfigurationManager.AppSettings["DateToProcess"], "yyyy-MM-dd", CultureInfo.InvariantCulture);

            Initialize();

            DoLog(string.Format("Starting to process file {0} for event types {1}", inputFile, type));


            using (FileStream fs = File.Open(inputFile, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
            {
                using (BufferedStream bs = new BufferedStream(fs))
                {
                    using (StreamReader sr = new StreamReader(bs))
                    {
                        string line;
                        DoLog("Starting to read lines...");
                        while ((line = sr.ReadLine()) != null)
                        {
                            ProcessLine(line,type);
                        }
                        DoLog(string.Format("{0} lines read", BloombergEvents.Count));
                    }
                }
            }  

      

            ProcessResults(procThreshold);
            DoLog("Validation completed...");
            Console.ReadKey();
        }
    }
}
