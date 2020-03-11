import configparser

class Configuration:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)

        self.IncomingModule = config['DEFAULT']['INCOMING_MODULE']
        self.IncomingConfigFile = config['DEFAULT']['INCOMING_CONFIG_FILE']
        self.OutgoingModule = config['DEFAULT']['OUTGOING_MODULE']
        self.OutgoingConfigFile = config['DEFAULT']['OUTGOING_CONFIG_FILE']
        self.Currency = config['DEFAULT']['CURRENCY']
        self.PauseBeforeExecutionInSeconds = int( config['DEFAULT']['PAUSE_BEFORE_EXECUTION_IN_SECONDS'])
        self.DefaultExchange= config['DEFAULT']['DEFAULT_EXCHANGE']
        self.MarketDataSubscriptionResetTime = config['DEFAULT']['MARKET_DATA_SUBSCRIPTION_RESET_TIME']
        self.DefaultAccount = config['DEFAULT']['DEFAULT_ACCOUNT']
        self.ImplementDetailedSides = bool(config['DEFAULT']['IMPLEMENT_DETAILED_SIDES'])
        self.TestMode = bool(config['DEFAULT']['TEST_MODE'])

        self.DBConectionString = config['DB']['CONNECTION_STRING']

        self.WebsocketModule = config['DEFAULT']['WEBSOCKET_MODULE']
        self.WebsocketConfigFile = config['DEFAULT']['WEBSOCKET_CONFIG_FILE']