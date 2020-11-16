import configparser


class Configuration:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)

        self.Server = config['DEFAULT']['SERVER']
        self.Port = int(config['DEFAULT']['PORT'])
        self.EMSX_Environment = config['DEFAULT']['EMSX_ENVIRONMENT']
        self.MktBar_Environment = config['DEFAULT']['MKTBAR_ENVIRONMENT']
        self.RefData_Environment = config['DEFAULT']['REF_DATA_ENVIRONMENT']

        self.Exchange = config['DEFAULT']['EXCHANGE']
        self.SecurityType = config['DEFAULT']['SECURITY_TYPE']
        self.DefaultBroker=config['DEFAULT']['DEFAULT_BROKER']
        self.DefaultTIF = config['DEFAULT']['DEFAULT_TIF']

        self.ImplementStrategy = config['DEFAULT']['IMPLEMENT_STRATEGY']
        #self.ImplementStrategy = config['DEFAULT'].getboolean('IMPLEMENT_STRATEGY')
        self.HandInst = config['DEFAULT']['HANDLE_INST']
        self.MaxOrdersPerSecond = int(config['DEFAULT']['MAX_ORDERS_PER_SECOND'])
        self.InitialRecoveryTimeoutInSeconds = int(config['DEFAULT']['INITIAL_RECOVERY_TIMEOUT_IN_SECONDS'])
        self.ImplementMock = config['DEFAULT']['IMPLEMENT_MOCK'] == "True"
        self.SecondsToSleepOnTradeForMock = float(config['DEFAULT']['SECONDS_TO_SLEEP_ON_TRADE_FOR_MOCK'])
        self.MockSendsToBloomberg = config['DEFAULT']['MOCK_SENDS_TO_BLOOMBERG'] == "True"

        self.ExternalOrdersPacingSeconds = int(config['DEFAULT']['EXTERNAL_ORDERS_PACING_SECONDS'])
        self.MarketDataUpdateFreqSeconds = float(config['DEFAULT']['MARKET_DATA_UPDATE_FREQ_SECONDS'])

        self.TimeZone = int(config['DEFAULT']['TIME_ZONE'])








