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



        self.ImplementStrategy = config['DEFAULT'].getboolean('IMPLEMENT_STRATEGY')
        self.HandInst = config['DEFAULT']['HANDLE_INST']
        self.MaxOrdersPerSecond = int(config['DEFAULT']['MAX_ORDERS_PER_SECOND'])
        self.InitialRecoveryTimeoutInSeconds = int(config['DEFAULT']['INITIAL_RECOVERY_TIMEOUT_IN_SECONDS'])




