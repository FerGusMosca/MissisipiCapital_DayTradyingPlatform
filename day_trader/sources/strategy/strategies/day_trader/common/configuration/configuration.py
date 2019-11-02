import configparser


class Configuration:
    def __init__(self, configFile):
        config = configparser.ConfigParser()
        config.read(configFile)


        self.OutgoingModule = config['DEFAULT']['OUTGOING_MODULE']
        self.OutgoingConfigFile = config['DEFAULT']['OUTGOING_CONFIG_FILE']
        self.Currency = config['DEFAULT']['CURRENCY']
        self.PauseBeforeExecutionInSeconds = config['DEFAULT']['PAUSE_BEFORE_EXECUTION_IN_SECONDS']

        self.PersistRecovery = config['DEFAULT']['PERSIST_RECOVERY'] == "True"
        self.PersistFullOrders = config['DEFAULT']['PERSIST_FULL_ORDERS']=="True"

