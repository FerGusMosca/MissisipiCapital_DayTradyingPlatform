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
        self.HistoricalPricesPastDays = int(config['DEFAULT']['HISTORICAL_PRICES_PAST_DAYS'])

        self.PersistRecovery = config['DEFAULT']['PERSIST_RECOVERY'] == "True"
        self.PersistFullOrders = config['DEFAULT']['PERSIST_FULL_ORDERS']=="True"

        self.DBHost = config['DB']['HOST']
        self.DBPort = config['DB']['PORT']
        self.DBCatalog = config['DB']['CATALOG']
        self.DBUser = config['DB']['USER']
        self.DBPassword = config['DB']['PASSWORD']